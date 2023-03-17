#
# 2023年3月10日 bianpeng
#
# build script

import os
import os.path
import shutil
import glob
import zipfile

GODOT_DIR = 'D:\\OpenSource\\godot'
PROJECT_DIR = 'D:\\OpenSource\\GodotPy'
PYTHON_DIR = 'D:\\OpenSource\\cpython'
THREADS = 6

if not os.path.exists(GODOT_DIR):
    GODOT_DIR = f'H:\\godot'
    PROJECT_DIR = f'H:\\GodotPy'
    PYTHON_DIR = 'H:\\cpython'
    THREADS = 4

GODOT_BIN_DIR = os.path.join(GODOT_DIR, 'bin')
EDITOR = os.path.join(GODOT_BIN_DIR, 'godot.windows.editor.x86_64.exe')
PLAYER = os.path.join(GODOT_BIN_DIR, 'godot.windows.template_release.x86_64.exe')

EDITOR_DEBUG = os.path.join(GODOT_BIN_DIR, 'godot.windows.editor.dev.x86_64.exe')

DEMO_DIR = os.path.join(PROJECT_DIR, 'Demo')
BUILD_DIR = os.path.join(PROJECT_DIR, 'Build')

RES_HACKER = f'd:\Tools\ResHacker\ResourceHacker.exe'
SCONS_EXE = 'scons.exe'

def run(cmd):
    print(cmd)
    os.system(cmd)

def build_publish():
    #run(f'{SCONS_EXE} p=windows vsproj=no bits=64 -j4 target=editor dev_build=false')
    build_editor_release()
    run(f'{EDITOR} -w --path "{DEMO_DIR}" --export-pack "Windows Desktop" {BUILD_DIR}\\Demo.pck')
    run(f'{SCONS_EXE} p=windows tools=no bits=64 -j{THREADS} target=template_release')

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
    shutil.copy(f'{PROJECT_DIR}\\LICENSE', os.path.join(BUILD_DIR, 'LICENSE'))
    
    # replace app icon
    run(f'{RES_HACKER} -script {PROJECT_DIR}\\Godot\\replace_icon.txt')

    make_python_zip()

    # remove pyc
    for f in glob.iglob(f'{DEMO_DIR}\\game\\**\\*.pyc'):
        os.remove(f)
    archive_demo()

def build_editor_debug():
    run(f'{SCONS_EXE} p=windows vsproj=yes tools=yes bits=64 -j{THREADS} target=editor dev_build=true')

def build_editor_release():
    run(f'{SCONS_EXE} p=windows vsproj=no tools=yes bits=64 -j{THREADS} target=editor dev_build=false')

def run_editor_release():
    run(f'{EDITOR} -w --path {DEMO_DIR} -e')

def play_editor_debug():
    run(f'{EDITOR_DEBUG} -w --path {DEMO_DIR}')

def zipdir(dir_path, f):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                f.write(file_path, os.path.relpath(file_path, dir_path))

def make_python_zip():
    path = f'{BUILD_DIR}\\python312.zip'
    if os.path.exists(path):
        os.remove(path)

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as f:
        zipdir(f'{PYTHON_DIR}\\Lib', f)

def archive_demo():
    path = f'{PROJECT_DIR}\\Demo.zip'
    if os.path.exists(path):
        os.remove(path)

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as f:
        zipdir(BUILD_DIR, f)

    os.rename(path, f'{BUILD_DIR}\\Demo.zip')

if __name__ == '__main__':
    import sys

    jump_table = {
        'publish' : build_publish,
        'editor_debug' : build_editor_debug,
        'editor_release' : build_editor_release,
        'run_editor_release' : run_editor_release,
        'play_editor_debug' : play_editor_debug,
        'python_zip' : make_python_zip,
        'archive_demo' : archive_demo,
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

