#
# 2023年2月10日 bianpeng
#
import os
import os.path
import json

from game.core import *
from game.game_mgr import *
from game.base_type import *
from game.event_name import *
from game.wait import *

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

        def in_range(x, min, max):
            return x >= min and x < max
        
        def co_create_robot_player():
            while not pm.main_player:
                yield
                
            main_city_unit = get_unit(get_main_player().main_city_id)
            x1,z1 = main_city_unit.get_xz()
            
            player_count = 0
            for i in range(60):
                city_unit = game_mgr.unit_mgr.find_unit(lambda x:
                        x.unit_type == UT_CITY and \
                        in_range(x.get_x()-x1, -200, 200) and \
                        in_range(x.get_z()-z1, -200, 200) and \
                        x.owner_player_id == 0)
                if city_unit:
                    player = self.create_player(city_unit,
                            player_name=None,
                            set_main_player=False)
                    log_debug('create robot player', player.player_name, city_unit.unit_name)
                    player_count += 1

            log_debug('create', player_count, 'robot players')

        # 默认创建一个空城
        def co_create_main_player(player_name):
            yield
            
            while True:
                yield
                
                # 找一个合适的城市, 改一下名字
                # 或者找一个空地, 新建一个城
                city_unit = game_mgr.unit_mgr.find_unit(lambda x:
                        x.unit_type == UT_CITY and \
                        x.unit_id > 10020 and \
                        in_range(x.get_x(), -120, 120) and \
                        in_range(x.get_z(), -120, 120) and \
                        x.owner_player_id == 0)

                if city_unit:
                    city_unit.unit_name = game_mgr.config_mgr.first_city_name
                    
                    # 这个后面看看咋办, 主要是要替换模型
                    city_unit.city_type = CT_XIAN
                    if city_unit.model_node:
                        city_unit.model_node.destroy()
                        city_unit.model_node = None
                        city_unit.load_model()
                    
                    player = self.create_player(
                            city_unit,
                            player_name=player_name,
                            set_main_player=True)
                    
                    hero = player.get_main_hero()
                    hero.set_age(15+int(random_1()*20))
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
            while not (game_mgr.ui_mgr.load_complete and \
                        game_mgr.ground_mgr.load_complete):
                yield
                
            city_name = game_mgr.config_mgr.first_city_name

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
                dlg.init(f'朝廷安抚平乱有功者, 因此你获授{city_name}县令, 将作何打算?',
                        ['遣散队伍回乡务农', '率众投军继续当兵', '听从安排克日赴任'],
                        confirm_start_option)
                dlg.show()

            def on_create_player(player_name):
                log_util.debug('create main player')
                ctx_data['player_name'] = player_name
                game_mgr.ui_mgr.story_panel_controller.play_story(
                    game_mgr.config_mgr.story.start_game_story,
                    show_start_options)

            def co_story1():
                dlg1 = game_mgr.ui_mgr.story_panel_controller
                dlg2 = game_mgr.ui_mgr.npc_dialog_controller
                dlg3 = game_mgr.ui_mgr.create_player_controller
                
                game_mgr.ui_mgr.show_base_ui(False)
                yield 1.0

                dlg1.init()
                dlg1.show_text('大江东去, 浪淘尽, 千古风流人物\n江山如画, 一时多少豪杰')
                yield 3.0
                dlg1.defer_close()
                yield WaitForSeconds(2)
                
                dlg1.init()
                dlg1.show_text('有一天, 我在街上闲逛')
                yield WaitForSeconds(1.5)
                dlg1.show_text('看人来人往, 潮起潮落')
                yield WaitForSeconds(1.5)
                dlg1.show_text('不禁放慢了脚步, 暗暗发愁晚饭还没着落')
                yield WaitForSeconds(1.5)
                dlg1.show_text('突然, 斜里过来一人, 一把将我拽住')
                yield WaitForSeconds(1.5)
                dlg1.defer_close()
                
                dlg2.init()
                dlg2.show_text2("陌生人", "兄台请留步")
                yield WaitForSeconds(1.5)
                dlg2.show_text2("我", "干啥, 我可没钱")
                yield WaitForSeconds(1.5)
                dlg2.show_text2("陌生人", "兄台取笑了, 不是问你要钱, 是给你钱!")
                yield WaitForSeconds(1.5)
                dlg2.show_text2("我", "还有这好事?")
                yield WaitForSeconds(1.5)
                dlg2.show_text2("陌生人", "未请教尊姓大名?")
                yield WaitForSeconds(1.5)
                dlg2.defer_close()
                
                dlg3.show_dialog()
                yield WaitForClose(dlg3)
                player_name = dlg3.player_name
                
                dlg2.init()
                dlg2.show_text2("陌生人", "久仰, 久仰. 是这样, 我这有个活, 包吃包住")
                yield WaitForSeconds(1.5)
                dlg2.show_text2(player_name, "真的吗?")
                yield 1.5
                dlg2.show_text2("陌生人", "我看你步履稳健, 气度不凡, 头顶一道英雄气直贯云天, 不得了, 不得了")
                yield 2.5
                dlg2.show_text2(player_name, "骗小孩呢? 有事说事, 别耽误我散步")
                yield 2.5
                dlg2.show_text2("陌生人", "...这个, 眼下虽然时运不济, 他日风云际会, 必定一飞冲天!")
                yield 2.5
                dlg2.show_text2("陌生人", "如今朝廷正在用人之际, 我推荐你到军中效力, 总好过在乡野埋没")
                yield 2.5
                dlg2.show_text2(player_name, "好像有点道理")
                yield 1.5
                dlg2.defer_close()
                
                dlg1.init()
                dlg1.show_text('这就是我被拉壮丁的经过')
                yield WaitForSeconds(1.5)
                dlg1.show_text('然后我结识了几个兄弟, 一起出生入死')
                yield WaitForSeconds(1.5)
                dlg1.show_text('我们几个武功还可以, 加上运气不错')
                yield WaitForSeconds(1.5)
                dlg1.show_text('没在某场战斗里, 被箭射死, 被刀砍死, 被马踩死, 落河淹死...')
                yield WaitForSeconds(2.5)
                dlg1.show_text('再后来, 仗打完了')
                yield WaitForSeconds(1.5)
                dlg1.show_text('我跟两位兄弟, 被安排来此处当了个普通县尉')
                yield WaitForSeconds(1.5)
                dlg1.show_text('故事从这里开始')
                yield WaitForSeconds(2.5)
                dlg1.defer_close()
                
                game_mgr.co_mgr.start(co_create_main_player(player_name))
                game_mgr.co_mgr.start(co_create_robot_player())
                yield
                
                dlg1.init()
                dlg1.show_chapter(f'第一回 赴任{city_name}')
                yield WaitForSeconds(2.5)
                dlg1.defer_close()
                
                dlg2.init()
                dlg2.show_text2("关羽", "如今各处刚历经兵乱, 此处虽小, 也可以励精图治")
                yield WaitForSeconds(1.5)
                dlg2.show_text2("张飞", "大哥, 先看下城里的[color=red]内政[/color]情况吧")
                yield WaitForSeconds(1.5)
                dlg2.show_text2(player_name, "好, 往后这就是我们的家了!")
                yield WaitForSeconds(1.5)
                dlg2.defer_close()
                
                dlg1.init()
                dlg1.show_text('三人读书练武勤于政务, 于百姓秋毫无犯, 日子倒也快活')
                yield WaitForSeconds(2.5)
                dlg1.defer_close()
                
                game_mgr.ui_mgr.show_base_ui(True)

                game_mgr.event_mgr.emit(MSG_PANEL_NEW_MSG, f"[color=red]{player_name}[/color]一行进入[color=green]{city_name}[/color]城")
            
            game_mgr.co_mgr.start(co_story1())
        game_mgr.co_mgr.start(co_wait_for_ground())

        test_wait_1()
        
        # load cursor
        self.cursor_list = [
            None,
            ResCapsule.load_resource(game_mgr.config_mgr.default_cursor),
            ResCapsule.load_resource(game_mgr.config_mgr.drag_cursor),
        ]
        self.set_cursor(1)

    def set_cursor(self, index:int):
        #OS.set_custom_mouse_cursor(None, 0, 0, 0)
        OS.set_custom_mouse_cursor(
                self.cursor_list[index].res if index > 0 else None,
                0, 2, 2)

    def on_player_ready(self) -> None:
        player = game_mgr.player_mgr.main_player
        log_debug('on_player_ready', player.player_name)
        
        self.refresh_player_resource(0)
        
        city_count = len(list(game_mgr.unit_mgr.loop_cities()))
        log_debug('create', city_count, 'cities')

    # 离开场景前, 需要做一些清理. 这个引擎还是有一些小瑕疵的, 这些问题有待解决.
    # 确保资源清理干净, 是一个优秀引擎的基本要求. 
    # 因此, godot离优秀, 还差那么一点点. 而我的游戏, 离优秀还差不止一点点.
    # 秉承严于律己, 宽以待人. 感谢godot已经做了很多, 我们自己做一点点清理, 也不算过.
    def on_leave_scene(self):
        game_mgr.event_mgr.emit(LEAVE_SCENE)
        
        # 这是要清理surface material override
        # 不然就有报错, 所以, 虽然不太合理,但还是可以做一下
        for city in game_mgr.unit_mgr.loop_cities():
            if city.model_node:
                flag_node = city.model_node.find_node('Flag')
                if flag_node:
                    flag_node.set_surface_material(0, None)
                    flag_node.set_surface_material(1, None)
        
        # 清理tile
        for tile in game_mgr.ground_mgr.loop_tiles():
            tile.unload()
            
        # 清理角色
        for player in game_mgr.player_mgr.loop_players():
            player.on_leave_scene()
        
        # reset cursor, othewise when exit app the console report leak error of the cursor texture2d asset
        self.cursor_list = None
        self.set_cursor(0)
        #OS.set_custom_mouse_cursor(None, 0, 1, 1)
        
    # API方法，业务代码

    # 修改城城池归属
    def set_city_owner(self, city, player):
        if city.owner_player_id == player.player_id:
            log_util.error(f'player already own the city {player.player_id} -> {city.unit_name}')
            return

        if city.owner_player_id > 0:
            owner = game_mgr.player_mgr.get_player(city.owner_player_id)
            owner.city_list.remove(city.unit_id)
            game_mgr.event_mgr.emit(NAV_PANEL_LOSE_UNIT, owner.player_id, city.unit_id)
            city.owner_player_id = 0
            
        city.owner_player_id = player.player_id
        player.city_list.append(city.unit_id)
        game_mgr.event_mgr.emit(NAV_PANEL_ADD_UNIT, player.player_id, city.unit_id)
        # 城内武将的归属
        # TODO: 城中的武将的归属,现在做成直接归属. 以后做成俘虏
        for hero_id in city.hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)
            hero.owner_player_id = player.player_id
            player.hero_list.append(hero)

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

    def update(self, delta_time:float) -> None:
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

            # 完成，刷新界面
            game_mgr.event_mgr.emit(MAINUI_REFRESH)

    # 刷新所有的资源增长, 这个开销也不大
    # delta_time: 间隔时长，单位秒
    def refresh_player_resource(self, delta_time:float) -> None:
        for city_unit in game_mgr.unit_mgr.loop_cities():
            city_unit.get_controller().refresh_resource_amount(delta_time)
        
        for player in game_mgr.player_mgr.loop_players():
            # 刷新资源
            total_money_amount = 0
            total_rice_amount = 0
            
            for city_id in player.city_list:
                city_unit = get_unit(city_id)
                total_money_amount += city_unit.money_amount.value
                total_rice_amount += city_unit.rice_amount.value
                
            player.total_money_amount = total_money_amount
            player.total_rice_amount = total_rice_amount

            # 刷新武将体力
            ap_growth_speed = game_mgr.config_mgr.ap_growth_speed
            for hero in player.hero_list:
                hero.ap.grow(ap_growth_speed,delta_time)


    # 解散队伍, 一般是进城, 或者被击溃
    # 如果是进城, 注意回收队伍中的武将, 士兵, 资源
    def remove_troop(self, troop_unit):
        pass
        
    # 创建队伍
    def create_troop(self,
            city_unit:object,
            hero_list:[object],
            x:float,y:float,z:float,
            army_amount:int,
            model_type:int) -> object:
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

        # 加入到troop_list里面
        player = get_player(troop.owner_player_id)
        player.troop_list.append(troop)

        # 军队的名字, 跟随主将
        if chief_hero_id > 0:
            troop.unit_name = f'{get_hero_name(chief_hero_id)}部'
            troop.chief_hero_id = chief_hero_id
        else:
            troop.unit_name = f'{city_unit.unit_name}军'
            troop.chief_hero_id = 0

        log_debug('create troop', troop.unit_id, troop.unit_name)

        game_mgr.event_mgr.emit(NAV_PANEL_ADD_UNIT, troop.owner_player_id, troop.unit_id)

        return troop

    #
    # 释放技能, 伤害结算. 目前这个是伤害的唯一方式
    #
    def cast_skill(self, skill_config_id:int, src_unit, target_unit) -> int:
        cfg = get_skill_config(skill_config_id)
        
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
            log_debug('skill damage', damage, 'remain', hp)
            # 如果目标被击败了
            if hp <= 0:
                self.defeat(src_unit, target_unit)
        
        # 释放一个技能, 传入一个结束回调
        game_mgr.skill_mgr.cast_skill(skill_config_id, on_complete)

        return 0

    # 击败
    def defeat(self, src_unit, target_unit) -> int:
        if target_unit.unit_type == UT_CITY:
            self.occupy_city(src_unit, target_unit)
            game_mgr.event_mgr.emit(MSG_PANEL_NEW_MSG, f"[color=red]{src_unit.unit_name}[/color]占领[color=green]{target_unit.unit_name}[/color]")
            
        return 0
    
    # 占领
    def occupy_city(self, src_unit, city_unit) -> int:
        log_debug('occupy', src_unit.unit_name, city_unit.unit_name)
        if city_unit.owner_player_id != 0:
            player = get_player(city_unit.owner_player_id)
            # TODO: 转移到最近的城, 如果城丢光了, 就算灭了
            pass
        
        if src_unit.owner_player_id != 0:
            player = get_player(src_unit.owner_player_id)
            self.set_city_owner(city_unit, player)
            controller = city_unit.get_controller()
            controller.get_hud_comp().set_valid(False)
            controller.set_flag_color()
            
        return 0

    # 在城里, 创建一个玩家
    def create_player(self,
            city_unit:object,
            player_name:str = None,
            set_main_player:bool = False) -> object:
        pm = game_mgr.player_mgr

        if player_name:
            game_mgr.hero_mgr.rename_hero(player_name)
        else:
            player_name = game_mgr.hero_mgr.gen_unique_hero_name()

        player = pm.new_player()
        player.player_name = player_name
        player.first_name = player_name[0]
        if set_main_player and not get_main_player():
            pm.set_main_player(player)
        
        # 玩家自己对应的武将
        hero = game_mgr.hero_mgr.new_hero()
        game_mgr.hero_mgr.rename_hero(player_name, hero)
        
        # 武将的从属
        hero.owner_player_id = player.player_id
        player.main_hero_id = hero.hero_id
        player.hero_list.append(hero)
        
        # 城市的从属
        self.set_city_owner(city_unit, player)
        player.main_city_id = city_unit.unit_id
        hero.owner_city_id = city_unit.unit_id
        city_unit.hero_list.insert(0, hero.hero_id)
        city_unit.satrap = hero.hero_id

        city_unit.get_controller().set_flag_color()

        return player

    def remove_player(self, player):
        pass


    
        
