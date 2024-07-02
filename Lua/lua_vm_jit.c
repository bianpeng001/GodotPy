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


enum EXEC_FLAG
{
    EF_NONE = 0,
    EF_END_FRAME,
    EF_GOTO_STARTFUNC,
    EF_GOTO_RETURNING,
};

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
    const Instruction *old_pc;
    int trap;

    // jit values
    int32 jit_pc;
    int32 *jit_code;
    TAllocator *allocator;

    int exec_flag;
};
typedef struct _TExecuteContext TExecuteContext;

static inline TInstruction *TExecuteContext_GetInstruction(TExecuteContext *ctx, int32 pc)
{
    lua_assert(pc >= 0);

    return (TInstruction*)TAllocator_GetMemory(ctx->allocator, ctx->jit_code[pc]);
}

typedef void (*TInstructFunction)(TExecuteContext *ctx, TInstruction* i);

/*
** jit opcodes
*/
enum JIT_OP_CODE
{
    JIT_START = NUM_OPCODES + 1,

    JIT_NOOP,

    JIT_OP_MAX,
};

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

static inline void TInstruction_Execute(TInstruction* i, TExecuteContext* ctx)
{
    TInstructFunction Fun = InstructionFuncTable[i->OpCode];
    if (Fun)
    {
        Fun(ctx, i);
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
    ctx.old_pc = ci->u.l.savedpc;
    // TODO: pc!!
    ctx.jit_pc = 0;

    if (l_unlikely(ctx.trap))
    {
        if (ctx.old_pc == ctx.cl->p->code)
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

    // reset execute flag
    ctx.exec_flag = EF_NONE;

    // gen code and execute
    // TODO:
    TAllocator *allocator = NULL;
    uint32* code = NULL;

    // run code
    for(;;)
    {
        TInstruction* i = (TInstruction*)TAllocator_GetMemory(allocator, code[ctx.jit_pc++]);
        TInstruction_Execute(i, &ctx);

        switch(ctx.exec_flag)
        {
            case EF_END_FRAME:
                return;
            case EF_GOTO_STARTFUNC:
                goto startfunc;
            case EF_GOTO_RETURNING:
                goto returning;
        }
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
    int32 padding = allocator->header % MEM_ALIGN;
    if(padding != 0)
    {
        allocator->header += MEM_ALIGN - padding;
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

/*
** compile lua bytecode to jit
*/
void lua_vm_jit_compile(lua_State *L, CallInfo *ci)
{
    const Instruction *pc;
    Proto *f;
    int i;

    f = ci_func(ci)->p;
    
    for (i = 0, pc = ci->u.l.savedpc; i < f->sizecode; ++i)
    {
        int line = luaG_getfuncline(f,i);
        const Instruction i = *pc++;
        printf("[%d] %x\n", line, GET_OPCODE(i));
    }
}

/*

#ifdef USE_JIT
#include "../lua_vm_jit.h"
void luaV_execute(lua_State *L, CallInfo *ci)
{
  lua_vm_jit_compile(L, ci);
  //lua_vm_jit_execute(L, ci);
}
void luaV_execute_old(lua_State *L, CallInfo *ci)
#else
void luaV_execute (lua_State *L, CallInfo *ci)
#endif

*/


