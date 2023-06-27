#
# 2023年1月31日 bianpeng
#

def print_line(*args, **kwargs):
    print(*args, **kwargs)

def get_time():
    return 0

def get_delta_time():
    return 1.0/60

def get_window_size():
    return 100,100

def get_window_rect():
    return 0, 0, 100, 100

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



