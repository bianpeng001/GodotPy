#
# 2023年2月8日 bianpeng
#

from game.core import *
from game.game_mgr import *

# 一个HUD，封装一下，关联unit_id，和UI元素
class HUDItem:
    def __init__(self):
        self.unit_id = 0

        self.hud_obj = None
        self.title_obj = None
        self.hp_obj = None

    def update(self):
        unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        if unit:
            x,y,z=unit.get_position()
            x1, y1 = get_main_camera().world_to_screen(x,y+8,z)
            self.hud_obj.set_position(x1-40, y1+36)

    def set_visible(self, Value):
        self.hud_obj.set_visible(Value)

    def set_text(self, text):
        self.title_obj.set_text(text)

    def set_flag_text(self, text):
        self.hud_obj.find_node('FlagLabel').set_text(text)

    def set_flag_color(self, r,g,b):
        self.hud_obj.find_node('Flag').set_self_modulate(r,g,b)

# HUD的显示，刷新
# 只分配已经在视野里面的，因为总体数量过于庞大，只在视野里面的，
# 数量应该是可以控制的
class HUDMgr:
    def __init__(self):
        self.is_show = True
        self.hud_root_obj = None
        self.template_obj = None
        self.title_obj = None
        self.hp_obj = None

        # 缓存起来，永不销毁，尤其是 self.template_obj
        self.hud_item_cache = []
        self.hud_item_dict = {}

    def setup(self):
        self.hud_root_obj = game_mgr.scene_root_obj.find_node('HUDRoot')

    def update(self, delta_time):
        for item in self.hud_item_dict.values():
            item.update()

    def show(self):
        self.is_show = True
        self.hud_root_obj.set_visible(True)

    def hide(self):
        self.is_show = False
        self.hud_root_obj.set_visible(False)

    def get_hud(self, unit_id):
        return self.hud_item_dict.get(unit_id, None)

    def create_hud(self, unit_id):
        item = HUDItem()
        
        if self.template_obj:
            item.hud_obj = self.template_obj.dup()
        else:
            self.template_obj = FNode3D.instantiate('res://ui/HUD.tscn')
            self.template_obj.reparent(self.hud_root_obj)
            item.hud_obj = self.template_obj

        item.title_obj = item.hud_obj.find_node('Title')
        item.hp_obj = item.hud_obj.find_node('HP')

        item.unit_id = unit_id
        # unit = game_mgr.unit_mgr.get_unit(unit_id)
        # item.set_text(unit.unit_name)
        # if unit.owner_player_id != 0:
        #     player = game_mgr.player_mgr.get_player(unit.owner_player_id)
        #     item.set_flag_text(player.player_name[0])
        item.set_text(get_unit_name(unit_id))
        item.set_visible(True)

        self.hud_item_dict[unit_id] = item
        item.update()

    def free_hud(self, unit_id):
        if unit_id in self.hud_item_dict:
            item = self.hud_item_dict.pop(unit_id)
            self.hud_item_cache.append(item)


