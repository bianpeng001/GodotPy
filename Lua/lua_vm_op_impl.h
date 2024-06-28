/*
** bianpeng 2024-6-28
** byte code instructions impmement
*/

/* limit for table tag-method chains (to avoid infinite loops) */
#define MAXTAGLOOP	2000

/*
** 'l_intfitsf' checks whether a given integer is in the range that
** can be converted to a float without rounding. Used in comparisons.
*/

/* number of bits in the mantissa of a float */
#define NBM		(l_floatatt(MANT_DIG))

/*
** Check whether some integers may not fit in a float, testing whether
** (maxinteger >> NBM) > 0. (That implies (1 << NBM) <= maxinteger.)
** (The shifts are done in parts, to avoid shifting by more than the size
** of an integer. In a worst case, NBM == 113 for long double and
** sizeof(long) == 32.)
*/
#if ((((LUA_MAXINTEGER >> (NBM / 4)) >> (NBM / 4)) >> (NBM / 4)) \
	>> (NBM - (3 * (NBM / 4))))  >  0

/* limit for integers that fit in a float */
#define MAXINTFITSF	((lua_Unsigned)1 << NBM)

/* check whether 'i' is in the interval [-MAXINTFITSF, MAXINTFITSF] */
#define l_intfitsf(i)	((MAXINTFITSF + l_castS2U(i)) <= (2 * MAXINTFITSF))

#else  /* all integers fit in a float precisely */

#define l_intfitsf(i)	1

#endif

//---------------------------------------------------------------------------------

#define UseL() \
lua_State *L = ctx->L;\
CallInfo *ci = ctx->ci;\
LClosure *cl = ctx->cl;\
(void)L;(void)ci;(void)cl;(void)ctx;(void)i;

#define JIT_GETARG_A(i) (i->A)
#define JIT_GETARG_Ax(i) (i->Ax)
#define JIT_GETARG_sJ(i) sC2int(JIT_GETARG_Ax(i))

#define JIT_GETARG_B(i) (i->B)
#define JIT_GETARG_sB(i) sC2int(JIT_GETARG_B(i))

#define JIT_GETARG_C(i) (i->C)
#define JIT_GETARG_sC(i) sC2int(JIT_GETARG_C(i))

#define JIT_GETARG_k(i) (i->k)
#define JIT_TESTARG_k(i) JIT_GETARG_k(i)

#define JIT_GETARG_Bx(i) (i->Bx)
#define JIT_GETARG_sBX(i) sC2int(JIT_GETARG_Bx(i))

#define RA(i) (ctx->base + JIT_GETARG_A(i))
#define RB(i) (ctx->base + JIT_GETARG_B(i))
#define RC(i) (ctx->base + JIT_GETARG_C(i))

#define JIT_GET_OPCODE(i) (((TInstruction *)i)->OpCode)

#define vRB(i) s2v(RB(i))
#define vRC(i) s2v(RC(i))

#define KB(i) (ctx->k + JIT_GETARG_B(i))
#define KC(i) (ctx->k + JIT_GETARG_C(i))
#define KBx(i) (ctx->k + JIT_GETARG_Bx(i))

#define RKC(i) (JIT_GETARG_k(i) ? ctx->k + JIT_GETARG_C(i) : s2v(ctx->base + JIT_GETARG_C(i)))

#define updatetrap(ci) (ctx->trap = ci->u.l.trap)
#define updatebase(ci) (ctx->base = ci->func.p + 1)
#define updatestack(ci) { if (l_unlikely(ctx->trap)) { updatebase(ci); ra = RA(i); } }

#define dojump(ci,pi,e) { ctx->jit_pc += JIT_GETARG_sJ(pi) + e; updatetrap(ci); }

#define donextjump(ci) { \
TInstructionAx *ni = (TInstructionAx *)JIT_GET_INST(ctx->jit_pc); \
dojump(ci, ni, 1); }

#define docondjump() if (cond != JIT_GETARG_k(i)) ctx->jit_pc++; else donextjump(ci);

#define savepc(L) (ctx->ci->u.l.savedpc = ctx->old_pc)

#define savestate(L,ci) (savepc(L), L->top.p = ci->top.p)

#define Protect(exp) (savestate(ctx->L, ctx->ci), (exp), updatetrap(ctx->ci))

#define ProtectNT(exp)  (savepc(L), (exp), updatetrap(ci))

#define halfProtect(exp)  (savestate(L,ci), (exp))

#define checkGC(L,c) { \
    luaC_condGC(L, (savepc(L), L->top.p = (c)), updatetrap(ci)); \
    luai_threadyield(L); }

#define JIT_GET_INST(pc) TExecuteContext_GetInstruction(ctx, (pc))


#define JIT_UNUSE(X) (void)X

#define goto_ret() { \
    if (ci->callstatus & CIST_FRESH) { \
        ctx->exec_flag = EF_END_FRAME; } \
    else { \
        ci = ci->previous; \
        ctx->exec_flag = EF_GOTO_RETURNING; } \
}


