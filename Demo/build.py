#
# 2023年3月10日 bianpeng
#
# build script

import os
import os.path
import shutil
import glob

GODOT_DIR = 'D:\\OpenSource\\godot'
if not os.path.exists(GODOT_DIR):
    GODOT_DIR = ''

WORK_DIR = 'D:\\OpenSource\\GodotPy'
DEMO_DIR = os.path.join(WORK_DIR, 'Demo')
BUILD_DIR = os.path.join(WORK_DIR, 'Build')

EDITOR = os.path.join(GODOT_DIR, 'bin', 'godot.windows.editor.x86_64.exe')
PLAYER = os.path.join(GODOT_DIR, 'bin', 'godot.windows.template_release.x86_64.exe')

RES_HACKER = f'd:\Tools\ResHacker\ResourceHacker.exe'
SCONS_EXE = 'scons.exe'

def run(cmd):
    print(cmd)
    os.system(cmd)

def main():
    os.chdir(GODOT_DIR)

    run(f'{SCONS_EXE} p=windows vsproj=no bits=64 -j6 target=editor dev_build=false')
    run(f'{EDITOR} -w --path "{DEMO_DIR}" --export-pack "Windows Desktop" {BUILD_DIR}\\Demo.pck')
    run(f'{SCONS_EXE} p=windows tools=no bits=64 -j6 target=template_release')

    file_list = (
        'python.exe',
        'python3.dll',
        'sqlite3.dll',
        '_sqlite3.pyd',
    )
    for item in file_list:
        shutil.copy(os.path.join(GODOT_DIR, 'bin', item), os.path.join(BUILD_DIR, item))

    shutil.copy(EDITOR, os.path.join(BUILD_DIR, 'GodotEditor.exe'))
    shutil.copy(PLAYER, os.path.join(BUILD_DIR, 'Demo.exe'))
    shutil.copy(f'{DEMO_DIR}\\gm.py', os.path.join(BUILD_DIR, 'gm.py'))
    
    # replace app icon
    run(f'{RES_HACKER} -script {WORK_DIR}\\Godot\\replace_icon.txt')

    # remove pyc
    for f in glob.iglob(f'{DEMO_DIR}\\game\\**\\*.pyc'):
        os.remove(f)

if __name__ == '__main__':
    main()

