#
# 2023年2月28日 bianpeng
#

from game.base_type import UIController

#
class SelectHeroController(UIController):
    def __init__(self):
        super().__init__()
        pass

    def setup(self, ui_obj):
        self.ui_obj = ui_obj
        