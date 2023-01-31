#
# 2023年1月31日 bianpeng
#
from game.core import *


# 地面
class GroudMgr(NodeObject):
    def __init__(self):
        super().__init__()
    
    def _create(self):
        set_process(self._get_node(), process=True, input=False)
        connect(self._get_node(), "ready", self._ready)
        
        print_line('create GroundMgr ok')

    def _ready(self):
        print_line('GroundMgr ready')

    def _process(self):
        delta_time = get_delta_time()
        pass

