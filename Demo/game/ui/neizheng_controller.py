#
# 2023年2月23日 bianpeng
#

#
class NeiZhengController:
    def __init__(self):
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        btn_close = ui_obj.find_node('Panel/BtnClose')
        btn_close.connect('pressed', self.on_close)

    def on_close(self):
        self.ui_obj.set_visible(False)

