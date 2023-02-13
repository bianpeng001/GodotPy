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

