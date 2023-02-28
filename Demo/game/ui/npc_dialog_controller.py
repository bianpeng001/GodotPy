#
# 2023年2月28日 bianpeng
#

class NpcDialogController:
    def __init__(self):
        self.show_time = 0

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        self.dialog_label = self.ui_obj.find_node('Label')

    def show_dialog(self, text, show_time = 1):
        self.show_time += show_time
        self.dialog_label.set_text(text)

        self.ui_obj.set_position(350, 480)
        self.ui_obj.set_visible(True)