/*
** Compare two strings 'ls' x 'rs', returning an integer less-equal-
** -greater than zero if 'ls' is less-equal-greater than 'rs'.
** The code is a little tricky because it allows '\0' in the strings
** and it uses 'strcoll' (to respect locales) for each segments
** of the strings.
*/
static int l_strcmp (const TString *ls, const TString *rs) {
  const char *l = getstr(ls);
  size_t ll = tsslen(ls);
  const char *r = getstr(rs);
  size_t lr = tsslen(rs);
  for (;;) {  /* for each segment */
    int temp = strcoll(l, r);
    if (temp != 0)  /* not equal? */
      return temp;  /* done */
    else {  /* strings are equal up to a '\0' */
      size_t len = strlen(l);  /* index of first '\0' in both strings */
      if (len == lr)  /* 'rs' is finished? */
        return (len == ll) ? 0 : 1;  /* check 'ls' */
      else if (len == ll)  /* 'ls' is finished? */
        return -1;  /* 'ls' is less than 'rs' ('rs' is not finished) */
      /* both strings longer than 'len'; go on comparing after the '\0' */
      len++;
      l += len; ll -= len; r += len; lr -= len;
    }
  }
}

/*
** Check whether integer 'i' is less than float 'f'. If 'i' has an
** exact representation as a float ('l_intfitsf'), compare numbers as
** floats. Otherwise, use the equivalence 'i < f <=> i < ceil(f)'.
** If 'ceil(f)' is out of integer range, either 'f' is greater than
** all integers or less than all integers.
** (The test with 'l_intfitsf' is only for performance; the else
** case is correct for all values, but it is slow due to the conversion
** from float to int.)
** When 'f' is NaN, comparisons must result in false.
*/
l_sinline int LTintfloat (lua_Integer i, lua_Number f) {
  if (l_intfitsf(i))
    return luai_numlt(cast_num(i), f);  /* compare them as floats */
  else {  /* i < f <=> i < ceil(f) */
    lua_Integer fi;
    if (luaV_flttointeger(f, &fi, F2Iceil))  /* fi = ceil(f) */
      return i < fi;   /* compare them as integers */
    else  /* 'f' is either greater or less than all integers */
      return f > 0;  /* greater? */
  }
}

/*
** Check whether integer 'i' is less than or equal to float 'f'.
** See comments on previous function.
*/
l_sinline int LEintfloat (lua_Integer i, lua_Number f) {
  if (l_intfitsf(i))
    return luai_numle(cast_num(i), f);  /* compare them as floats */
  else {  /* i <= f <=> i <= floor(f) */
    lua_Integer fi;
    if (luaV_flttointeger(f, &fi, F2Ifloor))  /* fi = floor(f) */
      return i <= fi;   /* compare them as integers */
    else  /* 'f' is either greater or less than all integers */
      return f > 0;  /* greater? */
  }
}

/*
** Check whether float 'f' is less than integer 'i'.
** See comments on previous function.
*/
l_sinline int LTfloatint (lua_Number f, lua_Integer i) {
  if (l_intfitsf(i))
    return luai_numlt(f, cast_num(i));  /* compare them as floats */
  else {  /* f < i <=> floor(f) < i */
    lua_Integer fi;
    if (luaV_flttointeger(f, &fi, F2Ifloor))  /* fi = floor(f) */
      return fi < i;   /* compare them as integers */
    else  /* 'f' is either greater or less than all integers */
      return f < 0;  /* less? */
  }
}

/*
** Check whether float 'f' is less than or equal to integer 'i'.
** See comments on previous function.
*/
l_sinline int LEfloatint (lua_Number f, lua_Integer i) {
  if (l_intfitsf(i))
    return luai_numle(f, cast_num(i));  /* compare them as floats */
  else {  /* f <= i <=> ceil(f) <= i */
    lua_Integer fi;
    if (luaV_flttointeger(f, &fi, F2Iceil))  /* fi = ceil(f) */
      return fi <= i;   /* compare them as integers */
    else  /* 'f' is either greater or less than all integers */
      return f < 0;  /* less? */
  }
}

/*
** Return 'l < r', for numbers.
*/
l_sinline int LTnum (const TValue *l, const TValue *r) {
  lua_assert(ttisnumber(l) && ttisnumber(r));
  if (ttisinteger(l)) {
    lua_Integer li = ivalue(l);
    if (ttisinteger(r))
      return li < ivalue(r);  /* both are integers */
    else  /* 'l' is int and 'r' is float */
      return LTintfloat(li, fltvalue(r));  /* l < r ? */
  }
  else {
    lua_Number lf = fltvalue(l);  /* 'l' must be float */
    if (ttisfloat(r))
      return luai_numlt(lf, fltvalue(r));  /* both are float */
    else  /* 'l' is float and 'r' is int */
      return LTfloatint(lf, ivalue(r));
  }
}

/*
** Return 'l <= r', for numbers.
*/
l_sinline int LEnum (const TValue *l, const TValue *r) {
  lua_assert(ttisnumber(l) && ttisnumber(r));
  if (ttisinteger(l)) {
    lua_Integer li = ivalue(l);
    if (ttisinteger(r))
      return li <= ivalue(r);  /* both are integers */
    else  /* 'l' is int and 'r' is float */
      return LEintfloat(li, fltvalue(r));  /* l <= r ? */
  }
  else {
    lua_Number lf = fltvalue(l);  /* 'l' must be float */
    if (ttisfloat(r))
      return luai_numle(lf, fltvalue(r));  /* both are float */
    else  /* 'l' is float and 'r' is int */
      return LEfloatint(lf, ivalue(r));
  }
}

/*
** return 'l < r' for non-numbers.
*/
static int lessthanothers (lua_State *L, const TValue *l, const TValue *r) {
  lua_assert(!ttisnumber(l) || !ttisnumber(r));
  if (ttisstring(l) && ttisstring(r))  /* both are strings? */
    return l_strcmp(tsvalue(l), tsvalue(r)) < 0;
  else
    return luaT_callorderTM(L, l, r, TM_LT);
}

