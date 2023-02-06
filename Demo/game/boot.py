#
# 2023年2月1日 bianpeng
#
from game.core import print_line
import sys

class PrintLine:
    def write(self, s):
        if s and s != '\n' and s != ' ' and s != '^':
            #print_line(s)
            print_line(repr(s))

saved_stderr = sys.stderr
sys.stderr = PrintLine()

saved_stdout = sys.stdout
sys.stdout = PrintLine()

from game.game_mgr import game_mgr
from game.event_mgr import EventMgr
game_mgr._event_mgr = EventMgr()

print('boot ok')

