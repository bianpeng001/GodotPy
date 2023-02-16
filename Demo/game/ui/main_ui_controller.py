#
# 2023年2月16日 bianpeng
#

from game.core import *

class MainUIController:
    def __init__(self):
        pass

    def init(self, ui_node):
        self.ui_node = ui_node

        self.money_label = Node.find_node(self.ui_node, 'MoneyLabel')
        #print(self.money_label)

        a = find_node2(self.ui_node, 'MoneyLabel')
        a.set_text('1111')
        




