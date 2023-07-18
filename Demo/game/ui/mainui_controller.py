#
# 2023年2月16日 bianpeng
#
import math
import os.path

from game.core import *
from game.game_mgr import *
from game.base_type import UIController
from game.ui.ui_traits import PopupTrait
from game.event_name import PRESSED, MAINUI_REFRESH, KEY_PRESS
from game.input_mgr import KEY_F9, KEY_ESC

#
# 头顶主界面逻辑
#
class MainUIController(UIController, PopupTrait):
    def __init__(self):
        super().__init__()
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.money_label = self.ui_obj.find_node('MoneyLabel')
        #print(self.money_label)

        self.money_label = self.ui_obj.find_node('MoneyLabel')
        self.rice_label = self.ui_obj.find_node('RiceLabel')
        
        # 刷新点的信息
        self.fps_label = self.ui_obj.find_node('FPSLabel')
        self.refresh_time = game_mgr.time_sec
        self.refresh_frame_number = game_mgr.frame_number
        
        # 年份
        self.date_label = self.ui_obj.find_node('DateLabel')
        self.date_label.set_text('公元184年 春')

        #btn_labels = ['地图', '战报', '势力', '执行']
        btn_labels = ['资源', '建设', '势力']
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

        #get_btn('系统').connect(PRESSED, self.on_setting_click)
        get_btn('势力').connect(PRESSED, self.on_map_click)
        get_btn('建设').connect(PRESSED, self.on_build_click)
        #get_btn('执行').connect(PRESSED, self.on_gm_click)
        #get_btn('存档').connect(PRESSED, self.on_save_click)
        
        # 事件
        game_mgr.event_mgr.add(KEY_PRESS, self.on_key_press)
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)

    def on_key_press(self, keycode):
        #log_debug('key press', keycode)
        if keycode == KEY_F9:
            self.on_gm_click()
        elif keycode == KEY_ESC:
            self.on_sys_panel()
            
    def on_build_click(self):
        dlg = game_mgr.ui_mgr.build_panel_controller
        dlg.popup(250, 100)
    
    def on_sys_panel(self):
        panel = game_mgr.ui_mgr.sys_panel_controller
        if panel.is_show():
            panel.hide()
        else:
            panel.init()

    def on_gm_click(self):
        # gm文件的路径
        gm_file_path = os.path.join(game_mgr.game_path, 'gm.py')
        if os.path.exists(gm_file_path):
            with open(gm_file_path, encoding='utf-8') as f:
                data = f.read()
                try:
                    c = compile(data, 'gm.py', 'exec')
                    exec(c)
                finally:
                    print('-----------------', gm_file_path, '-----------------')

    def on_map_click(self):
        obj = game_mgr.ui_mgr.map_panel_controller
        if obj.is_show():
            obj.defer_close()
        else:
            obj.init()
            obj.popup(150, 80)

    def on_refresh(self):
        self.update_fps()

        # 更新玩家资源
        mp = get_main_player()
        if mp:
            config_mgr = game_mgr.config_mgr

            money_text = config_mgr.format_amount_label(mp.total_money_amount)
            self.money_label.set_text(money_text)

            rice_text = config_mgr.format_amount_label(mp.total_rice_amount)
            self.rice_label.set_text(rice_text)

    def update_fps(self):
        delta_time = game_mgr.time_sec - self.refresh_time
        delta_frame_number = game_mgr.frame_number - self.refresh_frame_number

        self.refresh_time = game_mgr.time_sec
        self.refresh_frame_number = game_mgr.frame_number

        fps0 = int(Debug.get_monitor(0))
        fps = int(delta_frame_number/delta_time) if delta_time > 0 else 0
        dc = Debug.get_drawcall()
        
        self.fps_label.set_text(f'{fps} {fps0} {dc}')
    
    # def on_save_click(self):
    #     # TODO:
    #     game_mgr.game_data.save('01.db')
        
    