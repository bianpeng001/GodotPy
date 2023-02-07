#
# 2023年2月2日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

#
class CityController(BaseController):
    def __init__(self):
        super().__init__()

    def set_title(self, text):
        title_node = find_node(self.root_node, 'HUD/Title')
        label3d.set_text(title_node, text)

    def update(self):
        pass