/*
** return 'l <= r' for non-numbers.
*/
static int lessequalothers (lua_State *L, const TValue *l, const TValue *r) {
  lua_assert(!ttisnumber(l) || !ttisnumber(r));
  if (ttisstring(l) && ttisstring(r))  /* both are strings? */
    return l_strcmp(tsvalue(l), tsvalue(r)) <= 0;
  else
    return luaT_callorderTM(L, l, r, TM_LE);
}

extern int luaV_lessthan(lua_State *L, const TValue *l, const TValue *r);
extern int luaV_lessequal(lua_State *L, const TValue *l, const TValue *r);
extern int luaV_equalobj(lua_State *L, const TValue *t1, const TValue *t2);


/*
** Try to convert a 'for' limit to an integer, preserving the semantics
** of the loop. Return true if the loop must not run; otherwise, '*p'
** gets the integer limit.
** (The following explanation assumes a positive step; it is valid for
** negative steps mutatis mutandis.)
** If the limit is an integer or can be converted to an integer,
** rounding down, that is the limit.
** Otherwise, check whether the limit can be converted to a float. If
** the float is too large, clip it to LUA_MAXINTEGER.  If the float
** is too negative, the loop should not run, because any initial
** integer value is greater than such limit; so, the function returns
** true to signal that. (For this latter case, no integer limit would be
** correct; even a limit of LUA_MININTEGER would run the loop once for
** an initial value equal to LUA_MININTEGER.)
*/
static int forlimit (lua_State *L, lua_Integer init, const TValue *lim,
                                   lua_Integer *p, lua_Integer step) {
  if (!luaV_tointeger(lim, p, (step < 0 ? F2Iceil : F2Ifloor))) {
    /* not coercible to in integer */
    lua_Number flim;  /* try to convert to float */
    if (!tonumber(lim, &flim)) /* cannot convert to float? */
      luaG_forerror(L, lim, "limit");
    /* else 'flim' is a float out of integer bounds */
    if (luai_numlt(0, flim)) {  /* if it is positive, it is too large */
      if (step < 0) return 1;  /* initial value must be less than it */
      *p = LUA_MAXINTEGER;  /* truncate */
    }
    else {  /* it is less than min integer */
      if (step > 0) return 1;  /* initial value must be greater than it */
      *p = LUA_MININTEGER;  /* truncate */
    }
  }
  return (step > 0 ? init > *p : init < *p);  /* not to run? */
}


/*
** Prepare a numerical for loop (opcode OP_FORPREP).
** Return true to skip the loop. Otherwise,
** after preparation, stack will be as follows:
**   ra : internal index (safe copy of the control variable)
**   ra + 1 : loop counter (integer loops) or limit (float loops)
**   ra + 2 : step
**   ra + 3 : control variable
*/
static int forprep (lua_State *L, StkId ra) {
  TValue *pinit = s2v(ra);
  TValue *plimit = s2v(ra + 1);
  TValue *pstep = s2v(ra + 2);
  if (ttisinteger(pinit) && ttisinteger(pstep)) { /* integer loop? */
    lua_Integer init = ivalue(pinit);
    lua_Integer step = ivalue(pstep);
    lua_Integer limit;
    if (step == 0)
      luaG_runerror(L, "'for' step is zero");
    setivalue(s2v(ra + 3), init);  /* control variable */
    if (forlimit(L, init, plimit, &limit, step))
      return 1;  /* skip the loop */
    else {  /* prepare loop counter */
      lua_Unsigned count;
      if (step > 0) {  /* ascending loop? */
        count = l_castS2U(limit) - l_castS2U(init);
        if (step != 1)  /* avoid division in the too common case */
          count /= l_castS2U(step);
      }
      else {  /* step < 0; descending loop */
        count = l_castS2U(init) - l_castS2U(limit);
        /* 'step+1' avoids negating 'mininteger' */
        count /= l_castS2U(-(step + 1)) + 1u;
      }
      /* store the counter in place of the limit (which won't be
         needed anymore) */
      setivalue(plimit, l_castU2S(count));
    }
  }
  else {  /* try making all values floats */
    lua_Number init; lua_Number limit; lua_Number step;
    if (l_unlikely(!tonumber(plimit, &limit)))
      luaG_forerror(L, plimit, "limit");
    if (l_unlikely(!tonumber(pstep, &step)))
      luaG_forerror(L, pstep, "step");
    if (l_unlikely(!tonumber(pinit, &init)))
      luaG_forerror(L, pinit, "initial value");
    if (step == 0)
      luaG_runerror(L, "'for' step is zero");
    if (luai_numlt(0, step) ? luai_numlt(limit, init)
                            : luai_numlt(init, limit))
      return 1;  /* skip the loop */
    else {
      /* make sure internal values are all floats */
      setfltvalue(plimit, limit);
      setfltvalue(pstep, step);
      setfltvalue(s2v(ra), init);  /* internal index */
      setfltvalue(s2v(ra + 3), init);  /* control variable */
    }
  }
  return 0;
}


/*
** Execute a step of a float numerical for loop, returning
** true iff the loop must continue. (The integer case is
** written online with opcode OP_FORLOOP, for performance.)
*/
static int floatforloop (StkId ra) {
  lua_Number step = fltvalue(s2v(ra + 2));
  lua_Number limit = fltvalue(s2v(ra + 1));
  lua_Number idx = fltvalue(s2v(ra));  /* internal index */
  idx = luai_numadd(L, idx, step);  /* increment index */
  if (luai_numlt(0, step) ? luai_numle(idx, limit)
                          : luai_numle(limit, idx)) {
    chgfltvalue(s2v(ra), idx);  /* update internal index */
    setfltvalue(s2v(ra + 3), idx);  /* and control variable */
    return 1;  /* jump back */
  }
  else
    return 0;  /* finish the loop */
}

