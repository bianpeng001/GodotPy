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
# 业务逻辑也放到这里来，脏活累活都放这
# 有一些业务逻辑是好几个单位相互作用的
class GamePlay:
    def __init__(self):
        game_mgr.event_mgr.add(APP_LAUNCH, self.on_app_launch)
        game_mgr.event_mgr.add(START_GAME, self.on_start_game)
        game_mgr.event_mgr.add(MAIN_PLAYER_READY, self.on_player_ready)

        # 资源刷新tick
        self.resource_grow_time = 0

    # 事件
    def on_app_launch(self):
        # read window
        if os.path.exists('launch.json'):
            with open('launch.json', 'r') as f:
                obj = json.load(f)
                OS.set_window_size(*obj['window'])

        from game.player_mgr import PlayerMgr
        from game.hero_mgr import HeroMgr
        from game.unit_mgr import UnitMgr
        
        game_mgr.player_mgr = PlayerMgr()
        game_mgr.hero_mgr = HeroMgr()
        game_mgr.unit_mgr = UnitMgr()

    # create main player
    def on_start_game(self):
        pm = game_mgr.player_mgr
        cm = game_mgr.camera_mgr
        cm.update_camera()

        # 默认创建一个空城
        def co_bind_to_base_city():
            while True:
                city = game_mgr.unit_mgr.find_unit(lambda x: x.unit_type == UT_CITY \
                    and x.owner_player_id == 0)
                if city:
                    self.set_city_owner(city, pm.main_player)
                    city.get_controller().set_flag_color()

                    x,y,z = city.get_location()
                    cm.set_center(x,y,z)
                    cm.update_camera()

                    break

                yield None

            game_mgr.event_mgr.emit(MAIN_PLAYER_READY)

        log_util.debug('create main player')
        pm.main_player = pm.new_player()
        game_mgr.co_mgr.start(co_bind_to_base_city())
        test_wait_1()

    def on_player_ready(self):
        mp = game_mgr.player_mgr.main_player
        log_util.debug('on_player_ready', game_mgr.camera_mgr.center)

        self.refresh_resource_grow(0)


    # API方法，业务代码

    # 修改城城池归属
    def set_city_owner(self, city, player):
        if city.owner_player_id == player.player_id:
            log_util.error(f'player already own the city {player.player_id} -> {city.unit_name}')
            return

        if city.owner_player_id > 0:
            owner = game_mgr.player_mgr.get_player(city.owner_player_id)
            owner.city_list.remove(city.unit_id)
            city.owner_player_id = 0

        city.owner_player_id = player.player_id
        player.city_list.append(city.unit_id)

        # TODO: handle the heros in city

    # 队伍攻城
    def troop_attack_city(self, troop, city):
        if troop.owner_player_id == 0:
            return

        city.army_amount -= 60
        if city.army_amount < 0:
            city.army_amount = 0
            log_util.debug(f'city is occupied {troop.unit_id} -> {city.unit_name}')

            player = game_mgr.player_mgr.get_player(troop.owner_player_id)
            self.set_city_owner(city, player)
            city.get_controller().set_flag_color()

    def update(self, delta_time):
        self.resource_grow_time += delta_time
        if self.resource_grow_time > 1.1:
            self.refresh_resource_grow(self.resource_grow_time)
            self.resource_grow_time = 0

    # 刷新所有的资源增长, 这个开销也不大
    # delta_time：间隔时长，单位秒
    def refresh_resource_grow(self, delta_time):
        for city in game_mgr.unit_mgr.each_city():
            city.get_controller().grow_resource(delta_time)
        
        for player in game_mgr.player_mgr.each_player():
            player.total_money_amount = 0
            player.total_rice_amount = 0

            for city_id in player.city_list:
                city = game_mgr.unit_mgr.get_unit(city_id)
                player.total_money_amount += city.money_amount
                player.total_rice_amount += city.rice_amount
        
        # 完成，刷新界面
        game_mgr.event_mgr.emit(MAINUI_REFRESH)



