/*
** byte code impmement
*/

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

#define op_arithI(L,iop,fop) {  \
  StkId ra = RA(i); \
  TValue *v1 = vRB(i);  \
  int imm = GETARG_sC(i);  \
  if (ttisinteger(v1)) {  \
    lua_Integer iv1 = ivalue(v1);  \
    pc++; setivalue(s2v(ra), iop(L, iv1, imm));  \
  }  \
  else if (ttisfloat(v1)) {  \
    lua_Number nb = fltvalue(v1);  \
    lua_Number fimm = cast_num(imm);  \
    pc++; setfltvalue(s2v(ra), fop(L, nb, fimm)); \
  }}

// instruction implement
static void OP_MOVE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    StkId rb = RB();
    setobjs2s(L, ra, rb);
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
    ++ctx->pc; ++ctx->jit_pc;
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
        // TODO: 下一个指令的参数
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

static void OP_SELF_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();

    StkId ra = RA();
    const TValue *slot;
    TValue *rb = vRB();
    TValue *rc = RKC();
    TString *key = tsvalue(rc);  /* key must be a string */
    setobj2s(L, ra + 1, rb);
    if (luaV_fastget(L, rb, key, slot, luaH_getstr))
    {
        setobj2s(L, ra, slot);
    }
    else
    {
        Protect(luaV_finishget(L, rb, rc, ra, slot));
    }
}

static void OP_ADDI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();


}

static void OP_ADDK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SUBK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MULK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MODK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_POWK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_DIVK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_IDIVK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BANDK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BORK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BXORK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SHRI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SHLI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_ADD_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SUB_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MUL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MOD_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_POW_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_DIV_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_IDIV_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BAND_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BOR_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BXOR_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SHR_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SHL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MMBIN_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MMBINI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_MMBINK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_UNM_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_BNOT_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_NOT_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_LEN_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_CONCAT_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_CLOSE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TBC_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_JMP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_EQ_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_LT_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_LE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_EQK_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_EQI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_LTI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_LEI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_GTI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_GEI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TEST_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TESTSET_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_CALL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TAILCALL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_RETURN_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_RETURN0_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_RETURN1_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_FORLOOP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_FORPREP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TFORPREP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TFORCALL_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_TFORLOOP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_SETLIST_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_CLOSURE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_VARARG_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_VARARGPREP_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}

static void OP_EXTRAARG_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
    UseL();
}







