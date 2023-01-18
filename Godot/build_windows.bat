@rem scons -j6 platform=windows vsproj=yes bits=64 target=editor

goto :gd
goto :mono

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
scons p=windows tools=no bits=64 -j6 target=template_release
goto :end


:end

