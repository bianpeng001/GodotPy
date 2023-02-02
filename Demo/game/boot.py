#
# 2023年2月1日 bianpeng
#
from game.core import print_line
import sys

class PrintLine:
    def write(self, s):
        if s and s != '\n':
            print_line(s)

saved_stderr = sys.stderr
sys.stderr = PrintLine()

saved_stdout = sys.stdout
sys.stdout = PrintLine()


print('boot ok')

