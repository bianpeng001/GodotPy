#
# 2023年2月3日 bianpeng
#

###############################
# Units
###############################
class Unit:
    def __init__(self):
        self.unit_id = None
        self.unit_name = '桐乡渔叟'

        # 所属君主
        self.owner_player_id = None
        # 所属城
        self.owner_city_id = None

        # 战斗属性
        self.hp = self.maxhp = 100

        self.controller = None

    def update(self):
        pass

class TroopUnit(Unit):
    def __init__(self):
        super.__init__()

class CityUnit(Unit):
    def __init__(self):
        super.__init__()

###############################
# Units
###############################
class UnitMgr:
    def __init__(self):
        self.unit_dict = {}
        self.unit_id_seed = 100

    def get_next_unit_id(self):
        self.unit_id_seed += 1
        return self.unit_id_seed

    def update(self, delta_time):
        for k, v in self.unit_dict:
            v.update()

