#
# 2023年2月9日 bianepng
#
from game.core import *
from game.game_mgr import *
from game.coroutine_mgr import Waitable, WaitForSeconds 

#
# 等待面板关闭
#
class WaitForClose(Waitable):
    def __init__(self, pnl):
        super().__init__()
        self.pnl = pnl
        
    def is_done(self):
        return not self.pnl.is_show()
    

def test_wait_1():
    def co_print_number():
        print('co_print_number', game_mgr.frame_number)
        yield
        print(game_mgr.frame_number, game_mgr.time_sec)
        yield
        print(game_mgr.frame_number, game_mgr.time_sec)
        yield
        print(game_mgr.frame_number, game_mgr.time_sec)
        yield
        print(game_mgr.frame_number, game_mgr.time_sec)
        yield
        print(game_mgr.frame_number, game_mgr.time_sec)

        print(f'{OS.get_time()} {game_mgr.time_sec}')
        yield WaitForSeconds(3)
        print(f'{OS.get_time()} {game_mgr.time_sec}')
        
    game_mgr.co_mgr.start(co_print_number())





