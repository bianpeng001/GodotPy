cl /nologo /Zi /c test.c /ID:\OpenSource\cpython\Include /ID:\OpenSource\cpython\Include/internal /IGodot
link /nologo /debug:full /out:test.exe test.obj godot_python3.lib Kernel32.lib

test.exe

