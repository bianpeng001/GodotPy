@rem scons -j6 platform=windows vsproj=yes bits=64 target=editor

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
@rem scons p=windows vsproj=yes bits=64 -j6 target=editor
scons p=windows vsproj=yes bits=64 -j6 target=editor dev_build=true
@rem scons p=windows tools=no bits=64 -j6 target=template_release
goto :end


:publish
set WORK_DIR=d:\OpenSource\GodotPy
scons p=windows tools=no bits=64 -j6 target=template_release
bin\godot.windows.editor.dev.x86_64.console.exe --path %WORK_DIR%\Demo -w --export-pack "Windows Desktop" %WORK_DIR%\Build\Demo.pck
copy /Y bin\python3.dll %WORK_DIR%\Build\python3.dll
copy /Y bin\godot.windows.template_release.x86_64.exe %WORK_DIR%\Build\Demo.exe

goto :end

:end

