/*
** bianpeng 2024-6-21
** begin to implement a simple jit, use c cross platform in c language, for a test
** without any asm jit framework
*/

#include "lua.h"

typedef struct _TInstruction
{
    int FuncID;
} TInstruction;

typedef struct _TInstructionA
{
    struct _TInstruction Inst;
    int a;
} TInstructionA;

typedef void (*TInstructFuntion)(TInstruction* pInstruct);


static void Add(TInstructionA* pInstruct)
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

static inline void ExecuteOne(TInstruction* pInstruct)
{
    TInstructFuntion Fun = InstructionFuncTable[pInstruct->FuncID];
    if (Fun)
    {
        Fun(pInstruct);
    }

}

void Execute(TInstruction *pInstruct, int start, int stop)
{
    for(int i = start; i < stop; ++i)
    {
        ExecuteOne(pInstruct + i);
    }
}


