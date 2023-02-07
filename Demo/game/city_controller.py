#
# 2023年2月2日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

#
class CityController(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        pass

    def set_title(self, text):
        p = get_parent(self.get_node())
        title_node = find_node(p, 'HUD/Title')
        label3d.set_text(title_node, text)

    def update(self):
        pass

