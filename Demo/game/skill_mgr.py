#
# 2023年4月17日 bianpeng
#

class SkillItem:
    def __init__(self):
        self.life_time = 1
        self.time = 0


#
# 技能管理
#
class SkillMgr:
    def __init__(self):
        self.item_list = []
        self.back_item_list = []

    def update(self, delta_time):
        tmp = self.item_list
        self.item_list = self.back_item_list
        self.back_item_list = tmp

        if len(self.back_item_list) > 0:
            for item in self.back_item_list:
                item.time += delta_time
                if item.time >= item.life_time:
                    pass
                else:
                    self.add_skill(item)

            self.back_item_list.clear()

    def add_skill(self, item):
        self.item_list.append(item)




