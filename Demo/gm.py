import importlib

#import game.ui.npc_dialog_controller
#importlib.reload(game.ui.npc_dialog_controller)

from game.game_mgr import *
from game.config_mgr import new_hero_name
from game.core import *

main_camera = game_mgr.camera_mgr.main_camera

#dust = main_camera.find_node('/root/MainScene/Dust01')
#print(dust)

#game_mgr.enable_city_ai = True

#print(ui_mgr.build_panel_controller.is_visible)

def show_story():
    pass

#game_mgr.ui_mgr.story_panel_controller.play_story(['请主公指示'])
# game_mgr.ui_mgr.story_panel_controller.play_story([
#     '滚滚长江东逝水，浪花淘尽英雄。',
#     '是非成败转头空。',
#     '青山依旧在，几度夕阳红。',
#     '白发渔樵江渚上，惯看秋月春风。',
#     '一壶浊酒喜相逢。',
#     '古今多少事，都付笑谈中。',
# ])

# game_mgr.ui_mgr.story_panel_controller.play_story(
#     game_mgr.config_mgr.story.start_game_story)

def trigger_mainui():
    ui_mgr = game_mgr.ui_mgr
    show = not ui_mgr.mainui_controller.is_show()
    ui_mgr.show_base_ui(show)

#trigger_mainui()

def fix_config():
    config_mgr = game_mgr.config_mgr
    config_mgr.rvo_factor = 0.3

#fix_config()

def play_effect():
    effect_item = game_mgr.effect_mgr.play_effect2(2001)
    x,y,z = game_mgr.camera_mgr.get_focus_xyz()
    effect_item.set_position(x,y,z)

#play_effect()

def test_pos():
    #unit1 = game_mgr.unit_mgr.get_unit_by_name('王世玉部')
    unit2 = game_mgr.unit_mgr.get_unit_by_name('安喜')

    #print(unit1.get_position())
    print(unit2.get_position())
    
    x,z = unit2.get_xz()
    tile = game_mgr.ground_mgr.get_tile(x,z)
    for unit in tile.get_unit_list():
        print(unit.unit_name, unit.get_position())

#test_pos()

def test_damage():
    unit1 = game_mgr.unit_mgr.get_unit_by_name('安喜')
    if unit1:
        game_mgr.effect_mgr.play_damage(1234, unit1)

test_damage()

# 创建一个诸侯, 拥有一个城
def create_player(city_name1):
    city_unit = game_mgr.unit_mgr.get_unit_by_name(city_name1)
    player = game_mgr.game_play.create_player(city_unit)

#create_player()

#print(hsv_to_rgb(1,1,1))

def show_npc_dialog():
    dlg2 = game_mgr.ui_mgr.npc_dialog_controller
    if dlg2.is_show():
        dlg2.defer_close()
    else:
        dlg2.init()
        dlg2.show_text2("诸葛亮", "窗外日迟迟")

#show_npc_dialog()


def show_troop_detail():
    # for unit in game_mgr.unit_mgr.unit_dict.values():
    #     if unit.unit_name == '程秉部':
    #         print(unit.unit_id)
    #         print(unit.unit_name)
    
    unit = get_main_player().troop_list[0]
    #unit = get_unit(10281)
    print(unit.unit_name)
    controller = unit.get_controller()
    sight_comp = controller.sight_comp
    for unit in sight_comp._unit_dict.values():
        print(unit.unit_name)

    #print('rvo', controller.rvo_acce_x, controller.rvo_acce_z)
    print(controller.move_comp.block_time)

#show_troop_detail()


def show_scroll_bar():
    panel = game_mgr.ui_mgr.msg_panel_controller
    print(panel.vbar.get_value())


show_scroll_bar()


