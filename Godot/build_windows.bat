@rem scons -j6 platform=windows vsproj=yes bits=64 target=editor

@set cmd=%1
@echo "cmd=%cmd%"
@IF "%cmd%" == "publish" ( GOTO :publish )
@IF "%cmd%" == "editor_release" ( GOTO :editor_release )

goto :gd
@rem goto :mono
@rem goto :publish
goto :end

:mono
scons p=windows bits=64 target=editor module_mono_enabled=yes
bin\godot.windows.editor.x86_64.mono.console.exe --headless --generate-mono-glue modules/mono/glue
python modules\mono\build_scripts\build_assemblies.py --godot-output-dir=.\bin --godot-platform=windows
scons p=windows vsproj=yes target=editor bits=64 module_mono_enabled=yes
@rem scons p=windows target=template_release module_mono_enabled=yes
goto :end

:gd
:editor_debug
@rem scons p=windows vsproj=yes bits=64 -j6 target=editor
@rem scons p=windows tools=no bits=64 -j6 target=template_release
scons p=windows vsproj=yes bits=64 -j6 target=editor dev_build=true
goto :end

:editor_release
scons p=windows vsproj=no bits=64 -j6 target=editor dev_build=false
goto :end


:publish
set DEMO_DIR=..\GodotPy\Demo
set BUILD_DIR=..\GodotPy\Build
set EDITOR=bin\godot.windows.editor.x86_64.exe
set PLAYER=bin\godot.windows.template_release.x86_64.exe
set RES_HACKER=d:\Tools\ResHacker\ResourceHacker.exe

@rem build editor
scons p=windows vsproj=yes bits=64 -j6 target=editor dev_build=false
copy /Y %EDITOR% %BUILD_DIR%\GodotEditor.exe
@rem pack resources
%EDITOR% --path %DEMO_DIR% -w --export-pack "Windows Desktop" %BUILD_DIR%\Demo.pck
@rem build player, copy deps
scons p=windows tools=no bits=64 -j6 target=template_release
copy /Y %PLAYER% %BUILD_DIR%\Demo.exe
copy /Y bin\python.exe %BUILD_DIR%\python.exe

copy /Y bin\python3.dll %BUILD_DIR%\python3.dll
copy /Y bin\sqlite3.dll %BUILD_DIR%\sqlite3.dll
copy /Y bin\_sqlite3.pyd %BUILD_DIR%\_sqlite3.pyd

%RES_HACKER% -script %DEMO_DIR%\..\Godot\replace_icon.txt

goto :end

:end

