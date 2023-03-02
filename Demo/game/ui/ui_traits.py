#
# 2023年3月1日 bianpeng
#
import sys

from game.core import log_util_debug
from game.game_mgr import game_mgr

#------------------------------------------------------------
# traits 功能类，用来复用一些代码, 这里不带数据，只提供方法
#------------------------------------------------------------

class CloseTrait:
    def defer_close(self):
        game_mgr.ui_mgr.defer_close(self)

class HeroListTrait:
    def init_header(self, header):
        name_label = header.find_node('Label')
        name_label.set_minimum_size(80, 0)
        name_label.set_text('姓名')

        age_label = name_label.dup()
        age_label.set_minimum_size(40, 0)
        age_label.set_text('年龄')

        action_label = name_label.dup()
        action_label.set_minimum_size(60, 0)
        action_label.set_text('活动')

        wuli_label = name_label.dup()
        wuli_label.set_minimum_size(40, 0)
        wuli_label.set_text('武力')

        tongshuai_label = name_label.dup()
        tongshuai_label.set_minimum_size(40, 0)
        tongshuai_label.set_text('统率')

        zhili_label = name_label.dup()
        zhili_label.set_minimum_size(40, 0)
        zhili_label.set_text('智力')

        zhengzhi_label = name_label.dup()
        zhengzhi_label.set_minimum_size(40, 0)
        zhengzhi_label.set_text('政治')


    def init_items(self, item_node, hero_list):
        for item in self.item_list:
            _, item_obj = item
            item_obj.destroy()
        self.item_list.clear()

        for hero_id in hero_list:
            hero = game_mgr.hero_mgr.get_hero(hero_id)

            new_item = item_node.dup()
            new_item.set_visible(True)
            self.item_list.append((hero_id, new_item))
            
            name_label = new_item.find_node('Label')
            #log_util_debug(f'refcnt={sys.getrefcount(name_label)}')
            name_label.set_minimum_size(80, 0)
            name_label.set_text(hero.hero_name)
            #name_label.connect(GUI_INPUT, bind_gui_input())

            age_label = name_label.dup()
            age_label.set_minimum_size(40, 0)
            age_label.set_text(f'{hero.age}')

            action_label = name_label.dup()
            action_label.set_minimum_size(60, 0)
            action_label.set_text('空闲')

            zhili_label = name_label.dup()
            zhili_label.set_minimum_size(40, 0)
            zhili_label.set_text(f'{hero.zhili}')

            tongshuai_label = name_label.dup()
            tongshuai_label.set_minimum_size(40, 0)
            tongshuai_label.set_text(f'{hero.tongshuai}')

            wuli_label = name_label.dup()
            wuli_label.set_minimum_size(40, 0)
            wuli_label.set_text(f'{hero.wuli}')

            zhengzhi_label = name_label.dup()
            zhengzhi_label.set_minimum_size(40, 0)
            zhengzhi_label.set_text(f'{hero.zhengzhi}')

