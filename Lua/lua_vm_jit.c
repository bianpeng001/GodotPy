/*
** bianpeng 2024-6-21
** begin to implement a simple jit, use c cross platform in c language, for a test
** without any asm jit framework
*/

#define lvm_c
#define LUA_CORE

#include "lprefix.h"

#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "lua.h"

#include "ldebug.h"
#include "ldo.h"
#include "lfunc.h"
#include "lgc.h"
#include "lobject.h"
#include "lopcodes.h"
#include "lstate.h"
#include "lstring.h"
#include "ltable.h"
#include "ltm.h"
#include "lvm.h"

#include "lua_vm_jit.h"


/* instruction head */
struct _TInstruction
{
    uint8 FuncID;
};
typedef struct _TInstruction TInstruction;

/* iABC */
struct _TInstructionABC
{
    struct _TInstruction Inst;
    uint8 A, k, B, C;
};
typedef struct _TInstructionABC TInstructionABC;

/* iA */
struct _TInstructionA
{
    struct _TInstruction Inst;
    uint8 A;
};
typedef struct _TInstructionA TInstructionA;

/* iABx, iAsBx */
struct _TInstructionABx
{
    struct _TInstruction Inst;
    uint8 A;
    int32 Bx;
};
typedef struct _TInstructionABx TInstructionABx;

/* exec context */
struct _TExecuteContext
{
    // pass in parameters
    lua_State *L;
    CallInfo *ci;

    // local values
    LClosure *cl;
    TValue *k;
    StkId base;
    const Instruction *pc;
    int trap;

    // jit values
    uint32 jit_pc;
    uint32 *jit_code;
    TAllocator *allocator;
};
typedef struct _TExecuteContext TExecuteContext;

static inline TInstruction *TExecuteContext_GetInstruction(TExecuteContext *ctx, uint32 pc)
{
    return (TInstruction*)TAllocator_GetMemory(ctx->allocator, ctx->jit_code[pc]);
}

typedef void (*TInstructFunction)(TExecuteContext *ctx, TInstruction* pInstruct);


#define UseL() \
lua_State *L = ctx->L;\
CallInfo *ci = ctx->ci;\
LClosure *cl = ctx->cl;\
(void)L;(void)ci;(void)cl;(void)ctx;(void)pInstruct;

#define JIT_GETARG_A() (pInstruct->A)
#define JIT_GETARG_B() (pInstruct->B)
#define JIT_GETARG_C() (pInstruct->C)
#define JIT_GETARG_k() (pInstruct->k)
#define JIT_GETARG_Bx() (pInstruct->Bx)

#define RA() (ctx->base + JIT_GETARG_A())
#define RB() (ctx->base + JIT_GETARG_B())
#define RC() (ctx->base + JIT_GETARG_C())

#define vRB() s2v(RB())
#define vRC() s2v(RC())

#define KB() (ctx->k + JIT_GETARG_B())
#define KC() (ctx->k + JIT_GETARG_C())
#define KBx() (ctx->k + JIT_GETARG_Bx())

#define RKC() (JIT_GETARG_k() ? ctx->k + JIT_GETARG_C() : s2v(ctx->base + JIT_GETARG_C()))

#define updatetrap(ci) (ctx->trap = ci->u.l.trap)

#define savepc(L) (ctx->ci->u.l.savedpc = ctx->pc)
#define savestate(L,ci) (savepc(L), L->top.p = ci->top.p)

#define Protect(exp) (savestate(ctx->L, ctx->ci), (exp), updatetrap(ctx->ci))

#define ProtectNT(exp)  (savepc(L), (exp), updatetrap(ci))

#define checkGC(L,c)  \
	{ luaC_condGC(L, (savepc(L), L->top.p = (c)), updatetrap(ci)); \
           luai_threadyield(L); }

#define JIT_GET_INST(pc) TExecuteContext_GetInstruction(ctx, (pc))


#define NUM_OPCODES_EX 16
#define RegFunc(FuncName) (TInstructFunction)&FuncName ## _Func

#include "lua_vm_op_impl.h"

static TInstructFunction const InstructionFuncTable[NUM_OPCODES + NUM_OPCODES_EX] = 
{
    RegFunc(OP_MOVE),
    RegFunc(OP_LOADI),
    RegFunc(OP_LOADF),
    RegFunc(OP_LOADK),
    RegFunc(OP_LOADKX),
    RegFunc(OP_LOADFALSE),
    RegFunc(OP_LFALSESKIP),
    RegFunc(OP_LOADTRUE),
    RegFunc(OP_LOADNIL),

    RegFunc(OP_GETUPVAL),
    RegFunc(OP_SETUPVAL),
    RegFunc(OP_GETTABUP),
    RegFunc(OP_GETTABLE),
    RegFunc(OP_GETI),
    RegFunc(OP_GETFIELD),
    RegFunc(OP_SETTABUP),
    RegFunc(OP_SETTABLE),
    RegFunc(OP_SETI),
    RegFunc(OP_SETFIELD),
    RegFunc(OP_NEWTABLE),
    RegFunc(OP_SELF),

    RegFunc(OP_ADDI),
    RegFunc(OP_ADDK),
    RegFunc(OP_SUBK),
    RegFunc(OP_MULK),
    RegFunc(OP_MODK),
    RegFunc(OP_POWK),

    NULL,
};

static inline void TInstruction_Execute(TInstruction* pInstruct, TExecuteContext* ctx)
{
    TInstructFunction Fun = InstructionFuncTable[pInstruct->FuncID];
    if (Fun)
    {
        Fun(ctx, pInstruct);
    }
}

void lua_vm_jit_execute(lua_State *L, CallInfo *ci)
{
    TExecuteContext ctx;
    ctx.L = L;
    ctx.ci = ci;

startfunc:
    ctx.trap = L->hookmask;
returning:
    ctx.cl = clLvalue(s2v(ci->func.p));
    ctx.k = ctx.cl->p->k;
    ctx.pc = ci->u.l.savedpc;

    if (l_unlikely(ctx.trap))
    {
        if (ctx.pc == ctx.cl->p->code)
        {
            if (ctx.cl->p->is_vararg)
            {
                ctx.trap = 0;
            }
            else
            {
                luaD_hookcall(L, ci);
            }
        }
        ci->u.l.trap = 1;
    }
    ctx.base = ci->func.p + 1;

    // gen code
    TAllocator *allocator = NULL;
    uint32* code = NULL;

    // run code
    for(;;)
    {
        TInstruction* pInstruct = (TInstruction*)TAllocator_GetMemory(allocator, code[ctx.jit_pc++]);
        TInstruction_Execute(pInstruct, &ctx);
    }

}

/*
** Allocator
*/

TAllocator *TAllocator_Create(uint32 size)
{
    TAllocator * allocator = (TAllocator *)malloc(sizeof(TAllocator));
    memset(allocator, 0, sizeof(TAllocator));

    allocator->memory = (void *)malloc(size);
    allocator->size = size;
    allocator->header = 0;

    return allocator;
}

void TAllocator_Destroy(TAllocator *allocator)
{
    free(allocator->memory);
    free(allocator);
}

#define MEM_ALIGN 4
uint32 TAllocator_Alloc(TAllocator *allocator, uint32 size)
{
    if(size % MEM_ALIGN != 0)
    {
        allocator->header += MEM_ALIGN - size % MEM_ALIGN;
    }

    uint32 offset = allocator->header;
    allocator->header += size;

    if (allocator->header >= allocator->size)
    {
        allocator->size *= 2;
        allocator->memory = realloc(allocator->memory, allocator->size);
    }

    return offset;
}




