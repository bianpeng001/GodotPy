#
# simple lua jit
#

.PHONY: clean all

CC = clang.exe
LUA_DLL = lua.dll
LUA = lua.exe
LUAC = luac.exe
RM = del.exe

CORE_O = lapi.o lcode.o lctype.o ldebug.o ldo.o ldump.o lfunc.o lgc.o llex.o lmem.o lobject.o lopcodes.o lparser.o lstate.o lstring.o ltable.o ltm.o lundump.o lvm.o lzio.o
LIB_O = lauxlib.o lbaselib.o lcorolib.o ldblib.o liolib.o lmathlib.o loadlib.o loslib.o lstrlib.o ltablib.o lutf8lib.o linit.o

$(info generate obj files)
$(info ****************************************)
OBJ := $(foreach X, $(CORE_O) $(LIB_O), src/$(X))
$(info $(OBJ))
$(info ****************************************)

all: $(LUA_DLL) $(LUA)

#-O2 -Wall -Wextra -DLUA_COMPAT_5_3
CFLAGS = -O2 -Wall -Wextra
$(LUA_DLL): CFLAGS += -DLUA_BUILD_AS_DLL

src/%.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

%.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

lua_vm_jit.o: lua_vm_jit.c lua_vm_jit.h lua_vm_op_impl.h
	$(CC) -c $(CFLAGS) $< -o $@ -I src

$(LUA_DLL): $(OBJ) lua_vm_jit.o
	$(CC) -shared -o $@ $^

$(LUA): $(LUA_DLL) src/lua.o
	$(CC) -o $@ lua.lib src/lua.o

$(LUAC): $(OBJ) src/luac.o src/ldump.o
	$(CC) -o $@ $^

clean:
	del *.o src\*.o



