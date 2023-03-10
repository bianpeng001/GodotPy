#
# 2023年2月1日 bianpeng
#
from game.core import print_line
import sys

# saved_stderr = sys.stderr
# saved_stdout = sys.stdout

# init stdout, stderr
class PrintLine:
    def __init__(self):
        self.sb = []

    def write(self, s):
        if s == '\n':
            if len(self.sb) > 0:
                print_line(''.join(self.sb))
                self.sb.clear()
        else:
            self.sb.append(s)
    
    def flush(self):
        pass

if __name__ != '__main__':
    sys.stderr = PrintLine()
    sys.stdout = PrintLine()

print('boot ok')