/*
** create a new Lua closure, push it in the stack, and initialize
** its upvalues.
*/
static void pushclosure (lua_State *L, Proto *p, UpVal **encup, StkId base,
                         StkId ra) {
  int nup = p->sizeupvalues;
  Upvaldesc *uv = p->upvalues;
  int i;
  LClosure *ncl = luaF_newLclosure(L, nup);
  ncl->p = p;
  setclLvalue2s(L, ra, ncl);  /* anchor new closure in stack */
  for (i = 0; i < nup; i++) {  /* fill in its upvalues */
    if (uv[i].instack)  /* upvalue refers to local variable? */
      ncl->upvals[i] = luaF_findupval(L, base + uv[i].idx);
    else  /* get upvalue from enclosing function */
      ncl->upvals[i] = encup[uv[i].idx];
    luaC_objbarrier(L, ncl, ncl->upvals[i]);
  }
}



//---------------------------------------------------------------------------------

static void OP_MOVE_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    StkId rb = RB(i);
    setobjs2s(L, ra, rb);
}

static void OP_LOADI_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    StkId ra = RA(i);
    lua_Integer b = JIT_GETARG_Bx(i);
    setivalue(s2v(ra), b);
}

static void OP_LOADF_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    StkId ra = RA(i);
    lua_Integer b = JIT_GETARG_Bx(i);
    setfltvalue(s2v(ra), cast_num(b));
}

// 这个参数来自两个指令
static void OP_LOADK_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = KBx(i);
    setobj2s(L, ra, rb);
}

static void OP_LOADKX_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = KBx(i);
    ctx->jit_pc++;
    setobj2s(L, ra, rb);
}

static void OP_LOADFALSE_Func(TExecuteContext *ctx, TInstructionA* i)
{
    StkId ra = RA(i);
    setbfvalue(s2v(ra));
}

static void OP_LFALSESKIP_Func(TExecuteContext *ctx, TInstructionA* i)
{
    StkId ra = RA(i);
    setbfvalue(s2v(ra));
    ctx->jit_pc++;
}

static void OP_LOADTRUE_Func(TExecuteContext *ctx, TInstructionA* i)
{
    StkId ra = RA(i);
    setbtvalue(s2v(ra));
}

static void OP_LOADNIL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    StkId ra = RA(i);
    int b = i->B;
    do
    {
        setnilvalue(s2v(ra++));
    } while(b--);
}

static void OP_GETUPVAL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    setobj2s(L, ra, ctx->cl->upvals[JIT_GETARG_B(i)]->v.p);
}

static void OP_SETUPVAL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    UpVal *uv = ctx->cl->upvals[JIT_GETARG_B(i)];
    setobj(L, uv->v.p, s2v(ra));
    luaC_barrier(L, uv, s2v(ra));
}

static void OP_GETTABUP_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *upval = cl->upvals[JIT_GETARG_B(i)]->v.p;
    TValue *rc = KC(i);
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

static void OP_GETTABLE_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *rb = vRB(i);
    TValue *rc = vRC(i);
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

static void OP_GETI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *rb = vRB(i);
    lua_Integer c = JIT_GETARG_C(i);
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

static void OP_GETFIELD_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *rb = vRB(i);
    TValue *rc = KC(i);
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

static void OP_SETTABUP_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    const TValue *slot;
    TValue *upval = cl->upvals[JIT_GETARG_A(i)]->v.p;
    TValue *rb = KB(i);
    TValue *rc = RKC(i);
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

static void OP_SETTABLE_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *rb = vRB(i);  /* key (table is in 'ra') */
    TValue *rc = RKC(i);  /* value */
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

static void OP_SETI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    int c = JIT_GETARG_B(i);
    TValue *rc = RKC(i);
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

static void OP_SETFIELD_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *rb = KB(i);
    TValue *rc = RKC(i);
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

static void OP_NEWTABLE_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int b = JIT_GETARG_B(i);  /* log2(hash size) + 1 */
    int c = JIT_GETARG_C(i);  /* array size */
    Table *t;
    if (b > 0)
    {
        b = 1 << (b - 1);  /* size is 2^(b - 1) */
    }
    if (JIT_GETARG_k(i))  /* non-zero extra argument? */
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

static void OP_SELF_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    const TValue *slot;
    TValue *rb = vRB(i);
    TValue *rc = RKC(i);
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

// pc++, 如果是int，float，则跳过下一个处理符号重载的MMBINI
#define op_arithI(L,iop,fop) { \
    StkId ra = RA(i); \
    TValue *v1 = vRB(i); \
    int imm = JIT_GETARG_sC(i); \
    if (ttisinteger(v1)) { \
        lua_Integer iv1 = ivalue(v1); \
        ctx->jit_pc++; \
        setivalue(s2v(ra), iop(L, iv1, imm)); } \
    else if (ttisfloat(v1)) { \
        lua_Number fv1 = fltvalue(v1); \
        lua_Number fimm = cast_num(imm); \
        ctx->jit_pc++; \
        setfltvalue(s2v(ra), fop(L, fv1, fimm)); } \
}

#define op_arith_aux(L,v1,v2,iop,fop) { \
    StkId ra = RA(i); \
    if (ttisinteger(v1) && ttisinteger(v2)) { \
        lua_Integer i1 = ivalue(v1); lua_Integer i2 = ivalue(v2); \
        ctx->jit_pc++; \
        setivalue(s2v(ra), iop(L, i1, i2)); } \
    else { op_arithf_aux(L, v1, v2, fop); } \
}

