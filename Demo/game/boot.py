#
# 2023年2月1日 bianpeng
#
from game.core import print_line
import sys

# init stdout, stderr
class PrintLine:
    def write(self, s):
        if s and s != '\n' and s != ' ' and s != '^':
            print_line(s)
            #print_line(repr(s))
            pass

    def flush(self):
        pass

saved_stderr = sys.stderr
sys.stderr = PrintLine()

saved_stdout = sys.stdout
sys.stdout = PrintLine()

print('boot ok')

