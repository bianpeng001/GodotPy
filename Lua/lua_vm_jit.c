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

#include <stdlib.h>
#include <string.h>

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
    uint32 FuncID;
};
typedef struct _TInstruction TInstruction;

/* iABC */
struct _TInstructionABC
{
    struct _TInstruction Inst;
    uint8 A, B, C;
};
typedef struct _TInstructionABC TInstructionABC;

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
    Instruction *pc;
    int trap;

};
typedef struct _TExecuteContext TExecuteContext;

typedef void (*TInstructFunction)(TExecuteContext *ctx, TInstruction* pInstruct);

// instruction implement
static void OP_MOVE_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
}
static void OP_LOADI_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
}
static void OP_ADD_Func(TExecuteContext *ctx, TInstructionABC* pInstruct)
{
}

#define RegFunc(FuncName) (TInstructFunction)&FuncName ## _Func

static TInstructFunction InstructionFuncTable[] = 
{
    RegFunc(OP_MOVE),
    RegFunc(OP_LOADI),
    RegFunc(OP_ADD),
    RegFunc(OP_MOVE),
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

static void Execute(TExecuteContext *ctx, TInstruction *pInstruct, int start, int stop)
{
    for (int i = start; i < stop; ++i)
    {
        ExecuteOne(ctx, pInstruct + i);
    }
}

void lua_vm_jit_execute(lua_State *L, CallInfo *ci)
{
    TExecuteContext ctx;
    ctx.L = L;
    ctx.ci = ci;

    TInstruction *code = NULL;

    Execute(&ctx, code, 0, 0);
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

    if (allocator->header)
    {
        allocator->size *= 2;
        allocator->memory = realloc(allocator->memory, allocator->size);
    }

    return offset;
}

void *TAllocator_GetMemory(TAllocator *allocator, size_t offset)
{
    return allocator->memory + offset;
}





