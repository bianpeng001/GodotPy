#
# 2023年2月1日 bianpeng
#

#
# NOTICE!!! this file should put into the directory same as godot.exe
#
from io import StringIO
import os.path
import sys
import traceback

import GodotPy as gp

def print_line(*args, **kwargs):
    if not args:
        gp.print_line('')
    elif len(args) == 1:
        a = args[0]
        gp.print_line(str(a))
    else:
        a = ' '.join([str(x) for x in args])
        gp.print_line(a)

    if kwargs:
        sb = io.StringIO()
        for k in kwargs:
            sb.write(' ')
            sb.write(k)
            sb.write('=')
            sb.write(str(kwargs[k]))
        gp.print_line(sb.getvalue())

# saved_stderr = sys.stderr
# saved_stdout = sys.stdout

#
# init stdout, stderr
#
class PrintLine:
    def __init__(self):
        self.sb = StringIO()

    def write(self, s):
        if s == '\n':
            if self.sb.tell() > 0:
                print_line(self.sb.getvalue())
                self.sb.truncate(0)
                self.sb.seek(0)
        else:
            self.sb.write(s)
    
    def flush(self):
        pass

# 对标print, 但是输出到stderr
def print_error(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

# 后面那句print是有用的, 用来flush缓冲区数据, 强制打印到终端
def print_exception(err):
    traceback.print_exception(err)
    print('--------------------', file=sys.stderr)

import builtins
builtins.print_error = print_error
builtins.print_exception = print_exception

if __name__ != '__main__':
    sys.stderr = PrintLine()
    sys.stdout = PrintLine()

    exec_dir = os.path.dirname(sys.executable)
    sys.path.append(os.path.join(exec_dir, 'DLLs'))

    proj_dir = gp.get_project_path()
    if len(proj_dir) > 0:
        sys.path.insert(0, proj_dir)

    #sys.path.append(os.path.join(exec_dir, 'python313.zip'))

    print('sys.path:', sys.path)
    print('executable:', sys.executable)

print('boot ok')

