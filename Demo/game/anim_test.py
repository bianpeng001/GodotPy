#
# 2023年2月13日 bianpeng
#

from game.core import *


class AnimTest(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        connect(self.get_node(), "ready", self._ready)

    def _ready(self):
        anim_player = Node.find_node(Node.get_parent(self.get_node()), "Model/AnimationPlayer")
        AnimationPlayer.play(anim_player, "NewAnimLib/Run")


class TroopAnimTest(NodeObject):
    def _create(self):
        connect(self.get_node(), "ready", self._ready)

    def _ready(self):
        node = Node.get_parent(self.get_node())
        for i in range(2, 10):
            anim_player = Node.find_node(node, f"Soldier{i:02}/Model/AnimationPlayer")
            if anim_player:
                AnimationPlayer.play(anim_player, "NewAnimLib/Run")
                AnimationPlayer.set_speed_scale(anim_player, 3)

