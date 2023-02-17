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
        
        
        game_mgr.event_mgr.add(MAINUI_REFRESH, self.on_refresh)

    def on_refresh(self):
        player = game_mgr.player_mgr.main_player
        self.money_label.set_text(str(player.total_money_amount))

