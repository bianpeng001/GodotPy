set LUA_SRC=d:\OpenSource\lua-5.4.6\src
set CC=clang.exe

set CORE_O=lapi.o lcode.o lctype.o ldebug.o ldo.o ldump.o lfunc.o lgc.o llex.o lmem.o lobject.o lopcodes.o lparser.o lstate.o lstring.o ltable.o ltm.o lundump.o lvm.o lzio.o
set LIB_O=lauxlib.o lbaselib.o lcorolib.o ldblib.o liolib.o lmathlib.o loadlib.o loslib.o lstrlib.o ltablib.o lutf8lib.o linit.o
set BASE_O=%CORE_O% %LIB_O%

%CC% -O2 -Wall -Wextra -DLUA_COMPAT_5_3 -DLUA_BUILD_AS_DLL		-c %LUA_SRC%\*.c
@rem %CC% -O2 -Wall -Wextra -DLUA_COMPAT_5_3 -DLUA_BUILD_AS_DLL		-c -I %LUA_SRC% ..\Runtime\src\blua.c
%CC% -shared -o lua54.dll %BASE_O%
%CC% -o lua.exe lua.o lua54.lib
del %BASE_O%

%CC% -O2 -Wall -Wextra -DLUA_COMPAT_5_3 -c %LUA_SRC%\*.c
%CC% -o luac.exe luac.o %BASE_O%
del %BASE_O%

del *.o *.exp
