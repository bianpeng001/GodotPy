#
# 2023年3月10日 bianpeng
#
# build script

import glob
import os
import os.path
import shutil
import sys
import time
import zipfile

# 工具路径
PROJECT_DIR = 'D:\\OpenSource\\GodotPy'
GODOT_DIR = 'D:\\OpenSource\\godot'
PYTHON_DIR = 'D:\\OpenSource\\cpython'
THREADS = 12

if not os.path.exists(PROJECT_DIR):
    PROJECT_DIR = 'H:\\GodotPy'
    GODOT_DIR = 'H:\\godot'
    PYTHON_DIR = 'H:\\cpython'
    THREADS = 4

SCONS_EXE = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'scons.exe')
GIT_EXE = 'D:\\Tools\\PortableGit\\bin\\git.exe'
RES_HACKER = 'D:\\Tools\\ResHacker\\ResourceHacker.exe'

# 版本信息
python_tag = '3.13.0a0'
godot_tag = '4.2.dev.custom_build'
demo_tag = '1.0.0'

# 攻城结构
GODOT_BIN_DIR = os.path.join(GODOT_DIR, 'bin')
EDITOR = os.path.join(GODOT_BIN_DIR, 'godot.windows.editor.x86_64.exe')
EDITOR_DEBUG = os.path.join(GODOT_BIN_DIR, 'godot.windows.editor.dev.x86_64.exe')
PLAYER = os.path.join(GODOT_BIN_DIR, 'godot.windows.template_release.x86_64.exe')

DEMO_DIR = os.path.join(PROJECT_DIR, 'Demo')
BUILD_DIR = os.path.join(PROJECT_DIR, 'Build')

def run(cmd):
    print(cmd)
    os.system(cmd)
    
def copy(src_path, dst_path):
    if not os.path.exists(dst_path) or \
            os.path.getmtime(dst_path) < os.path.getmtime(src_path):
        print('copy', src_path, '->', dst_path)
        shutil.copyfile(src_path, dst_path)
    else:
        print('skip', dst_path)

def mkdir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)

def build_publish():
    call_task('python')
    run(f'{SCONS_EXE} p=windows vsproj=no bits=64{THREADS} target=editor dev_build=false')
    call_task('editor_release')
    # build package
    call_task('package')
    # build player
    call_task('player_release')
    
    # 开始
    os.chdir(PROJECT_DIR)

    # 先创建目录
    mkdir_if_not_exists(BUILD_DIR)
    # 写当前的版本信息
    run(f'{GIT_EXE} log -1 --format=%H > demo_ver.txt')
    # 打包demo源码
    run(f'{GIT_EXE} archive -o Build\\src.tgz HEAD Demo')

    # 需要从bin里面复制的文件
    file_list = (
        'sqlite3.dll',
        '_sqlite3.pyd',
        '_socket.pyd',
        '_asyncio.pyd',
        '_overlapped.pyd',
        '_multiprocessing.pyd',
        '_queue.pyd',
        '_decimal.pyd',
    )
    copy(os.path.join(GODOT_BIN_DIR, "python.exe"), os.path.join(BUILD_DIR, "python.exe"))
    copy(os.path.join(GODOT_BIN_DIR, "python3.dll"), os.path.join(BUILD_DIR, "python3.dll"))
    copy(os.path.join(PROJECT_DIR, '3rd', 'vcruntime140.dll'), os.path.join(BUILD_DIR, 'vcruntime140.dll'))
    mkdir_if_not_exists(os.path.join(BUILD_DIR, "DLLs"))
    for item in file_list:
        copy(os.path.join(GODOT_BIN_DIR, "DLLs", item), os.path.join(BUILD_DIR, "DLLs", item))

    copy(EDITOR, os.path.join(BUILD_DIR, 'GodotEditor.exe'))
    copy(PLAYER, os.path.join(BUILD_DIR, 'Demo.exe'))
    copy(PLAYER.replace('.exe','.console.exe'), os.path.join(BUILD_DIR, 'Demo.console.exe'))
    copy(os.path.join(DEMO_DIR, 'gm.py'), os.path.join(BUILD_DIR, 'gm.py'))
    copy(os.path.join(PROJECT_DIR, 'LICENSE'), os.path.join(BUILD_DIR, 'LICENSE'))
    
    # replace app icon
    run(f'{RES_HACKER} -script {PROJECT_DIR}\\Godot\\replace_icon.txt')
    run(f'{RES_HACKER} -script {PROJECT_DIR}\\Godot\\replace_icon_console.txt')

    # zip python313.zip
    call_task('archive_python')

    with open(f'{PYTHON_DIR}\\python_ver.txt') as f:
        python_ver = f.read().strip()
    with open(f'{GODOT_DIR}\\godot_ver.txt') as f:
        godot_ver = f.read().strip()
    with open(f'{PROJECT_DIR}\\demo_ver.txt') as f:
        demo_ver = f.read().strip()
    with open(f'{BUILD_DIR}\\verion.txt', 'w') as f:
        f.write(f'python {python_tag} {python_ver}\n')
        f.write(f'godot {godot_tag} {godot_ver}\n')
        f.write(f'demo {demo_tag} {demo_ver}\n')

    # zip Demo.zip
    call_task('archive_demo')

