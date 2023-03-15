#
# 2023年2月10日 bianpeng
#
import os
import os.path
import json

from game.core import *
from game.game_mgr import *
from game.event_name import *
from game.wait import *
from game.base_type import UT_CITY, UT_TROOP

# 游戏的控制逻辑, 事件响应啥的，集中到这里来
# 业务逻辑也放到这里来，脏活累活都放这
# 有一些业务逻辑是好几个单位相互作用的
class GamePlay:
    def __init__(self):
        # init sub systems
        from game.config_mgr import ConfigMgr
        from game.player_mgr import PlayerMgr
        from game.hero_mgr import HeroMgr
        from game.unit_mgr import UnitMgr
        from game.effect_mgr import EffectMgr
        from game.game_data import GameData
        from game.hud_mgr import HUDMgr
        
        game_mgr.player_mgr = PlayerMgr()
        game_mgr.hero_mgr = HeroMgr()
        game_mgr.unit_mgr = UnitMgr()
        game_mgr.effect_mgr = EffectMgr()
        game_mgr.game_data = GameData()
        game_mgr.config_mgr = ConfigMgr()
        game_mgr.hud_mgr = HUDMgr()

        game_mgr.hud_mgr.setup()
        
        # 资源刷新tick
        self.data_tick_time = 0

        # add event handler
        game_mgr.event_mgr.add(APP_LAUNCH, self.on_app_launch)
        game_mgr.event_mgr.add(START_GAME, self.on_start_game)
        game_mgr.event_mgr.add(MAIN_PLAYER_READY, self.on_player_ready)

    # 事件
    def on_app_launch(self):
        log_util.debug('on_app_launch')
        game_mgr.init_update_list()
        game_mgr.ground_mgr.load_data()

        # read window
        if os.path.exists('launch.json'):
            with open('launch.json', 'r') as f:
                obj = json.load(f)
                OS.set_window_rect(*obj['window'])

        # 起始块, 不加载物件，因为这块可能会有一些特效残留的bug，
        # 弄一个建筑物挡一挡，毕竟是天下之中
        tile, _ = game_mgr.ground_mgr.create_tile(0, 0)
        tile.load()

    # create main player
    def on_start_game(self):
        pm = game_mgr.player_mgr
        cm = game_mgr.camera_mgr
        cm.update_camera()

        # 默认创建一个空城
        def co_bind_to_base_city():
            while True:
                city = game_mgr.unit_mgr.find_unit(lambda x:
                        x.unit_type == UT_CITY \
                        and x.owner_player_id == 0)
                if city:
                    self.set_city_owner(city, pm.main_player)
                    pm.main_player.main_city_id = city.unit_id

                    city.get_controller().set_flag_color()
                    hud_item = game_mgr.hud_mgr.get_hud(city.unit_id)
                    if hud_item:
                        hud_item.set_flag_text(pm.main_player.player_name[0])
                        hud_item.set_flag_color(0.0,1.0,0.0)

                    #cm.set_center(x,y,z)
                    cm.set_target_center(*city.get_position())
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

        self.refresh_player_resource(0)
        
        #game_mgr.ui_mgr.story_panel_controller.play_story()

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

        # TODO: 城中的武将的归属,逃走俘虏

    # 队伍攻城
    def troop_attack_city(self, troop, city):
        if troop.owner_player_id == 0:
            return

        city.army_amount.add(-100)
        if city.army_amount.value < 0:
            city.army_amount.value = 0
            log_util.debug(f'city is occupied {troop.unit_id} -> {city.unit_name}')

            player = game_mgr.player_mgr.get_player(troop.owner_player_id)
            self.set_city_owner(city, player)
            city.get_controller().set_flag_color()

    def update(self, delta_time):
        # 游戏时间
        game_data = game_mgr.game_data
        time_scale = game_mgr.config_mgr.play_time_scale
        game_data.play_time += delta_time * time_scale
        
        # 资源刷新
        self.data_tick_time += delta_time
        if self.data_tick_time > 30.0:
            # 刷新日期
            game_data.cur_year = game_data.get_cur_year()
            # 结算资源
            self.refresh_player_resource(self.data_tick_time)
            self.data_tick_time = 0

    # 刷新所有的资源增长, 这个开销也不大
    # delta_time：间隔时长，单位秒
    def refresh_player_resource(self, delta_time):
        for city in game_mgr.unit_mgr.each_city():
            city.get_controller().refresh_resource_amount(delta_time)
        
        for player in game_mgr.player_mgr.each_player():
            player.total_money_amount = 0
            player.total_rice_amount = 0

            for city_id in player.city_list:
                city = game_mgr.unit_mgr.get_unit(city_id)
                player.total_money_amount += city.money_amount.value
                player.total_rice_amount += city.rice_amount.value
        
        # 完成，刷新界面
        game_mgr.event_mgr.emit(MAINUI_REFRESH)

    # 创建队伍
    def create_troop(self, city_unit, hero_list, x,y,z, army_amount):
        # 主将
        chief_hero_id = 0
        for item in hero_list:
            if item.pos_index == 5:
                chief_hero_id = item.hero_id
                break
            elif chief_hero_id == 0:
                chief_hero_id = item.hero_id

        troop = game_mgr.unit_mgr.create_troop()
        troop.hero_list = hero_list
        troop.owner_city_id = city_unit.unit_id
        troop.owner_player_id = city_unit.owner_player_id
        troop.army_amount = army_amount
        troop.set_position(x,y,z)

        if chief_hero_id > 0:
            troop.chief_hero_id = chief_hero_id
            troop.unit_name = f'{get_unit_name(chief_hero_id)}军'

        return troop



