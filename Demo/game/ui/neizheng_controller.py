#
# 2023年2月23日 bianpeng
#

#
class NeiZhengController:
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj

        self.btn_close = ui_obj.find_node('Panel/BtnClose')
        self.btn_close.connect('pressed', self.on_close)

        self.tab_bar = ui_obj.find_node('TabBar')
        self.tab_bar.connect('tab_changed', self.on_tab_changed)

    def on_close(self):
        self.ui_obj.set_visible(False)

    def on_tab_changed(self):
        idx = self.tab_bar.get_current_tab()
        print(idx)
        

