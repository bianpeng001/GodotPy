#
# 2023年2月23日 bianpeng
#

from game.game_mgr import game_mgr


#
class NeiZhengController:
    def __init__(self):
        self.tab_index = 0

        self.tabs = []

    def setup(self, ui_obj):
        from game.event_name import PRESSED

        self.ui_obj = ui_obj

        self.btn_close = ui_obj.find_node('Panel/BtnClose')
        self.btn_close.connect(PRESSED, self.on_close)

        self.tab_bar = ui_obj.find_node('TabBar')
        self.tab_bar.connect('tab_changed', self.on_tab_changed)

        self.tabs = [
            ui_obj.find_node('Panel/TabNong'),
            ui_obj.find_node('Panel/TabShang'),
            ui_obj.find_node('Panel/TabJiang'),
        ]
        self.tab_index = 0
        self.tab_bar.set_current_tab(self.tab_index)
        self.on_tab_changed()

    def on_close(self):
        game_mgr.ui_mgr.defer_close(self.ui_obj)

    def on_tab_changed(self):
        self.tab_index = self.tab_bar.get_current_tab()
        for i in range(len(self.tabs)):
            self.tabs[i].set_visible(i == self.tab_index)
        

