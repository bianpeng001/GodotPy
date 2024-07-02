/*
** bianpeng 2024-6-21
*/

#ifndef __LUA_VM_JIT_H__
#define __LUA_VM_JIT_H__

void lua_vm_jit_execute(lua_State *L, CallInfo *ci);
void lua_vm_jit_compile(lua_State *L, CallInfo *ci);

#ifndef INT_TYPES

typedef long long int int64;
typedef unsigned long long uint64;
typedef int int32;
typedef unsigned int uint32;
typedef short int16;
typedef unsigned short uint16;
typedef char int8;
typedef unsigned char uint8;

#endif

struct _TAllocator
{
    void *memory;
    uint32 size;
    uint32 header;
};
typedef struct _TAllocator TAllocator;

TAllocator *TAllocator_Create(uint32 size);
void TAllocator_Destroy(TAllocator *allocator);
uint32 TAllocator_Alloc(TAllocator *allocator, uint32 size);

typedef struct _TInstruction TInstruction;

inline void *TAllocator_GetMemory(TAllocator *allocator, int32 offset)
{
    lua_assert(offset >= 0);
    return allocator->memory + offset;
}

#endif // __LUA_VM_JIT_H__



