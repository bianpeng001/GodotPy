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


#ifndef INT_TYPES

typedef long long int int64;
typedef unsigned long long int uint64;
typedef int int32;
typedef unsigned int uint32;
typedef short int16;
typedef unsigned short uint16;
typedef char int8;
typedef unsigned char uint8;

#endif

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

/* iAx, isJ */
struct _TInstructionAx
{
    struct _TInstruction Inst;
    uint8 A;
    int32 Ax;
};
typedef struct _TInstructionAx TInstructionAx;

/* exec context */
struct _TExecuteContext
{
    // pass in paramter
    lua_State *L;
    CallInfo *ci;

    // local values
    LClosure *cl;
    TValue *k;
    StkId base;
    const Instruction *pc;
    int trap;

    // jit values
    size_t jit_pc;

};
typedef struct _TExecuteContext TExecuteContext;

typedef void (*TInstructFunction)(TExecuteContext *ctx, TInstruction* pInstruct);

#define RA() (ctx->base + pInstruct->A)
#define RB() (ctx->base + pInstruct->B)
#define RC() (ctx->base + pInstruct->C)

#define vRB() s2v(RB())
#define vRC() s2v(RC())

#define KB() (ctx->k+pInstruct->B)
#define KC() (ctx->k + pInstruct->C)

#define updatetrap(ci) (ctx->trap = ci->u.l.trap)

#define savepc(L) (ctx->ci->u.l.savedpc = ctx->pc)
#define savestate(L,ci) (savepc(L), L->top.p = ci->top.p)
#define Protect(exp) (savestate(ctx->L, ctx->ci), (exp), updatetrap(ctx->ci))


// instruction implement
static void OP_MOVE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    StkId ra = RA();
    StkId rb = RB();
    setobjs2s(ctx->L, ra, rb);
}

static void OP_LOADI_Func(TExecuteContext *ctx, TInstructionABx* pInstruct)
{
    StkId ra = RA();
    lua_Integer b = pInstruct->Bx;
    setivalue(s2v(ra), b);
}

static void OP_LOADF_Func(TExecuteContext *ctx, TInstructionABx* pInstruct)
{
    StkId ra = RA();
    setfltvalue(s2v(ra), cast_num(pInstruct->Bx));
}

// A from pc, Ax from pc+1
static void OP_LOADK_Func(TExecuteContext *ctx, TInstructionABx* pInstruct)
{
    StkId ra = RA();
    TValue *rb = ctx->k + pInstruct->Bx;
    setobj2s(ctx->L, ra, rb);
}

static void OP_LOADKX_Func(TExecuteContext *ctx, TInstructionAx* pInstruct)
{
    StkId ra = RA();
    TValue *rb = ctx->k + pInstruct->Ax;
    ++ctx->pc;
    setobj2s(ctx->L, ra, rb);
}

static void OP_LOADFALSE_Func(TExecuteContext *ctx, TInstructionA* pInstruct)
{
    StkId ra = RA();
    setbfvalue(s2v(ra));
}

static void OP_LFALSESKIP_Func(TExecuteContext *ctx, TInstructionA* pInstruct)
{
    StkId ra = RA();
    setbfvalue(s2v(ra));
    ++ctx->pc;
}

static void OP_LOADTRUE_Func(TExecuteContext *ctx, TInstructionA* pInstruct)
{
    StkId ra = RA();
    setbtvalue(s2v(ra));
}

static void OP_LOADNIL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    StkId ra = RA();
    int b = pInstruct->B;
    do
    {
        setnilvalue(s2v(ra++));
    } while(b--);
}

static void OP_GETUPVAL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    StkId ra = RA();
    int b = pInstruct->B;
    setobj2s(ctx->L, ra, ctx->cl->upvals[b]->v.p);
}

static void OP_SETUPVAL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    StkId ra = RA();
    UpVal *uv = ctx->cl->upvals[pInstruct->B];
    setobj(ctx->L, uv->v.p, s2v(ra));
    luaC_barrier(ctx->L, uv, s2v(ra));
}

static void OP_GETTABUP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    StkId ra = RA();
    const TValue *slot;
    TValue *upval = ctx->cl->upvals[pInstruct->B]->v.p;
    TValue *rc = KC();
    TString *key = tsvalue(rc);  /* key must be a string */
    if (luaV_fastget(L, upval, key, slot, luaH_getshortstr))
    {
        setobj2s(ctx->L, ra, slot);
    }
    else
    {
        Protect(luaV_finishget(ctx->L, upval, rc, ra, slot));
    }
}

static void OP_GETTABLE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    StkId ra = RA();
    const TValue *slot;
    TValue *rb = vRB();
    TValue *rc = vRC();
    lua_Unsigned n;
    if (ttisinteger(rc)  /* fast track for integers? */
            ? (cast_void(n = ivalue(rc)), luaV_fastgeti(ctx->L, rb, n, slot))
            : luaV_fastget(ctx->L, rb, rc, slot, luaH_get)) {
        setobj2s(ctx->L, ra, slot);
    }
    else
    {
        Protect(luaV_finishget(ctx->L, rb, rc, ra, slot));
    }
}

static void OP_GETI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
}

static void OP_GETFIELD_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
}


#define NUM_OPCODES_EX 16
#define RegFunc(FuncName) (TInstructFunction)&FuncName ## _Func

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

    NULL,
};

static inline void ExecuteOne(TExecuteContext *ctx, TInstruction* pInstruct)
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

    TInstruction* code = NULL;
    for(;;)
    {
        TInstruction* pInstruct = code + (ctx.jit_pc++);
        ExecuteOne(&ctx, pInstruct);
    }

}

/*
** Allocator
*/

TAllocator *TAllocator_Create(size_t size)
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
size_t TAllocator_Alloc(TAllocator *allocator, size_t size)
{
    if(size % MEM_ALIGN != 0)
    {
        allocator->header += MEM_ALIGN - size % MEM_ALIGN;
    }

    size_t offset = allocator->header;
    allocator->header += size;

    if (allocator->header >= allocator->size)
    {
        allocator->size *= 2;
        allocator->memory = realloc(allocator->memory, allocator->size);
    }

    return offset;
}