def build_editor_debug():
    run(f'{SCONS_EXE} p=windows vsproj=yes tools=yes bits=64 -j{THREADS} target=editor warnings=no dev_build=true')

def build_editor_release():
    run(f'{SCONS_EXE} p=windows vsproj=no tools=yes bits=64 -j{THREADS} target=editor warnings=no dev_build=false')

def run_editor_release():
    run(f'{EDITOR} -w --path {DEMO_DIR} -e')

def play_editor_debug():
    run(f'{EDITOR_DEBUG} -w --path {DEMO_DIR}')

# 打包一个目录, 过滤文件
def zipdir(dir_path, f):
    for root, dirs, files in os.walk(dir_path, followlinks=True):
        if root.endswith('.vscode'):
            continue
        
        for file in files:
            if file.endswith('.pyc') or file.endswith('.import'):
                continue
            
            file_path = os.path.join(root, file)
            f.write(file_path, os.path.relpath(file_path, dir_path))

def archive_python():
    path = f'{BUILD_DIR}\\python313.zip'
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
    run(f'{GIT_EXE} log -1 --format=%H > python_ver.txt')
    os.chdir(GODOT_DIR)

def build_pck():
    run(f'{EDITOR} -w --path "{DEMO_DIR}" --export-pack "Windows Desktop" {BUILD_DIR}\\Demo.pck')

def build_player_release():
    run(f'{SCONS_EXE} p=windows tools=no bits=64 -j{THREADS} target=template_release')
    #run(f'{SCONS_EXE} p=windows vsproj=yes tools=no bits=64 -j{THREADS} target=template_release')
    run(f'{GIT_EXE} log -1 --format=%H > godot_ver.txt')

def verinfo():
    os.chdir(GODOT_DIR)
    run(f'{GIT_EXE} log -1 --format=%H')
    os.chdir(PYTHON_DIR)
    run(f'{GIT_EXE} log -1 --format=%h')

def cleanup():
    os.chdir(GODOT_DIR)
    run(f'{SCONS_EXE} --clean dev_build=True')
    run(f'{SCONS_EXE} --clean dev_build=False')
    os.chdir(PYTHON_DIR)
    run(f'{SCONS_EXE} --clean')

# tasks
task_table = {
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
        'cleanup' : cleanup,
        'verinfo' : verinfo,
    }

def call_task(task_name):
    fun = task_table.get(task_name, None)
    if fun:
        print('-------', task_name, 'begin')
        t1 = time.time()
        os.chdir(GODOT_DIR)
        fun()
        cost_time = time.time() - t1
        print('-------', task_name, 'end', f'in {cost_time:.1f}s')
    else:
        print('tasks', list(task_table.keys()))

if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        call_task(cmd)
    else:
        print('cmd required')
    

