#
# 2023年2月1日 bianpeng
#
from game.core import print_text
import sys

class FakeStdOut:
    def write(self, s):
        print_text(s)

saved_stderr = sys.stderr
sys.stderr = FakeStdOut()

saved_stdout = sys.stdout
sys.stdout = FakeStdOut()


