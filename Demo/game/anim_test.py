#
# 2023年2月13日 bianpeng
#

from game.core import *

class AnimTest(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        #connect(self.get_node(), "ready", self._ready)
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        anim_player = find_node2(Node.get_parent(self.get_node()), "Model/AnimationPlayer")
        anim_player.play("SoldierAnimLib/Run")


class TroopAnimTest(NodeObject):
    def _create(self):
        #connect(self.get_node(), "ready", self._ready)
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        node = Node.get_parent(self.get_node())
        for i in range(2, 11):
            anim_player = find_node2(node, f"Soldier{i:02}/Model/AnimationPlayer")
            if anim_player:
                anim_player.play"SoldierAnimLib/Run")
                anim_player.set_speed_scale(2.6)

