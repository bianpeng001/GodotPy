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

all: $(LUA_DLL) $(LUA)

CFLAGS_COMMON = -O2 -Wall -Wextra -DLUA_COMPAT_5_3
CFLAGS = $(CFLAGS_COMMON)

$(LUA_DLL): CFLAGS = $(CFLAGS_COMMON) -DLUA_BUILD_AS_DLL

%.o: src/%.c
	$(CC) -c $(CFLAGS) $< -o $@

lua_vm_jit.o: lua_vm_jit.c
	$(CC) -c $(CFLAGS) $< -o $@ -I src

$(LUA_DLL): $(CORE_O) $(LIB_O) lua_vm_jit.o
	$(CC) -shared -o $@ $^

lua.o: src/lua.c
	$(CC) -c $(CFLAGS) $< -o $@

$(LUA): $(LUA_DLL) lua.o
	$(CC) -o $@ lua.o lua.lib

$(LUAC): $(CORE_O) $(LIB_O) luac.o ldump.o
	$(CC) -o $@ $^

clean:
	del *.o



