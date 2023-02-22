#
# 2023年2月1日 bianpeng
#
from game.core import print_line, log_util
import sys

# saved_stderr = sys.stderr
# saved_stdout = sys.stdout

# init stdout, stderr
class PrintLine:
    def write(self, s):
        if s and s != '\n' and s != ' ' and s != '^':
            print_line(s)
            #print_line(repr(s))
            pass

    def flush(self):
        pass
        
sys.stderr = PrintLine()
sys.stdout = PrintLine()


log_util.debug('boot ok')

