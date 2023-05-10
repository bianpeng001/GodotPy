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
log_debug = log_util.debug

class FObject:
    pass

class FNode(FObject):
    pass

class FNode3D(FNode):
    pass

class FCanvasItem(FNode):
    pass

print('init GodotPy ok')



