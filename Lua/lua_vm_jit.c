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
    lua_Integer b = JIT_GETARG_Bx();
    setivalue(s2v(ra), b);
}

static void OP_LOADF_Func(TExecuteContext *ctx, TInstructionABx* pInstruct)
{
    StkId ra = RA();
    lua_Integer b = JIT_GETARG_Bx();
    setfltvalue(s2v(ra), cast_num(b));
}

// 这个参数来自两个指令
static void OP_LOADK_Func(TExecuteContext *ctx, TInstructionABx* pInstruct)
{
    UseL();

    StkId ra = RA();
    TValue *rb = KBx();
    setobj2s(L, ra, rb);
}

static void OP_LOADKX_Func(TExecuteContext *ctx, TInstructionABx* pInstruct)
{
    UseL();

    StkId ra = RA();
    TValue *rb = KBx();
    ++ctx->pc;
    setobj2s(L, ra, rb);
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
    UseL();

    StkId ra = RA();
    setobj2s(L, ra, ctx->cl->upvals[JIT_GETARG_B()]->v.p);
}

static void OP_SETUPVAL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    UpVal *uv = ctx->cl->upvals[JIT_GETARG_B()];
    setobj(L, uv->v.p, s2v(ra));
    luaC_barrier(L, uv, s2v(ra));
}

static void OP_GETTABUP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *upval = cl->upvals[JIT_GETARG_B()]->v.p;
    TValue *rc = KC();
    TString *key = tsvalue(rc);  /* key must be a string */
    if (luaV_fastget(L, upval, key, slot, luaH_getshortstr))
    {
        setobj2s(L, ra, slot);
    }
    else
    {
        Protect(luaV_finishget(L, upval, rc, ra, slot));
    }
}

static void OP_GETTABLE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *rb = vRB();
    TValue *rc = vRC();
    lua_Unsigned n;
    if (ttisinteger(rc)  /* fast track for integers? */
            ? (cast_void(n = ivalue(rc)), luaV_fastgeti(ctx->L, rb, n, slot))
            : luaV_fastget(L, rb, rc, slot, luaH_get))
    {
        setobj2s(L, ra, slot);
    }
    else
    {
        Protect(luaV_finishget(L, rb, rc, ra, slot));
    }
}

static void OP_GETI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *rb = vRB();
    lua_Integer c = JIT_GETARG_C();
    if (luaV_fastgeti(L, rb, c, slot))
    {
        setobj2s(L, ra, slot);
    }
    else
    {
        TValue key;
        setivalue(&key, c);
        Protect(luaV_finishget(L, rb, &key, ra, slot));
    }
}

static void OP_GETFIELD_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *rb = vRB();
    TValue *rc = KC();
    TString *key = tsvalue(rc);  /* key must be a string */
    if (luaV_fastget(L, rb, key, slot, luaH_getshortstr))
    {
        setobj2s(L, ra, slot);
    }
    else
    {
        Protect(luaV_finishget(L, rb, rc, ra, slot));
    }
}

static void OP_SETTABUP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    const TValue *slot;
    TValue *upval = cl->upvals[pInstruct->A]->v.p;
    TValue *rb = KB();
    TValue *rc = RKC();
    TString *key = tsvalue(rb);  /* key must be a string */
    if (luaV_fastget(L, upval, key, slot, luaH_getshortstr))
    {
        luaV_finishfastset(L, upval, slot, rc);
    }
    else
    {
        Protect(luaV_finishset(L, upval, rb, rc, slot));
    }
}

static void OP_SETTABLE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *rb = vRB();  /* key (table is in 'ra') */
    TValue *rc = RKC();  /* value */
    lua_Unsigned n;
    if (ttisinteger(rb)  /* fast track for integers? */
            ? (cast_void(n = ivalue(rb)), luaV_fastgeti(L, s2v(ra), n, slot))
            : luaV_fastget(L, s2v(ra), rb, slot, luaH_get))
    {
        luaV_finishfastset(L, s2v(ra), slot, rc);
    }
    else
    {
        Protect(luaV_finishset(L, s2v(ra), rb, rc, slot));
    }
}

static void OP_SETI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    int c = JIT_GETARG_B();
    TValue *rc = RKC();
    if (luaV_fastgeti(L, s2v(ra), c, slot))
    {
        luaV_finishfastset(L, s2v(ra), slot, rc);
    }
    else
    {
        TValue key;
        setivalue(&key, c);
        Protect(luaV_finishset(L, s2v(ra), &key, rc, slot));
    }
}

static void OP_SETFIELD_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *rb = KB();
    TValue *rc = RKC();
    TString *key = tsvalue(rb);  /* key must be a string */
    if (luaV_fastget(L, s2v(ra), key, slot, luaH_getshortstr))
    {
        luaV_finishfastset(L, s2v(ra), slot, rc);
    }
    else
    {
        Protect(luaV_finishset(L, s2v(ra), rb, rc, slot));
    }
}

static void OP_NEWTABLE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    int b = JIT_GETARG_B();  /* log2(hash size) + 1 */
    int c = JIT_GETARG_C();  /* array size */
    Table *t;
    if (b > 0)
    {
        b = 1 << (b - 1);  /* size is 2^(b - 1) */
    }
    if (JIT_GETARG_k())  /* non-zero extra argument? */
    {
        c += ((TInstructionABx *)JIT_GET_INST(ctx->jit_pc))->Bx * (MAXARG_C + 1);
    }
    ctx->jit_pc++;  /* skip extra argument */
    L->top.p = ra + 1;  /* correct top in case of emergency GC */
    t = luaH_new(L);  /* memory allocation */
    sethvalue2s(L, ra, t);
    if (b != 0 || c != 0)
    {
        luaH_resize(L, t, c, b);  /* idem */
    }
    checkGC(L, ra + 1);
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




