#
# 2023年2月1日 bianpeng
#
import sys
import os.path
from io import StringIO

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

if __name__ != '__main__':
    sys.stderr = PrintLine()
    sys.stdout = PrintLine()

    sys.path.append(os.path.join(os.path.dirname(sys.executable), 'DLLs'))
    #print(sys.executable)
    #print(sys.path)


print('boot ok')

