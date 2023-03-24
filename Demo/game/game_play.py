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

        def in_range(x, min, max):
            return x >= min and x < max

        # 默认创建一个空城
        def co_choose_base_city():
            player = pm.main_player
            player.player_name = '刘备'
            
            while True:
                city = game_mgr.unit_mgr.find_unit(lambda x:
                        x.unit_type == UT_CITY and \
                        x.unit_id > 10020 and \
                        x.model_type == 2 and \
                        in_range(x.get_x(), -300, 300) and \
                        in_range(x.get_z(), -300, 300) and \
                        x.owner_player_id == 0)

                if city:
                    city.unit_name = '安喜'
                    self.set_city_owner(city, player)
                    player.main_city_id = city.unit_id

                    # 还要创建一个自己
                    hero = game_mgr.hero_mgr.new_hero()
                    hero.hero_name = player.player_name
                    hero.owner_player_id = player.player_id
                    hero.owner_city_id = city.unit_id
                    player.main_hero_id = hero.hero_id
                    player.hero_list.append(hero.hero_id)

                    city.hero_list.append(hero.hero_id)
                    city.get_controller().set_flag_color()
                    cm.set_target_focus(*city.get_position())
                    cm.update_camera()
                    for hero_id in city.hero_list:
                        player.hero_list.append(hero_id)

                    break

                yield None

            yield None
            game_mgr.event_mgr.emit(MAIN_PLAYER_READY)

        # 等地图加载好,弹一个选择框,然后在分配城
        def co_wait_for_ground():
            yield None

            # 到达之后, 显示一段对话
            def co_show_dialog():
                yield WaitForSeconds(1.5)

                dlg = game_mgr.ui_mgr.npc_dialog_controller
                dlg.init('大哥, 此处虽小, 只要用心经营, 未必不能有一番作为.', 3)

            # 游戏的第一个选择
            def confirm_start_option(index):
                # TODO: 这里要根据选项做一些区别对待
                if index == 0:
                    dlg = game_mgr.ui_mgr.npc_dialog_controller
                    dlg.init('大哥, 你在开玩笑?', 10)
                    return True

                log_debug('select', index)
                game_mgr.co_mgr.start(co_choose_base_city())
                game_mgr.ui_mgr.show_base_ui(True)
                game_mgr.co_mgr.start(co_show_dialog())

            def show_start_options():
                dlg = game_mgr.ui_mgr.option_panel_controller
                dlg.init('  朝廷安抚平乱有功者, 因此你除授定州安喜县令, 克日赴任. 你将作何选择?',
                        ['遣散队伍回乡务农', '率众投军继续当兵', '听从安排上任县令'],
                        confirm_start_option)
                dlg.push_panel()

            game_mgr.ui_mgr.show_base_ui(False)
            game_mgr.ui_mgr.story_panel_controller.play_story(
                    game_mgr.config_mgr.story.start_game_story,
                    show_start_options)

        log_util.debug('create main player')
        pm.main_player = pm.new_player()
        game_mgr.co_mgr.start(co_wait_for_ground())
        test_wait_1()

        # load cursor
        if not OS.is_editor_hint():
            #cursor = OS.load_resource('res://Cursor.png')
            #OS.set_custom_mouse_cursor(cursor, 0, 1, 1)
            pass

    def on_player_ready(self):
        mp = game_mgr.player_mgr.main_player
        log_debug('on_player_ready')

        self.refresh_player_resource(0)

        city_count = len([x for x in game_mgr.unit_mgr.each_city()])
        log_debug('city count =', city_count)

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
    def create_troop(self, city_unit, hero_list, x,y,z, army_amount, model_type):
        # 主将
        chief_hero_id = 0
        for item in hero_list:
            if item.pos_index == 4:
                chief_hero_id = item.hero_id
                break
            elif chief_hero_id == 0:
                chief_hero_id = item.hero_id

        troop = game_mgr.unit_mgr.create_troop()
        
        troop.hero_list = hero_list
        troop.owner_city_id = city_unit.unit_id
        troop.owner_player_id = city_unit.owner_player_id
        troop.army_amount = army_amount
        troop.model_type = model_type
        troop.set_position(x,y,z)

        # 军队的名字, 跟随主将
        troop.chief_hero_id = chief_hero_id
        if chief_hero_id > 0:
            troop.unit_name = f'{get_hero_name(chief_hero_id)}军'
        else:
            troop.unit_name = f'{city_unit.unit_name}军'

        #log_debug('create troop', troop.unit_id, troop.unit_name)
        return troop



