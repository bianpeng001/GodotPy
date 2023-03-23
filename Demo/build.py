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

RES_HACKER = f'D:\Tools\ResHacker\ResourceHacker.exe'
SCONS_EXE = 'scons.exe'

def run(cmd):
    print(cmd)
    os.system(cmd)

def build_publish():
    build_python()
    #run(f'{SCONS_EXE} p=windows vsproj=no bits=64 -j4 target=editor dev_build=false')
    build_editor_release()
    # build package
    build_pck()
    # build player
    build_player_release()
    
    # copy files
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
    
    # zip python312.zip
    archive_python()

    # 这步不需要了, zipdir 的时候, 会跳过pyc
    # remove pyc
    # for f in glob.iglob(f'{DEMO_DIR}\\game\\**\\*.pyc'):
    #     os.remove(f)

    # zip Demo.zip
    archive_demo()

    print('------------- build ok -------------')

def build_editor_debug():
    run(f'{SCONS_EXE} p=windows vsproj=yes tools=yes bits=64 -j{THREADS} target=editor dev_build=true')

def build_editor_release():
    run(f'{SCONS_EXE} p=windows vsproj=no tools=yes bits=64 -j{THREADS} target=editor dev_build=false')

def run_editor_release():
    run(f'{EDITOR} -w --path {DEMO_DIR} -e')

def play_editor_debug():
    run(f'{EDITOR_DEBUG} -w --path {DEMO_DIR}')

def zipdir(dir_path, f):
    for root, dirs, files in os.walk(dir_path, followlinks=True):
        for file in files:
            if not file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                f.write(file_path, os.path.relpath(file_path, dir_path))

def archive_python():
    path = f'{BUILD_DIR}\\python312.zip'
    if os.path.exists(path):
        os.remove(path)

    lib_dir = f'{PYTHON_DIR}\\Lib'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as f:
        zipdir(lib_dir, f)

def archive_demo():
    path1 = f'{BUILD_DIR}\\..\\Demo.zip'
    path2 = f'{BUILD_DIR}\\Demo.zip'

    if os.path.exists(path1):
        os.remove(path1)
    if os.path.exists(path2):
        os.remove(path2)

    with zipfile.ZipFile(path1, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as f:
        zipdir(BUILD_DIR, f)

    os.rename(path1, path2)

def build_python():
    os.chdir(PYTHON_DIR)
    run(f'{SCONS_EXE}')
    os.chdir(GODOT_DIR)

def build_pck():
    run(f'{EDITOR} -w --path "{DEMO_DIR}" --export-pack "Windows Desktop" {BUILD_DIR}\\Demo.pck')

def build_player_release():
    run(f'{SCONS_EXE} p=windows tools=no bits=64 -j{THREADS} target=template_release')

if __name__ == '__main__':
    import sys

    jump_table = {
        'publish' : build_publish,
        'editor_debug' : build_editor_debug,
        'editor_release' : build_editor_release,
        'run_editor_release' : run_editor_release,
        'play_editor_debug' : play_editor_debug,

        # 分步骤
        'python' : build_python,
        'player_release' : build_player_release,
        'package' : build_pck,
        'archive_python' : archive_python,
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

