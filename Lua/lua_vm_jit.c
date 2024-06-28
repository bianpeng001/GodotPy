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
    uint8 OpCode;
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
    uint32 Bx;
};
typedef struct _TInstructionABx TInstructionABx;

/* iAx, isJ */
struct _TInstructionAx
{
    struct _TInstruction Inst;
    uint32 Ax;
};
typedef struct _TInstructionAx TInstructionAx;

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

/*
** jit opcodes
*/
enum _JIT_OP_CODE
{
    JIT_START = NUM_OPCODES + 1,

    JIT_NOOP,

    JIT_OP_MAX,
};
typedef enum _JIT_OP_CODE JIT_OP_CODE;

#define NUM_JIT_OPCODES (JIT_OP_MAX)

#define RegFunc(FuncName) (TInstructFunction)&FuncName ## _Func

#include "lua_vm_op_impl.h"

static TInstructFunction const InstructionFuncTable[NUM_OPCODES + NUM_JIT_OPCODES] =
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
    RegFunc(OP_DIVK),
    RegFunc(OP_IDIVK),
    RegFunc(OP_BANDK),
    RegFunc(OP_BORK),
    RegFunc(OP_BXORK),
    RegFunc(OP_SHRI),
    RegFunc(OP_SHLI),
    RegFunc(OP_ADD),
    RegFunc(OP_SUB),
    RegFunc(OP_MUL),
    RegFunc(OP_MOD),
    RegFunc(OP_POW),
    RegFunc(OP_DIV),
    RegFunc(OP_IDIV),
    RegFunc(OP_BAND),
    RegFunc(OP_BOR),
    RegFunc(OP_BXOR),
    RegFunc(OP_SHR),
    RegFunc(OP_SHL),
    RegFunc(OP_MMBIN),
    RegFunc(OP_MMBINI),
    RegFunc(OP_MMBINK),
    RegFunc(OP_UNM),
    RegFunc(OP_BNOT),
    RegFunc(OP_NOT),

    RegFunc(OP_LEN),
    RegFunc(OP_CONCAT),
    RegFunc(OP_CLOSE),
    RegFunc(OP_TBC),
    RegFunc(OP_JMP),
    RegFunc(OP_EQ),
    RegFunc(OP_LT),
    RegFunc(OP_LE),
    RegFunc(OP_EQK),
    RegFunc(OP_EQI),
    RegFunc(OP_LTI),
    RegFunc(OP_LEI),
    RegFunc(OP_GTI),
    RegFunc(OP_GEI),
    RegFunc(OP_TEST),
    RegFunc(OP_TESTSET),
    RegFunc(OP_CALL),
    RegFunc(OP_TAILCALL),
    RegFunc(OP_RETURN),
    RegFunc(OP_RETURN0),
    RegFunc(OP_RETURN1),

    RegFunc(OP_FORLOOP),
    RegFunc(OP_FORPREP),
    RegFunc(OP_TFORPREP),
    RegFunc(OP_TFORCALL),
    RegFunc(OP_TFORLOOP),
    RegFunc(OP_SETLIST),
    RegFunc(OP_CLOSURE),
    RegFunc(OP_VARARG),
    RegFunc(OP_VARARGPREP),
    RegFunc(OP_EXTRAARG),

    NULL,

    RegFunc(JIT_NOOP),
    RegFunc(JIT_NOOP),
    RegFunc(JIT_NOOP),

    NULL,

};

static inline void TInstruction_Execute(TInstruction* pInstruct, TExecuteContext* ctx)
{
    TInstructFunction Fun = InstructionFuncTable[pInstruct->OpCode];
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




