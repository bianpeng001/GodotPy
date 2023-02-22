#
# 2023年1月31日 bianpeng
#

def print_line(*args, **kwargs):
    print(*args, **kwargs)

def connect(node, signal, callback):
    pass

def get_position(node):
    return 0,0,0

def set_position(node, x, y, z):
    pass

def lookat(node, x, y, z):
    pass

def screen_to_world(camera, x, y):
    return 0,0,0

def get_time():
    return 0

def get_delta_time():
    return 0
    
def instantiate(path):
    return None
    
class LogUtil:
    def debug(self, *args):
        print(*args)

    def error(self, *args):
        print(*args)

log_util = LogUtil()

print('init GodotPy ok')
