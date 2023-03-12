#
# 2023年3月10日 bianpeng
#
# build script

import os
import os.path
import shutil
import glob

GODOT_DIR = 'D:\\OpenSource\\godot'
GP_DIR = 'D:\\OpenSource\\GodotPy'

if not os.path.exists(GODOT_DIR):
    GODOT_DIR = f'H:\\godot'
    GP_DIR = f'H:\\GodotPy'

GODOT_BIN_DIR = os.path.join(GODOT_DIR, 'bin')
EDITOR = os.path.join(GODOT_BIN_DIR, 'godot.windows.editor.x86_64.exe')
PLAYER = os.path.join(GODOT_BIN_DIR, 'godot.windows.template_release.x86_64.exe')

DEMO_DIR = os.path.join(GP_DIR, 'Demo')
BUILD_DIR = os.path.join(GP_DIR, 'Build')

RES_HACKER = f'd:\Tools\ResHacker\ResourceHacker.exe'
SCONS_EXE = 'scons.exe'

def run(cmd):
    print(cmd)
    os.system(cmd)

def build_publish():
    #run(f'{SCONS_EXE} p=windows vsproj=no bits=64 -j4 target=editor dev_build=false')
    build_editor_release()
    run(f'{EDITOR} -w --path "{DEMO_DIR}" --export-pack "Windows Desktop" {BUILD_DIR}\\Demo.pck')
    run(f'{SCONS_EXE} p=windows tools=no bits=64 -j4 target=template_release')

    file_list = (
        'python.exe',
        'python3.dll',
        'sqlite3.dll',
        '_sqlite3.pyd',
    )
    for item in file_list:
        shutil.copy(os.path.join(GODOT_BIN_DIR, item), os.path.join(BUILD_DIR, item))

    shutil.copy(EDITOR, os.path.join(BUILD_DIR, 'GodotEditor.exe'))
    shutil.copy(PLAYER, os.path.join(BUILD_DIR, 'Demo.exe'))
    shutil.copy(f'{DEMO_DIR}\\gm.py', os.path.join(BUILD_DIR, 'gm.py'))
    
    # replace app icon
    run(f'{RES_HACKER} -script {GP_DIR}\\Godot\\replace_icon.txt')

    # remove pyc
    for f in glob.iglob(f'{DEMO_DIR}\\game\\**\\*.pyc'):
        os.remove(f)

def build_editor_debug():
    run(f'{SCONS_EXE} p=windows vsproj=yes tools=yes bits=64 -j4 target=editor dev_build=true')

def build_editor_release():
    run(f'{SCONS_EXE} p=windows vsproj=no tools=yes bits=64 -j4 target=editor dev_build=false')

if __name__ == '__main__':
    import sys

    jump_table = {
        'publish' : build_publish,
        'editor_debug' : build_editor_debug,
        'editor_release' : build_editor_release,
    }
    fun = None
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        print(cmd)
        fun = jump_table.get(cmd, None)
    
    if fun:
        os.chdir(GODOT_DIR)
        fun()
    else:
        print('tasks', list(jump_table.keys()))

