#
# 2023年2月8日 bianpeng
#

from game.core import *
from game.game_mgr import *
from game.base_type import *

# 一个HUD，封装一下，关联unit_id，和UI元素
class HUDItem:
    def __init__(self):
        self.unit_id = 0

        self.unit_type = 0
        self.offset = -40

        self.hud_obj = None
        self.title_obj = None
        self.hp_obj = None
        
        # 可见度,加一个计数
        self.show_age = 1

    def set_visible(self, value):
        self.hud_obj.set_visible(value)

    def set_text(self, text):
        self.title_obj.set_text(text)

    def set_flag_text(self, text):
        label = self.hud_obj.find_node('FlagLabel')
        label.set_text(text)

    def set_flag_color(self, r,g,b):
        flag = self.hud_obj.find_node('Flag')
        flag.set_self_modulate(r,g,b)

    # new_hud 是否新创建的, 少刷新一些东西
    def update(self, unit, new_hud):
        if unit:
            x,y,z = unit.get_position()
            x1,y1 = get_main_camera().world_to_screen(x,y+8,z)
            self.hud_obj.set_position(x1+self.offset, y1)
            
            if new_hud:
                if unit.owner_player_id != 0:
                    player = game_mgr.player_mgr.get_player(unit.owner_player_id)
                    if player:
                        self.set_flag_text(player.player_name[0])
                        self.set_flag_color(*player.flag_color)
                    else:
                        pass
                else:
                    self.set_flag_text('')
                    self.set_flag_color(1,1,1)

# HUD的显示，刷新
# 只分配已经在视野里面的，因为总体数量过于庞大，只在视野里面的，
# 数量应该是可以控制的
class HUDMgr:
    def __init__(self):
        self.is_show = True
        self.hud_root_obj = None
        # 缓存起来，永不销毁，尤其是 self.template_obj
        self.hud_item_cache = []
        self.hud_item_dict = {}

        self.template_list = None
        # 需要隐藏的排队
        self.hide_queue = []

    def setup(self):
        self.hud_root_obj = game_mgr.scene_root_obj.find_node('HUDRoot')

    def update(self, delta_time):
        # for item in self.hud_item_dict.values():
        #     item.update()
        pass

    def show(self):
        self.is_show = True
        self.hud_root_obj.set_visible(True)

    def hide(self):
        self.is_show = False
        self.hud_root_obj.set_visible(False)

    def get_hud(self, unit_id):
        return self.hud_item_dict.get(unit_id, None)

    def _create_hud(self, unit):
        # load template
        if not self.template_list:
            self.template_list = [ None, None, None ]

            hud_obj = FNode3D.instantiate('res://ui/CityHUD.tscn')
            self.template_list[1] = hud_obj
            
            hud_obj = FNode3D.instantiate('res://ui/TroopHUD.tscn')
            self.template_list[2] = hud_obj
            
            for hud_obj in self.template_list:
                if hud_obj:
                    hud_obj.reparent(self.hud_root_obj)
                    hud_obj.set_visible(False)

        # create hud_item
        hud_item = None

        if len(self.hud_item_cache) > 0:
            index = -1
            for i in range(len(self.hud_item_cache)):
                if self.hud_item_cache[i].unit_type == unit.unit_type:
                    index = i
                    break

            if index >= 0:
                hud_item = self.hud_item_cache.pop(index)
                #log_debug('reuse hud item', len(self.hud_item_dict), len(self.hud_item_cache))

        if not hud_item:
            hud_item = HUDItem()
            hud_item.unit_type = unit.unit_type
            hud_item.hud_obj = self.template_list[hud_item.unit_type].dup()
            hud_item.title_obj = hud_item.hud_obj.find_node('Title')
            hud_item.hp_obj = hud_item.hud_obj.find_node('HP')

            if unit.unit_type == 2:
                hud_item.offset = -50
            else:
                hud_item.offset = -40

        #log_debug('create hud', unit.unit_id, unit.unit_name)
        hud_item.unit_id = unit.unit_id
        hud_item.set_text(unit.unit_name)
        hud_item.set_visible(True)
        hud_item.show_age = 1

        self.hud_item_dict[hud_item.unit_id] = hud_item
        return hud_item

    def _free_hud(self, unit_id):
        if unit_id in self.hud_item_dict:
            hud_item = self.hud_item_dict.pop(unit_id)
            hud_item.set_visible(False)
            self.hud_item_cache.append(hud_item)

    def update_hud(self, unit):
        hud_item = self.get_hud(unit.unit_id)
        if hud_item:
            hud_item.update(unit, False)
        else:
            hud_item = self._create_hud(unit)
            hud_item.update(unit, True)
        # 增加可见计数
        hud_item.show_age += 1

    # 把本次没被刷新的,清理掉
    def update_hud_items(self):
        # 刷新可见性
        for hud_item in self.hud_item_dict.values():
            hud_item.show_age -= 1
            if hud_item.show_age <= 0:
                self.hide_queue.append(hud_item.unit_id)

        # 清空没有关联的
        if len(self.hide_queue) > 0:
            for unit_id in self.hide_queue:
                self._free_hud(unit_id)
            self.hide_queue.clear()


