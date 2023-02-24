#
# 2023年1月31日 bianpeng
#

def print_line(*args, **kwargs):
    print(*args, **kwargs)
   
class LogUtil:
    def debug(self, *args):
        print(*args)

    def error(self, *args):
        print(*args)

log_util = LogUtil()

print('init GodotPy ok')
