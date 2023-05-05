#
# 2023年2月8日 bianpeng
#

from game.core import log_debug, OS
from game.game_mgr import *
from game.base_type import *

#
# 一个HUD，封装一下，关联unit_id，和UI元素
#
class HUDItem:
    def __init__(self):
        self.unit_id = 0

        self.unit_type = 0
        self.offset = -40

        self.hud_obj = None
        self.title_obj = None
        self.hp_obj = None
        
        self.flag_label_obj = None
        self.flag_obj = None
        
        # 高度修正
        self.hud_height = 8
        
        # 可见度,加一个计数
        self.show_count = 1

    def set_visible(self, value):
        self.hud_obj.set_visible(value)

    def set_text(self, text):
        self.title_obj.set_text(text)

    def set_flag_text(self, text):
        if not self.flag_label_obj:
            self.flag_label_obj = self.hud_obj.find_node('FlagLabel')
        self.flag_label_obj.set_text(text)

    def set_flag_color(self, r,g,b):
        if not self.flag_obj:
            self.flag_obj = self.hud_obj.find_node('Flag')
        self.flag_obj.set_self_modulate(r,g,b)

    # new_hud 是否新创建的, 少刷新一些东西
    def update(self, unit, new_hud):
        if unit:
            x,y,z = unit.get_position()
            x1,y1 = get_main_camera().world_to_screen(x,y+self.hud_height,z)
            self.hud_obj.set_position(x1+self.offset, y1)
            
            hud_comp = unit.get_controller().hud_comp
            if new_hud or not hud_comp.is_valid():
                hud_comp.set_valid()
                
                if unit.owner_player_id != 0:
                    player = game_mgr.player_mgr.get_player(unit.owner_player_id)
                    self.set_flag_text(player.first_name)
                    self.set_flag_color(*player.flag_color)
                else:
                    self.set_flag_text('')
                    self.set_flag_color(1,1,1)
                    
            # 然后是刷新血量等参数
            pass

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
        
        self.hide_queue = []

    def setup(self):
        self.hud_root_obj = game_mgr.scene_root_obj.find_node('HUDRoot')

    def update(self, delta_time):
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
            self.template_list = [ None for i in range(10) ]
            self.template_list[1] = OS.instantiate('res://ui/CityHUD.tscn')
            self.template_list[2] = OS.instantiate('res://ui/TroopHUD.tscn')

            for hud_obj in self.template_list:
                if hud_obj:
                    hud_obj.reparent(self.hud_root_obj)
                    hud_obj.set_visible(False)

        # create hud_item
        hud_item = None

        if len(self.hud_item_cache) > 0:
            index = -1
            count = len(self.hud_item_cache)
            if count > 0:
                for i in range(-1, -count-1, -1):
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

            if unit.unit_type == UT_TROOP:
                hud_item.offset = -40
                hud_item.hud_height = 6.0
            else:
                hud_item.offset = -40
                hud_item.hud_height = 7.0

        #log_debug('create hud', unit.unit_id, unit.unit_name)
        hud_item.unit_id = unit.unit_id
        hud_item.set_text(unit.unit_name)
        hud_item.set_visible(True)
        hud_item.show_count = 1
        
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
        hud_item.show_count += 1

    # 把本次没被刷新的,清理掉
    def update_hud_items(self):
        # 需要隐藏的排队
        hide_queue = self.hide_queue
        hide_queue.clear()
        
        # 刷新可见性
        for hud_item in self.hud_item_dict.values():
            hud_item.show_count -= 1
            if hud_item.show_count <= 0:
                hide_queue.append(hud_item.unit_id)

        # 清空没有关联的
        if len(hide_queue) > 0:
            for unit_id in hide_queue:
                self._free_hud(unit_id)
            hide_queue.clear()


