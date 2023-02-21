#
# 2023年2月16日 bianpeng
#
import math

from game.core import *
from game.game_mgr import game_mgr
from game.event_name import MAINUI_REFRESH

# 头顶主界面逻辑
class MainUIController:
    def __init__(self):
        pass

    def init(self, ui_node):
        self.ui_node = ui_node

        self.money_label = Node.find_node(self.ui_node, 'MoneyLabel')
        #print(self.money_label)

        self.money_label = find_node2(self.ui_node, 'MoneyLabel')
        self.rice_label = find_node2(self.ui_node, 'RiceLabel')
        
        # 刷新点的信息
        self.fps_label = find_node2(self.ui_node, 'FPSLabel')
        self.refresh_time = game_mgr.sec_time
        self.refresh_frame_number = game_mgr.frame_number

        # 事件
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)

    def _get_amount_str(self, value):
        if value < 100000:
            return str(round(value))
        else:
            value //= 10000
            return f'{value}万'

    def on_refresh(self):
        # player resource...
        player = game_mgr.player_mgr.main_player

        money_text = self._get_amount_str(player.total_money_amount)
        self.money_label.set_text(money_text)

        rice_text = self._get_amount_str(player.total_rice_amount)
        self.rice_label.set_text(rice_text)

        self.update_fps()

    def update_fps(self):
        delta_time = game_mgr.sec_time - self.refresh_time
        delta_frame_number = game_mgr.frame_number - self.refresh_frame_number
        self.refresh_time = game_mgr.sec_time
        self.refresh_frame_number = game_mgr.frame_number

        fps = int(delta_frame_number/delta_time)
        fps0 = int(Debug.get_monitor(0))
        draw_call = get_draw_call()
        
        self.fps_label.set_text(f'fps:{fps},{fps0} dc:{draw_call}')
        
        
