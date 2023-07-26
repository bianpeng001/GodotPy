#
# 2023年2月1日 bianpeng
#
from io import StringIO
import os.path
import sys
import traceback

from game.core import print_line

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

    dll_path = os.path.join(os.path.dirname(sys.executable), 'DLLs')
    sys.path.append(dll_path)
    print('path:', sys.path)
    print('executable:', sys.executable)

print('boot ok')

