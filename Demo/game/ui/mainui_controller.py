#
# 2023年2月16日 bianpeng
#
import math
import os.path

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED, MAINUI_REFRESH

# 头顶主界面逻辑
class MainUIController(UIController, PopupTrait):
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.money_label = self.ui_obj.find_node('MoneyLabel')
        #print(self.money_label)

        self.money_label = self.ui_obj.find_node('MoneyLabel')
        self.rice_label = self.ui_obj.find_node('RiceLabel')
        
        # 刷新点的信息
        self.fps_label = self.ui_obj.find_node('FPSLabel')
        self.refresh_time = game_mgr.sec_time
        self.refresh_frame_number = game_mgr.frame_number

        btn_labels = ['系统', '读档', '存档', '地图', '战报', '执行', '势力']
        btn_1 = self.ui_obj.find_node('Btn1')
        btn_list = [btn_1.dup() for i in range(len(btn_labels) - 1)]
        btn_list.append(btn_1)
        
        for i in range(len(btn_list)):
            btn = btn_list[i]
            text = btn_labels[i]
            btn.set_text('\n'.join(text))
            btn.set_position(1116-32*i, 4)

        def get_btn(s):
            index = btn_labels.index(s)
            return btn_list[index]

        get_btn('系统').connect(PRESSED, self.on_setting_click)
        get_btn('地图').connect(PRESSED, self.on_map_click)
        get_btn('执行').connect(PRESSED, self.on_gm_click)

        # 事件
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)

        self.gm_file_path = os.path.join(game_mgr.game_path, 'gm.py')
        if not os.path.exists(self.gm_file_path):
            self.gm_file_path = None

    def on_gm_click(self):
        if self.gm_file_path:
            with open(self.gm_file_path, encoding='utf-8') as f:
                data = f.read()
                exec(data)
                print('-----------------', self.gm_file_path, '-----------------')

    def on_map_click(self):
        obj = game_mgr.ui_mgr.map_panel_controller
        if obj.is_show():
            #obj.defer_close()
            game_mgr.ui_mgr.pop_panel(obj)
        else:
            obj.init()
            obj.popup(150, 80)
            game_mgr.ui_mgr.push_panel(obj)

    def on_setting_click(self):
        obj = game_mgr.ui_mgr.setting_panel_controller
        if obj.is_show():
            game_mgr.ui_mgr.pop_panel(obj)
        else:
            obj.init()
            obj.popup(150, 80)
            game_mgr.ui_mgr.push_panel(obj)

    def on_refresh(self):
        self.update_fps()

        config_mgr = game_mgr.config_mgr

        # 更新玩家资源
        mp = get_main_player()

        money_text = config_mgr.format_amount_label(mp.total_money_amount)
        self.money_label.set_text(money_text)

        rice_text = config_mgr.format_amount_label(mp.total_rice_amount)
        self.rice_label.set_text(rice_text)

    def update_fps(self):
        delta_time = game_mgr.sec_time - self.refresh_time
        delta_frame_number = game_mgr.frame_number - self.refresh_frame_number

        self.refresh_time = game_mgr.sec_time
        self.refresh_frame_number = game_mgr.frame_number

        fps0 = int(Debug.get_monitor(0))
        fps = int(delta_frame_number/delta_time) if delta_time > 0 else 0
        dc = Debug.get_drawcall()
        
        self.fps_label.set_text(f'fps:{fps},{fps0} dc:{dc}')
        
        
    
