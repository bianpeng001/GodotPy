#
# 2023年2月16日 bianpeng
#
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
        
        
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)

    def _get_amount_str(self, value):
        if value < 100000:
            return str(round(value))
        else:
            value //= 100000
            return f'{value}万'

    def on_refresh(self):
        player = game_mgr.player_mgr.main_player

        money_text = self._get_amount_str(player.total_money_amount)
        self.money_label.set_text(money_text)

        rice_text = self._get_amount_str(player.total_rice_amount)
        self.rice_label.set_text(rice_text)