#define op_arithf_aux(L,v1,v2,fop) { \
    lua_Number n1; lua_Number n2; \
    if (tonumberns(v1, n1) && tonumberns(v2, n2)) { \
        ctx->jit_pc++; \
        setfltvalue(s2v(ra), fop(L, n1, n2)); } \
}

#define op_arithf_aux(L,v1,v2,fop) { \
    lua_Number n1; lua_Number n2; \
    if (tonumberns(v1, n1) && tonumberns(v2, n2)) { \
        ctx->jit_pc++; \
        setfltvalue(s2v(ra), fop(L, n1, n2)); } \
}

#define op_arithf(L,fop) { \
    StkId ra = RA(i); \
    TValue *v1 = vRB(i); \
    TValue *v2 = vRC(i); \
    op_arithf_aux(L, v1, v2, fop); \
}

#define op_arith(L,iop,fop) { \
    TValue *v1 = vRB(i); \
    TValue *v2 = vRC(i); \
    op_arith_aux(L, v1, v2, iop, fop); \
}

#define op_arithK(L,iop,fop) { \
    TValue *v1 = vRB(i); \
    TValue *v2 = KC(i); lua_assert(ttisnumber(v2)); \
    op_arith_aux(L, v1, v2, iop, fop); \
}

#define op_arithfK(L,fop) { \
    StkId ra = RA(i); \
    TValue *v1 = vRB(i); \
    TValue *v2 = KC(i); lua_assert(ttisnumber(v2)); \
    op_arithf_aux(L, v1, v2, fop); \
}

#define op_bitwiseK(L,op) { \
    StkId ra = RA(i); \
    TValue *v1 = vRB(i); \
    TValue *v2 = KC(i);  \
    lua_Integer i1; \
    lua_Integer i2 = ivalue(v2); \
    if (tointegerns(v1, &i1)) { \
        ctx->jit_pc++; \
        setivalue(s2v(ra), op(i1, i2)); } \
}

#define op_bitwise(L,op) { \
    StkId ra = RA(i); \
    TValue *v1 = vRB(i); \
    TValue *v2 = vRC(i); \
    lua_Integer i1; lua_Integer i2; \
    if (tointegerns(v1, &i1) && tointegerns(v2, &i2)) { \
        ctx->jit_pc++; \
        setivalue(s2v(ra), op(i1, i2)); } \
}

#define op_order(L,opi,opn,other) { \
    StkId ra = RA(i); \
    int cond; \
    TValue *rb = vRB(i); \
    if (ttisinteger(s2v(ra)) && ttisinteger(rb)) { \
        lua_Integer ia = ivalue(s2v(ra)); \
        lua_Integer ib = ivalue(rb); \
        cond = opi(ia, ib); } \
    else if (ttisnumber(s2v(ra)) && ttisnumber(rb)) { \
        cond = opn(s2v(ra), rb); } \
    else { \
        Protect(cond = other(L, s2v(ra), rb)); } \
    docondjump(); \
}

#define op_orderI(L,opi,opf,inv,tm) { \
    StkId ra = RA(i); \
    int cond; \
    int im = JIT_GETARG_sB(i); \
    if (ttisinteger(s2v(ra))) { \
        cond = opi(ivalue(s2v(ra)), im); } \
    else if (ttisfloat(s2v(ra))) { \
        lua_Number fa = fltvalue(s2v(ra)); \
        lua_Number fim = cast_num(im); \
        cond = opf(fa, fim); } \
    else { \
        int isf = JIT_GETARG_C(i); \
        Protect(cond = luaT_callorderiTM(L, s2v(ra), im, inv, isf, tm)); } \
    docondjump(); \
}

#define l_addi(L,a,b)	intop(+, a, b)
#define l_subi(L,a,b)	intop(-, a, b)
#define l_muli(L,a,b)	intop(*, a, b)
#define l_band(a,b)	intop(&, a, b)
#define l_bor(a,b)	intop(|, a, b)
#define l_bxor(a,b)	intop(^, a, b)

#define l_lti(a,b)	(a < b)
#define l_lei(a,b)	(a <= b)
#define l_gti(a,b)	(a > b)
#define l_gei(a,b)	(a >= b)

static void OP_ADDI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithI(L, l_addi, luai_numadd);
}

static void OP_ADDK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithK(L, l_addi, luai_numadd);
}

static void OP_SUBK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithK(L, l_subi, luai_numsub);
}

static void OP_MULK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();
    
    op_arithK(L, l_muli, luai_nummul);
}

static void OP_MODK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    savestate(L, ci); /* in case of division by 0 */
    op_arithK(L, luaV_mod, luaV_modf);
}

static void OP_POWK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithfK(L, luai_numpow);
}

static void OP_DIVK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithfK(L, luai_numdiv);
}

static void OP_IDIVK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    savestate(L, ci);  /* in case of division by 0 */
    op_arithK(L, luaV_idiv, luai_numidiv);
}

static void OP_BANDK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwiseK(L, l_band);
}

static void OP_BORK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwiseK(L, l_bor);
}

static void OP_BXORK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwiseK(L, l_bxor);
}

static void OP_SHRI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = vRB(i);
    int ic = JIT_GETARG_sC(i);
    lua_Integer ib;
    if (tointegerns(rb, &ib))
    {
        ctx->jit_pc++;
        setivalue(s2v(ra), luaV_shiftl(ib, -ic));
    }
}

