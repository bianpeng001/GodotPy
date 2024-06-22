/*
** bianpeng 2024-6-21
** begin to implement a simple jit, use c cross platform in c language, for a test
** without any asm jit framework
*/

#include "lprefix.h"

#include "lua.h"

#include "ldebug.h"
#include "lfunc.h"
#include "lgc.h"
#include "lobject.h"
#include "lopcodes.h"
#include "lstate.h"
#include "lstring.h"
#include "ltable.h"
#include "ltm.h"

#include "lua_vm_jit.h"

typedef struct _TInstruction
{
    unsigned char FuncID;
} TInstruction;

/* iABC */
typedef struct _TInstructionABC
{
    struct _TInstruction Inst;
    char A, B, C;
} TInstructionABC;

/* iABx, iAsBx */
typedef struct _TInstructionABx
{
    struct _TInstruction Inst;
    char A;
    int Bx;
} TInstructionABx;

/* iAx, isJ */
typedef struct _TInstructionAx
{
    struct _TInstruction Inst;
    int Ax;
} TInstructionAx;

/* exec context */
typedef struct _TExecContext
{
    // pass in paramter
    lua_State *L;
    CallInfo *ci;

    // local values
    LClosure *cl;
    TValue *k;
    StkId base;
    Instruction *pc;
    int trap;

} TExecContext;

typedef void (*TInstructFuntion)(TExecContext *ctx, TInstruction* pInstruct);

static void Add(TExecContext *ctx, TInstructionABC* pInstruct)
{
}


static TInstructFuntion InstructionFuncTable[] = 
{
    (TInstructFuntion)&Add,
    (TInstructFuntion)&Add,
    (TInstructFuntion)&Add,
    (TInstructFuntion)&Add,
    (TInstructFuntion)&Add,
    NULL,
};

static inline void ExecuteOne(TExecContext *ctx, TInstruction* pInstruct)
{
    TInstructFuntion Fun = InstructionFuncTable[pInstruct->FuncID];
    if (Fun)
    {
        Fun(ctx, pInstruct);
    }

}

static void Execute(TExecContext *ctx, TInstruction *pInstruct, int start, int stop)
{
    for(int i = start; i < stop; ++i)
    {
        ExecuteOne(ctx, pInstruct + i);
    }
}

void lua_vm_jit_execute(lua_State *L, CallInfo *ci)
{
    TExecContext ctx;
    ctx.L = L;
    ctx.ci = ci;

    TInstruction *code = NULL;

    Execute(&ctx, code, 0, 0);
}


