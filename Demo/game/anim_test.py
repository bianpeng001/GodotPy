#
# 2023年2月13日 bianpeng
#

from game.core import *

#
class AnimTest(NodeObject):
    def __init__(self):
        super().__init__()

    def _create(self):
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        anim_player = self.get_obj().get_parent().find("Model/AnimationPlayer")
        anim_player.play("SoldierAnimLib/Run")


class TroopAnimTest(NodeObject):
    def _create(self):
        self.get_obj().connect("ready", self._ready)

    def _ready(self):
        node = self.get_obj().get_parent()
        for i in range(2, 11):
            anim_player = node.find_node(f"Soldier{i:02}/Model/AnimationPlayer")
            if anim_player:
                anim_player.play("SoldierAnimLib/Run")
                anim_player.set_speed_scale(2.6)