static void OP_SHLI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = vRB(i);
    int ic = JIT_GETARG_sC(i);
    lua_Integer ib;
    if (tointegerns(rb, &ib))
    {
        ctx->jit_pc++;
        setivalue(s2v(ra), luaV_shiftl(ic, ib));
    }
}

static void OP_ADD_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arith(L, l_addi, luai_numadd);
}

static void OP_SUB_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arith(L, l_subi, luai_numsub);
}

static void OP_MUL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arith(L, l_muli, luai_nummul);
}

static void OP_MOD_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    savestate(L, ci);  /* in case of division by 0 */
    op_arith(L, luaV_mod, luaV_modf);
}

static void OP_POW_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithf(L, luai_numpow);
}

static void OP_DIV_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_arithf(L, luai_numdiv);
}

static void OP_IDIV_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    savestate(L, ci);  /* in case of division by 0 */
    op_arith(L, luaV_idiv, luai_numidiv);
}

static void OP_BAND_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwise(L, l_band);
}

static void OP_BOR_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwise(L, l_bor);
}

static void OP_BXOR_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwise(L, l_bxor);
}

static void OP_SHR_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwise(L, luaV_shiftr);
}

static void OP_SHL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_bitwise(L, luaV_shiftl);
}

// metamethod的实现，那几个操作符重载
static void OP_MMBIN_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TInstructionABC *pi = (TInstructionABC *)JIT_GET_INST(ctx->jit_pc - 2);
    TValue *rb = vRB(i);
    TMS tm = (TMS)JIT_GETARG_C(i);
    StkId result = RA(pi);
    lua_assert(OP_ADD <= JIT_GET_OPCODE(pi) && JIT_GET_OPCODE(pi) <= OP_SHR);
    Protect(luaT_trybinTM(L, s2v(ra), rb, result, tm));
}

static void OP_MMBINI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TInstructionABC *pi = (TInstructionABC *)JIT_GET_INST(ctx->jit_pc - 2);
    TValue *rb = vRB(i);
    TMS tm = (TMS)JIT_GETARG_C(i);
    StkId result = RA(pi);
    lua_assert(OP_ADD <= JIT_GET_OPCODE(pi) && JIT_GET_OPCODE(pi) <= OP_SHR);
    Protect(luaT_trybinTM(L, s2v(ra), rb, result, tm));
}

static void OP_MMBINK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TInstructionABC *pi = (TInstructionABC *)JIT_GET_INST(ctx->jit_pc - 2);
    TValue *imm = KB(i);
    TMS tm = (TMS)JIT_GETARG_C(i);
    int flip = JIT_GETARG_k(i);
    StkId result = RA(pi);
    Protect(luaT_trybinassocTM(L, s2v(ra), imm, flip, result, tm));
}

static void OP_UNM_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = vRB(i);
    lua_Number nb;
    if (ttisinteger(rb))
    {
        lua_Integer ib = ivalue(rb);
        setivalue(s2v(ra), intop(-, 0, ib));
    }
    else if (tonumberns(rb, nb))
    {
        setfltvalue(s2v(ra), luai_numunm(L, nb));
    }
    else
    {
        Protect(luaT_trybinTM(L, rb, rb, ra, TM_UNM));
    }
}

static void OP_BNOT_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = vRB(i);
    lua_Integer ib;
    if (tointegerns(rb, &ib)) 
    {
        setivalue(s2v(ra), intop(^, ~l_castS2U(0), ib));
    }
    else 
    {
        Protect(luaT_trybinTM(L, rb, rb, ra, TM_BNOT));
    }
}

static void OP_NOT_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = vRB(i);
    if (l_isfalse(rb))
    {
        setbtvalue(s2v(ra));
    }
    else
    {
        setbfvalue(s2v(ra));
    }
}

static void OP_LEN_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    Protect(luaV_objlen(L, ra, vRB(i)));
}

static void OP_CONCAT_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int n = JIT_GETARG_B(i);  /* number of elements to concatenate */
    L->top.p = ra + n;  /* mark the end of concat operands */
    ProtectNT(luaV_concat(L, n));
    checkGC(L, L->top.p); /* 'luaV_concat' ensures correct top */
}

static void OP_CLOSE_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    Protect(luaF_close(L, ra, LUA_OK, 1));
}

static void OP_TBC_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    /* create new to-be-closed upvalue */
    halfProtect(luaF_newtbcupval(L, ra));
}

static void OP_JMP_Func(TExecuteContext *ctx, TInstructionAx* i)
{
    UseL();

    dojump(ci, i, 0);
}

static void OP_EQ_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int cond;
    TValue *rb = vRB(i);
    Protect(cond = luaV_equalobj(L, s2v(ra), rb));
    docondjump();
}

static void OP_LT_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_order(L, l_lti, LTnum, lessthanothers);
}

static void OP_LE_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_order(L, l_lei, LEnum, lessequalothers);
}

static void OP_EQK_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = KB(i);
    /* basic types do not use '__eq'; we can use raw equality */
    int cond = luaV_rawequalobj(s2v(ra), rb);
    docondjump();
}

static void OP_EQI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int cond;
    int im = JIT_GETARG_sB(i);
    if (ttisinteger(s2v(ra)))
        cond = (ivalue(s2v(ra)) == im);
    else if (ttisfloat(s2v(ra)))
        cond = luai_numeq(fltvalue(s2v(ra)), cast_num(im));
    else
        cond = 0;  /* other types cannot be equal to a number */
    docondjump();
}

