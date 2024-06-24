#ifndef __LUA_VM_JIT_H__
#define __LUA_VM_JIT_H__

void lua_vm_jit_execute(lua_State *L, CallInfo *ci);


struct _TAllocator
{
    void *memory;
    size_t size;
    size_t header;
};
typedef struct _TAllocator TAllocator;

TAllocator *TAllocator_Create(size_t size);
void TAllocator_Destroy(TAllocator *allocator);
size_t TAllocator_Alloc(TAllocator *allocator, size_t size);
void *TAllocator_GetMemory(TAllocator *allocator, size_t offset);


#endif // __LUA_VM_JIT_H__



