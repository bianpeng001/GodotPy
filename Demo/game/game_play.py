#
# 2023年2月10日 bianpeng
#
import os
import os.path
import json

from game.core import *
from game.game_mgr import game_mgr
from game.event_name import *
from game.base_type import UT_CITY
from game.wait import *

# 游戏的控制逻辑, 事件响应啥的，集中到这里来
class GamePlay:
    def __init__(self):
        game_mgr.event_mgr.add(APP_LAUNCH, self.on_app_launch)
        game_mgr.event_mgr.add(START_GAME, self.on_start_game)
        game_mgr.event_mgr.add(MAIN_PLAYER_READY, self.on_player_ready)

        pass

    def on_app_launch(self):
        # read window
        if os.path.exists('launch.json'):
            with open('launch.json', 'r') as f:
                obj = json.load(f)
                OS.set_window_size(*obj['window'])

        from game.unit_mgr import UnitMgr
        from game.player_mgr import PlayerMgr
        from game.hero_mgr import HeroMgr
        
        game_mgr.unit_mgr = UnitMgr()
        game_mgr.player_mgr = PlayerMgr()
        game_mgr.hero_mgr = HeroMgr()

    # create main player
    def on_start_game(self):
        pm = game_mgr.player_mgr
        cm = game_mgr.camera_mgr

        def co_bind_to_base_city():
            while True:
                unit = game_mgr.unit_mgr.find_unit(lambda x: x.unit_type == UT_CITY \
                    and x.owner_player_id == 0)
                if unit:
                    pm.main_player.base_city_id = unit.unit_id
                    x,y,z = unit.get_location()
                    cm.set_center(x,y,z)
                    cm.update_camera()
                    break

                yield None

            game_mgr.event_mgr.emit(MAIN_PLAYER_READY)
                
        log_util.debug('create main player')
        pm.main_player = pm.create_player()
        game_mgr.co_mgr.start(co_bind_to_base_city())
        test_wait_1()

    def on_player_ready(self):
        mp = game_mgr.player_mgr.main_player
        log_util.debug('on_player_ready', 
            game_mgr.camera_mgr.center,
            mp.base_city_id)


        

