#
# 2023年2月16日 bianpeng
#
import math

from game.core import *
from game.game_mgr import *
from game.event_name import PRESSED
from game.base_type import UIController

# 头顶主界面逻辑
class MainUIController(UIController):
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

        self.ui_obj.find_node('BtnGM').set_text('执\n行')
        self.ui_obj.find_node('BtnSys2').set_text('系\n统')

        # 事件
        from game.event_name import MAINUI_REFRESH
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)

        # gm
        self.ui_obj.find_node('BtnGM').connect(PRESSED, self.on_gm_click)

    def on_gm_click(self):
        with open('./gm.py') as f:
            data = f.read()
            exec(data)
            print('-----------------gm ok-----------------')

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
        
        
    
