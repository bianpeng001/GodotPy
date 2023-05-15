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
from game.base_type import *
from game.config_mgr import parse_name, new_hero_name

#
# 游戏的控制逻辑, 事件响应啥的，集中到这里来
# 业务逻辑也放到这里来，脏活累活都放这
# 有一些业务逻辑是好几个单位相互作用的
#
class GamePlay:
    def __init__(self):
        # init sub systems
        from game.config_mgr import ConfigMgr
        from game.player_mgr import PlayerMgr
        from game.hero_mgr import HeroMgr
        from game.unit_mgr import UnitMgr
        from game.skill_mgr import SkillMgr
        from game.effect_mgr import EffectMgr
        from game.hud_mgr import HUDMgr
        from game.game_data import GameData
        
        game_mgr.player_mgr = PlayerMgr()
        game_mgr.hero_mgr = HeroMgr()
        game_mgr.unit_mgr = UnitMgr()
        game_mgr.effect_mgr = EffectMgr()
        game_mgr.game_data = GameData()
        game_mgr.config_mgr = ConfigMgr()
        game_mgr.hud_mgr = HUDMgr()
        game_mgr.skill_mgr = SkillMgr()

        game_mgr.hud_mgr.setup()
        
        # 资源刷新tick
        self.data_tick_time = 0

        # 处理事件
        game_mgr.event_mgr.add(APP_LAUNCH, self.on_app_launch)
        game_mgr.event_mgr.add(START_GAME, self.on_start_game)
        game_mgr.event_mgr.add(MAIN_PLAYER_READY, self.on_player_ready)
        
    # 事件
    def on_app_launch(self):
        log_util.debug('on_app_launch')
        game_mgr.init_update_list()
        game_mgr.ground_mgr.load_data()

        # restore saved window position
        if os.path.exists('launch.json'):
            with open('launch.json', 'r') as f:
                obj = json.load(f)
                OS.set_window_rect(*obj['window'])

        # 标题
        OS.set_window_title(game_mgr.config_mgr.app_title)

        # 起始块, 不加载物件，因为这块可能会有一些特效残留的bug，
        # 弄一个建筑物挡一挡，毕竟是天下之中
        tile, _ = game_mgr.ground_mgr.create_tile(0, 0)
        tile.load()

    # create main player
    def on_start_game(self):
        pm = game_mgr.player_mgr
        cm = game_mgr.camera_mgr
        cm.update_camera()
        
        # 记录一些数据
        ctx_data = {}

        def in_range(x, min, max):
            return x >= min and x < max
        
        def co_create_robot_player():
            while not pm.main_player:
                yield None
                
            for i in range(30):
                yield None
                city_unit = game_mgr.unit_mgr.find_unit(lambda x:
                        x.unit_type == UT_CITY and \
                        in_range(x.get_x(), -120, 120) and \
                        in_range(x.get_z(), -120, 120) and \
                        x.owner_player_id == 0)
                if city_unit:
                    player = self.create_player(city_unit,
                            player_name=None,
                            is_main_player=False)
                    player.flag_color = (random_1(), 0.4, 1)
                    log_debug('create player', player.player_name, city_unit.unit_name)

        # 默认创建一个空城
        def co_create_main_player():
            while True:
                yield None
                
                # 找一个合适的城市, 改一下名字
                # 或者找一个空地, 新建一个城
                city_unit = game_mgr.unit_mgr.find_unit(lambda x:
                        x.unit_type == UT_CITY and \
                        x.unit_id > 10020 and \
                        in_range(x.get_x(), -120, 120) and \
                        in_range(x.get_z(), -120, 120) and \
                        x.owner_player_id == 0)

                if city_unit:
                    city_unit.unit_name = '安喜'
                    
                    # 这个后面看看咋办, 主要是要替换模型
                    if city_unit.city_type != CT_XIAN:
                        city_unit.city_type = CT_XIAN
                        if city_unit.model_node:
                            city_unit.model_node.destroy()
                            city_unit.model_node = None
                            city_unit.load_model()
                    
                    player = self.create_player(city_unit,
                            player_name=ctx_data['player_name'],
                            is_main_player=True)
                    
                    player.flag_color = (1, 0, 0)
                    pm.main_player = player
                    
                    #hero = get_hero(player.main_hero_id)
                    hero = player.get_main_hero()
                    hero.set_age(28)
                    hero.attr[2] = 88
                    hero.attr[4] = 88

                    # 旗帜颜色
                    city_unit.get_controller().set_flag_color()
                    # 镜头
                    cm.set_target_focus(*city_unit.get_position())
                    cm.update_camera()

                    break

            game_mgr.event_mgr.emit(MAIN_PLAYER_READY)
            
        
        def co_wait_for_ground():
            # 等地图和ui加载好,然后分配一个新手城
            while not game_mgr.ui_mgr.load_complete or \
                        not game_mgr.ground_mgr.load_complete:
                yield None
            
            # 到达之后, 显示一段对话
            def co_show_dialog():
                yield WaitForSeconds(2.5)
                
                yield game_mgr.co_mgr.start(co_show_chapter('第一回 治理安喜'))

                dlg = game_mgr.ui_mgr.npc_dialog_controller
                dlg.init('现在各地经历兵乱, 破坏凋敝. 此处虽小, 只要用心经营, 也是个安身立命之处.', 2)
                yield WaitForSeconds(2.5)
                dlg.init('不错, 安喜虽小, 不妨碍我们励精图治.', 2)
                yield WaitForSeconds(2.5)
                dlg.init('大哥, 先看下城里的[color=red]内政[/color]情况吧.', 2)
                yield WaitForSeconds(2.5)
                game_mgr.ui_mgr.show_base_ui(True)

            # 游戏的第一个选择
            def confirm_start_option(index):
                # TODO: 这里要根据选项做一些区别对待
                if index == 0:
                    dlg = game_mgr.ui_mgr.npc_dialog_controller
                    dlg.init('认真点, 别开玩笑', 3)
                    return True

                log_debug('select', index)
                game_mgr.co_mgr.start(co_create_main_player())
                game_mgr.co_mgr.start(co_create_robot_player())
                game_mgr.co_mgr.start(co_show_dialog())

            def show_start_options():
                dlg = game_mgr.ui_mgr.option_panel_controller
                dlg.init('朝廷安抚平乱有功者, 因此你除授定州安喜县令, 你将作何打算?',
                        ['遣散队伍回乡务农', '率众投军继续当兵', '听从安排克日赴任'],
                        confirm_start_option)
                dlg.push_panel()

            def on_create_player(player_name):
                log_util.debug('create main player')
                ctx_data['player_name'] = player_name
                game_mgr.ui_mgr.story_panel_controller.play_story(
                    game_mgr.config_mgr.story.start_game_story,
                    show_start_options)

            game_mgr.ui_mgr.show_base_ui(False)
            game_mgr.ui_mgr.create_player_controller.show_dialog(on_create_player)
    
        game_mgr.co_mgr.start(co_wait_for_ground())

        test_wait_1()
        
        # load cursor
        self.cursor_list = [
            None,
            ResCapsule.load_resource(game_mgr.config_mgr.default_cursor),
            ResCapsule.load_resource(game_mgr.config_mgr.drag_cursor),
        ]
        self.set_cursor(1)

    def set_cursor(self, index):
        #OS.set_custom_mouse_cursor(None, 0, 0, 0)
        if index > 0:
            OS.set_custom_mouse_cursor(self.cursor_list[index].res, 0, 1, 1)

    def on_player_ready(self):
        mp = game_mgr.player_mgr.main_player
        log_debug('on_player_ready')
        
        self.refresh_player_resource(0)
        
        city_count = len(list(game_mgr.unit_mgr.loop_cities()))
        log_debug('city count =', city_count)

    # 离开场景前, 需要做一些清理. 这个引擎还是有一些小瑕疵的, 这些问题有待解决.
    # 确保资源清理干净, 是一个优秀引擎的基本要求. 
    # 因此, godot离优秀, 还差那么一点点. 而我的游戏, 离优秀还差不止一点点.
    # 秉承严于律己, 宽以待人. 感谢godot已经做了很多, 我们自己做一点点清理, 也不算过.
    def on_leave_scene(self):
        # 这是要清理surface material override
        # 不然就有报错, 所以, 虽然不太合理,但还是可以做一下
        for city in game_mgr.unit_mgr.loop_cities():
            if city.model_node:
                flag_node = city.model_node.find_node('Flag')
                if flag_node:
                    flag_node.set_surface_material(0, None)
                    flag_node.set_surface_material(1, None)
        
        game_mgr.ui_mgr.cmd_panel_controller.on_leave_scene()

        # 清理tile
        for tile in game_mgr.ground_mgr.loop_tiles():
            tile.unload()
            
        # 清理角色
        for player in game_mgr.player_mgr.loop_players():
            player.on_leave_scene()
        
        # reset cursor, othewise when exit app the console report leak error of the cursor texture2d asset
        self.cursor_list = None
        OS.set_custom_mouse_cursor(None, 0, 1, 1)
        
    # API方法，业务代码

    # 修改城城池归属
    def set_city_owner(self, city, player):
        if city.owner_player_id == player.player_id:
            log_util.error(f'player already own the city {player.player_id} -> {city.unit_name}')
            return

        if city.owner_player_id > 0:
            owner = game_mgr.player_mgr.get_player(city.owner_player_id)
            owner.city_list.remove(city.unit_id)
            game_mgr.event_mgr.emit(NAV_PANEL_LOSE_CITY, owner.player_id, city.unit_id)
            city.owner_player_id = 0
            
        city.owner_player_id = player.player_id
        player.city_list.append(city.unit_id)
        game_mgr.event_mgr.emit(NAV_PANEL_GAIN_CITY, player.player_id, city.unit_id)
        # 城内武将的归属
        # TODO: 城中的武将的归属,现在做成直接归属. 以后做成俘虏
        for hero_id in city.hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            hero.owner_player_id = player.player_id
            player.hero_list.append(hero_id)

    # 队伍攻城
    @obstacle
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
    # delta_time: 间隔时长，单位秒
    def refresh_player_resource(self, delta_time):
        for city in game_mgr.unit_mgr.loop_cities():
            city.get_controller().refresh_resource_amount(delta_time)
        
        for player in game_mgr.player_mgr.loop_players():
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
        troop.army_amount.value = army_amount
        troop.model_type = model_type
        troop.set_position(x,y,z)

        # 军队的名字, 跟随主将
        troop.chief_hero_id = chief_hero_id
        if chief_hero_id > 0:
            troop.unit_name = f'{get_hero_name(chief_hero_id)}部'
        else:
            troop.unit_name = f'{city_unit.unit_name}军'

        return troop
    
        #log_debug('create troop', troop.unit_id, troop.unit_name)

    #
    # 释放技能, 伤害结算. 目前这个是伤害的唯一方式
    #
    def cast_skill(self, skill_config_id, src_unit, target_unit):
        cfg = game_mgr.config_mgr.get_skill(skill_config_id)
        
        # 放特效
        effect_item = game_mgr.effect_mgr.play_effect3(src_unit.unit_id, cfg.effect_id)
        effect_item.set_position(*src_unit.get_position())
        effect_item.look_at(*target_unit.get_position())
        
        # 放技能名字的特效
        effect_item = game_mgr.effect_mgr.play_effect3(src_unit.unit_id, 2004)
        effect_item.attach_unit = target_unit
        #effect_item.set_text(cfg.skill_name)
        effect_item.set_text(game_mgr.config_mgr.get_skill_word())
        
        # 修改战斗单位
        src_controller = src_unit.get_controller()
        src_fight_comp = src_controller.get_fight_comp()
        src_fight_comp.skill_cooldown = cfg.cooldown
        
        def on_complete():
            # 结算伤害, 或者是等结束再结算?
            damage = game_mgr.config_mgr.calc_skill_damage(
                    skill_config_id,
                    src_unit,
                    target_unit)
            
            # 掉血飘字
            game_mgr.effect_mgr.play_damage(damage, target_unit)
            
            target_unit.army_amount.add(-damage)
            hp = target_unit.army_amount.get_value()
            log_debug('skill damage', damage, hp)
            # 如果目标被击败了
            if hp <= 0:
                self.defeat(src_unit, target_unit)
        
        # 释放一个技能, 传入一个结束回调
        game_mgr.skill_mgr.cast_skill(skill_config_id, on_complete)

    # 击败
    def defeat(self, src_unit, target_unit):
        if target_unit.unit_type == UT_CITY:
            self.occupy_city(src_unit, target_unit)
    
    # 占领
    def occupy_city(self, src_unit, city_unit):
        log_debug('occupy', src_unit.unit_name, city_unit.unit_name)
        if src_unit.owner_player_id != 0:
            player = game_mgr.player_mgr.get_player(src_unit.owner_player_id)
            self.set_city_owner(city_unit, player)
            controller = city_unit.get_controller()
            controller.get_hud_comp().set_valid(False)
            controller.set_flag_color()

    # 在城里, 创建一个玩家
    def create_player(self,
            city_unit,
            player_name=None,
            is_main_player=False):
        player_name = player_name or new_hero_name()
        pm = game_mgr.player_mgr
        
        player = pm.new_player()
        if is_main_player:
            pm.main_player = player
        player.player_name = player_name
        player.first_name = player_name[0]
        
        # 玩家自己对应的武将
        hero = game_mgr.hero_mgr.new_hero()
        hero.hero_name = player_name
        
        # 武将的从属
        hero.owner_player_id = player.player_id
        player.main_hero_id = hero.hero_id
        player.hero_list.append(hero.hero_id)
        
        # 城市的从属
        self.set_city_owner(city_unit, player)
        player.main_city_id = city_unit.unit_id
        hero.owner_city_id = city_unit.unit_id
        city_unit.hero_list.insert(0, hero.hero_id)
        city_unit.satrap = hero.hero_id
        
        return player