static void OP_LTI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_orderI(L, l_lti, luai_numlt, 0, TM_LT);
}

static void OP_LEI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_orderI(L, l_gti, luai_numgt, 1, TM_LT);
}

static void OP_GTI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_orderI(L, l_gei, luai_numge, 1, TM_LE);
}

static void OP_GEI_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    op_orderI(L, l_gei, luai_numge, 1, TM_LE);
}

static void OP_TEST_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int cond = !l_isfalse(s2v(ra));
    docondjump();
}

static void OP_TESTSET_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    TValue *rb = vRB(i);
    if (l_isfalse(rb) == JIT_GETARG_k(i)) 
    {
        ctx->jit_pc++;
    }
    else 
    {
        setobj2s(L, ra, rb);
        donextjump(ci);
    }
}

/*
** 这里要处理goto
*/
static void OP_CALL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    CallInfo *newci;
    int b = JIT_GETARG_B(i);
    int nresults = JIT_GETARG_C(i) - 1;
    /* fixed number of arguments? */
    if (b != 0) 
    {
        /* top signals number of arguments */
        L->top.p = ra + b;  
    }
    /* else previous instruction set top */
    savepc(L);  /* in case of errors */
    if ((newci = luaD_precall(L, ra, nresults)) == NULL)
    {
        /* C call; nothing else to be done */
        updatetrap(ci);  
    }
    else 
    {  
        /* Lua call: run function in this same C frame */
        ctx->ci = newci;
        //goto startfunc;
        ctx->exec_flag = EF_GOTO_STARTFUNC;
    }
}

static void OP_TAILCALL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();
    StkId base = ctx->base;

    StkId ra = RA(i);
    int b = JIT_GETARG_B(i);  /* number of arguments + 1 (function) */
    int n;  /* number of results when calling a C function */
    int nparams1 = JIT_GETARG_C(i);
    /* delta is virtual 'func' - real 'func' (vararg functions) */
    int delta = (nparams1) ? ci->u.l.nextraargs + nparams1 : 0;
    if (b != 0)
        L->top.p = ra + b;
    else  /* previous instruction set top */
        b = cast_int(L->top.p - ra);
    savepc(ci);  /* several calls here can raise errors */
    if (JIT_TESTARG_k(i))
    {
        luaF_closeupval(L, base);  /* close upvalues from current call */
        lua_assert(L->tbclist.p < base);  /* no pending tbc variables */
        lua_assert(base == ci->func.p + 1);
    }
    if ((n = luaD_pretailcall(L, ci, ra, b, delta)) < 0)  /* Lua function? */
    {
        /* execute the callee */
        //goto startfunc;  
        ctx->exec_flag = EF_GOTO_STARTFUNC;
    }
    else 
    {  
        /* C function? */
        ci->func.p -= delta;  /* restore 'func' (if vararg) */
        luaD_poscall(L, ci, n);  /* finish caller */
        updatetrap(ci);  /* 'luaD_poscall' can change hooks */
        /* caller returns after the tail call */
        goto_ret();
    }
}

static void OP_RETURN_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();
    StkId base = ctx->base;

    StkId ra = RA(i);
    int n = JIT_GETARG_B(i) - 1;  /* number of results */
    int nparams1 = JIT_GETARG_C(i);
    if (n < 0)  /* not fixed? */
        n = cast_int(L->top.p - ra);  /* get what is available */
    savepc(ci);
    if (JIT_TESTARG_k(i))
    {
        /* may there be open upvalues? */
        ci->u2.nres = n;  /* save number of returns */
        if (L->top.p < ci->top.p)
            L->top.p = ci->top.p;
        luaF_close(L, base, CLOSEKTOP, 1);
        updatetrap(ci);
        updatestack(ci);
    }
    if (nparams1)  /* vararg function? */
        ci->func.p -= ci->u.l.nextraargs + nparams1;
    L->top.p = ra + n;  /* set call for 'luaD_poscall' */
    luaD_poscall(L, ci, n);
    updatetrap(ci);  /* 'luaD_poscall' can change hooks */

    goto_ret();
}

static void OP_RETURN0_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();
    StkId base = ctx->base;

    if (l_unlikely(L->hookmask))
    {
        StkId ra = RA(i);
        L->top.p = ra;
        savepc(ci);
        luaD_poscall(L, ci, 0);  /* no hurry... */
        ctx->trap = 1;
    }
    else
    {  
        /* do the 'poscall' here */
        int nres;
        L->ci = ci->previous;  /* back to caller */
        L->top.p = base - 1;
        for (nres = ci->nresults; l_unlikely(nres > 0); nres--)
        {
            setnilvalue(s2v(L->top.p++));  /* all results are nil */
        }
    }

    goto_ret();
}

static void OP_RETURN1_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();
    StkId base = ctx->base;

    if (l_unlikely(L->hookmask))
    {
        StkId ra = RA(i);
        L->top.p = ra + 1;
        savepc(ci);
        luaD_poscall(L, ci, 1);  /* no hurry... */
        ctx->trap = 1;
    }
    else
    {
        /* do the 'poscall' here */
        int nres = ci->nresults;
        L->ci = ci->previous;  /* back to caller */
        if (nres == 0)
            L->top.p = base - 1;  /* asked for no results */
        else
        {
            StkId ra = RA(i);
            setobjs2s(L, base - 1, ra);  /* at least this result */
            L->top.p = base;
            for (; l_unlikely(nres > 1); nres--)
            {
                /* complete missing results */
                setnilvalue(s2v(L->top.p++));
            }
        }
    }

    goto_ret();
}

