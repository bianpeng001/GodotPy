#
# simple lua jit
#

.PHONY: clean all

CC = clang.exe
LUA_DLL = lua.dll
LUA = lua.exe
LUA_C = luac.exe
RM = del.exe

CORE_O = lapi lcode lctype ldebug ldo ldump lfunc lgc llex lmem lobject lopcodes lparser lstate lstring ltable ltm lundump lvm lzio
LIB_O = lauxlib lbaselib lcorolib ldblib liolib lmathlib loadlib loslib lstrlib ltablib lutf8lib linit


all: $(LUA_DLL) $(LUA) $(LUA_C)

#-O2 -Wall -Wextra -DLUA_COMPAT_5_3
# -DLUAI_ASSERT
CFLAGS = -O3 -Wall -Wextra
$(LUA_DLL): CFLAGS += -DLUA_BUILD_AS_DLL

#$(info generate obj files)
#$(info ****************************************)
OBJ := $(foreach Item, $(CORE_O) $(LIB_O), src/$(Item).o)
DLL_OBJ := $(foreach Item, $(CORE_O) $(LIB_O), src/$(Item)_d.o)
C_OBJ := $(foreach Item, $(CORE_O) $(LIB_O) luac ldump, src/$(Item)_c.o)
#$(info $(OBJ))
#$(info ****************************************)


# 几种不同的后缀，区分不同的目标，的模式
src/%_d.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

src/%_c.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

src/%.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

%.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

lua_vm_jit.o: lua_vm_jit.c lua_vm_jit.h lua_vm_op_impl.h
	$(CC) -c $(CFLAGS) $< -o $@ -I src

$(LUA_DLL): $(DLL_OBJ) lua_vm_jit.o
	$(CC) -shared -o $@ $^

$(LUA): $(LUA_DLL) src/lua_c.o
	$(CC) -o $@ lua.lib src/lua_c.o

$(LUA_C): $(C_OBJ)
	$(CC) -o $@ $^

clean:
	del *.o src\*.o



