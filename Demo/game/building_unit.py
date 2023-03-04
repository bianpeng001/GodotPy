#
# 2023年3月4日 bianpeng
#
from game.core import *
from game.game_mgr import *
from game.base_type import Unit, UT_BUILDING

#
class BuildingController(Controller):
    def __init__(self):
        super().__init__()
        pass

#
class BuildingUnit(Unit, UnitTrait):
    def __init__(self):
        self._controller = BuildingController()
        self._controller._unit = self

        self.unit_type = UT_BUILDING

