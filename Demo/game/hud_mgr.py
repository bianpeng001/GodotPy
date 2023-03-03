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

    def update(self):
        unit = game_mgr.unit_mgr.get_unit(self.unit_id)
        if unit:
            x, y = get_main_camera().world_to_screen(*unit.get_position())
            self.hud_obj.set_position(x, y)

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
        self.hud_item_list = []

    def setup(self):
        self.hud_root_obj = game_mgr.scene_root_obj.find_node('HUDRoot')

    def update(self, delta_time):
        for item in self.hud_item_list:
            item.update()

    def show(self):
        self.is_show = True
        self.hud_root_obj.set_visible(True)

    def hide(self):
        self.is_show = False
        self.hud_root_obj.set_visible(False)

    def create_hud(self, unit_id):
        item = HUDItem()
        item.unit_id = unit_id
        if self.template_obj:
            item.hud_obj = self.template_obj.dup()
        else:
            self.template_obj = FNode3D.instantiate('res://ui/HUD.tscn')
            self.template_obj.reparent(self.hud_root_obj)
            item.hud_obj = self.template_obj

        item.title_obj = item.hud_obj.find_node('Title')
        item.hp_obj = item.hud_obj.find_node('HP')
        item.hud_obj.set_visible(True)
        item.title_obj.set_text(game_mgr.unit_mgr.get_unit(unit_id).unit_name)

        self.hud_item_list.append(item)
        item.update()

