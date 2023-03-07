#
# 2023年2月16日 bianpeng
#
import math

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED

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

        btn_labels = ['系统', '地图', '战报', '执行']
        btn_sys = self.ui_obj.find_node('BtnSys')
        btn_list = [btn_sys.dup() for i in range(len(btn_labels) - 1)]
        btn_list.append(btn_sys)
        
        for i in range(len(btn_list)):
            btn = btn_list[i]
            btn.set_text('\n'.join(btn_labels[i]))
            btn.set_position(1116-32*i, 4)

        btn_list[0].connect(PRESSED, self.on_setting_click)
        btn_list[1].connect(PRESSED, self.on_map_click)
        btn_list[3].connect(PRESSED, self.on_gm_click)

        # 事件
        from game.event_name import MAINUI_REFRESH
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)
       

    def on_gm_click(self):
        with open('./gm.py') as f:
            data = f.read()
            exec(data)
            print('-----------------gm ok-----------------')

    def on_map_click(self):
        obj = game_mgr.ui_mgr.map_panel_controller
        if obj.is_visible:
            obj.defer_close()
        else:
            obj.popup(150, 80)

    def on_setting_click(self):
        obj = game_mgr.ui_mgr.setting_panel_controller
        if obj.is_visible:
            obj.defer_close()
        else:
            obj.popup(150, 80)

    def format_amount_str(self, value):
        if value < 100000:
            return str(round(value))
        elif value < 100000000:
            value //= 10000
            return f'{value}万'
        else:
            value //= 100000000
            return f'{value}亿'
        
    def on_refresh(self):
        self.update_fps()

        # player resource...
        mp = get_main_player()

        money_text = self.format_amount_str(mp.total_money_amount)
        self.money_label.set_text(money_text)

        rice_text = self.format_amount_str(mp.total_rice_amount)
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
        
        
    