static void OP_FORLOOP_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    if (ttisinteger(s2v(ra + 2)))
    {
        /* integer loop? */
        lua_Unsigned count = l_castS2U(ivalue(s2v(ra + 1)));
        if (count > 0)
        {
            /* still more iterations? */
            lua_Integer step = ivalue(s2v(ra + 2));
            lua_Integer idx = ivalue(s2v(ra));  /* internal index */
            chgivalue(s2v(ra + 1), count - 1);  /* update counter */
            idx = intop(+, idx, step);  /* add step to index */
            chgivalue(s2v(ra), idx);  /* update internal index */
            setivalue(s2v(ra + 3), idx);  /* and control variable */
            ctx->jit_pc -= JIT_GETARG_Bx(i);  /* jump back */
        }
    }
    else if (floatforloop(ra))
    {
        /* float loop */
        ctx->jit_pc -= JIT_GETARG_Bx(i);  /* jump back */
    }
    updatetrap(ci);  /* allows a signal to break the loop */
}

static void OP_FORPREP_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    savestate(L, ci);  /* in case of errors */
    if (forprep(L, ra))
    {
        ctx->jit_pc += JIT_GETARG_Bx(i) + 1;  /* skip the loop */
    }
}

void OP_TFORCALL_Func(TExecuteContext *ctx, TInstructionABC* i);
void OP_TFORLOOP_Func(TExecuteContext *ctx, TInstructionABx* i);

static void OP_TFORPREP_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    /* create to-be-closed upvalue (if needed) */
    halfProtect(luaF_newtbcupval(L, ra + 3));
    ctx->jit_pc += JIT_GETARG_Bx(i);

    /* go to next instruction */
    TInstructionABC *ni = (TInstructionABC *)JIT_GET_INST(ctx->jit_pc);
    ctx->jit_pc++;

    lua_assert(JIT_GET_OPCODE(ni) == OP_TFORCALL && ra == RA(ni));
    OP_TFORCALL_Func(ctx, ni);
}

static void OP_TFORCALL_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    /* 'ra' has the iterator function, 'ra + 1' has the state,
       'ra + 2' has the control variable, and 'ra + 3' has the
       to-be-closed variable. The call will use the stack after
       these values (starting at 'ra + 4')
     */
    /* push function, state, and control variable */
    memcpy(ra + 4, ra, 3 * sizeof(*ra));
    L->top.p = ra + 4 + 3;
    ProtectNT(luaD_call(L, ra + 4, JIT_GETARG_C(i)));  /* do the call */
    updatestack(ci);  /* stack may have changed */

    TInstructionABx *ni = (TInstructionABx *)JIT_GET_INST(ctx->jit_pc);
    /* go to next instruction */
    ctx->jit_pc++;

    lua_assert(JIT_GET_OPCODE(ni) == OP_TFORLOOP && ra == RA(ni));
    OP_TFORLOOP_Func(ctx, ni);
}

static void OP_TFORLOOP_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    if (!ttisnil(s2v(ra + 4)))
    {
        /* continue loop? */
        setobjs2s(L, ra + 2, ra + 4);  /* save control variable */
        ctx->jit_pc -= JIT_GETARG_Bx(i);  /* jump back */
    }
}

static void OP_SETLIST_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int n = JIT_GETARG_B(i);
    unsigned int last = JIT_GETARG_C(i);
    Table *h = hvalue(s2v(ra));
    if (n == 0)
        n = cast_int(L->top.p - ra) - 1;  /* get up to the top */
    else
        L->top.p = ci->top.p;  /* correct top in case of emergency GC */
    last += n;

    if (JIT_TESTARG_k(i))
    {
        TInstructionAx *ni = (TInstructionAx *)JIT_GET_INST(ctx->jit_pc);
        last += JIT_GETARG_Ax(ni) * (MAXARG_C + 1);
        ctx->jit_pc++;
    }
    if (last > luaH_realasize(h))  /* needs more space? */
        luaH_resizearray(L, h, last);  /* preallocate it at once */
    for (; n > 0; n--)
    {
        TValue *val = s2v(ra + n);
        setobj2t(L, &h->array[last - 1], val);
        last--;
        luaC_barrierback(L, obj2gco(h), val);
    }
}

static void OP_CLOSURE_Func(TExecuteContext *ctx, TInstructionABx* i)
{
    UseL();

    StkId ra = RA(i);
    Proto *p = cl->p->p[JIT_GETARG_Bx(i)];
    halfProtect(pushclosure(L, p, cl->upvals, ctx->base, ra));
    checkGC(L, ra + 1);
}

static void OP_VARARG_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    StkId ra = RA(i);
    int n = JIT_GETARG_C(i) - 1;  /* required results */
    Protect(luaT_getvarargs(L, ci, ra, n));
}

static void OP_VARARGPREP_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    UseL();

    ProtectNT(luaT_adjustvarargs(L, JIT_GETARG_A(i), ci, cl->p));
    if (l_unlikely(ctx->trap))
    {
        /* previous "Protect" updated trap */
        luaD_hookcall(L, ci);
        L->oldpc = 1;  /* next opcode will be seen as a "new" line */
    }
    updatebase(ci);  /* function has new base after adjustment */
}

static void OP_EXTRAARG_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    JIT_UNUSE(ctx);JIT_UNUSE(i);

    lua_assert(0);
}


// jit 指令
static void JIT_NOOP_Func(TExecuteContext *ctx, TInstructionABC* i)
{
    JIT_UNUSE(ctx);JIT_UNUSE(i);
}





