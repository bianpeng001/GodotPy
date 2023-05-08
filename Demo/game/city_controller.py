#
# 2023年2月2日 bianpeng
#

import random

from game.core import log_debug, ResCapsule
from game.game_mgr import *
from game.base_type import Controller, narudo_range, UT_CITY
from game.ground_mgr import pos_to_colrow

#
# 城池
#
class CityController(Controller):
    def __init__(self, unit):
        super().__init__(unit)

        # 控制属性
        self.ai_tick_time = 0

    def set_title(self, text):
        pass

    def set_flag_color(self):
        node = self.get_model_node()
        if node:
            flag_node = node.find_node('Flag')
            if flag_node:
                #mesh_instance3d_load_material(flag_node, 0, 'res://models/Color/Green.tres')
                #flag_node.load_material(1, 'res://models/Color/Green.tres')
                # TODO: 这里还要读取数据, 加载正确的颜色
                
                path = 'res://models/Color/FlagCityMat.tres'
                
                if self.get_unit().owner_player_id != 0:
                    player = game_mgr.player_mgr.get_player(self.get_unit().owner_player_id)
                    if not player.flag_mat:
                        a = ResCapsule.load_resource(path)
                        player.flag_mat = a.duplicate()
                        player.flag_mat.set_shader_color("_color", 1,0,0,1)
                    flag_node.set_surface_material(1, player.flag_mat.res)
                else:
                    a = ResCapsule.load_resource(path)
                    flag_node.set_surface_material(1, a.res)

    # 计算资源增长
    def _calc_resource_grow(self, amount, growth_rate, delta_time, max_amount):
        value =  amount + growth_rate * delta_time
        if value > max_amount:
            value = max_amount
        return value

    # 刷新资源增长
    def refresh_resource_amount(self, delta_time):
        city_unit = self.get_unit()

        # 重新计算城内各个增长率
        order,rice,money,population,army = self.calc_growth_rate(
                city_unit.satrap,
                city_unit.order_incharge,
                city_unit.farmer_incharge,
                city_unit.trader_incharge)

        city_unit.money_amount.grow(money*0.1, delta_time)
        city_unit.rice_amount.grow(rice*0.1, delta_time)
        city_unit.population.grow(population*0.1, delta_time)
        city_unit.army_amount.grow(army*0.1, delta_time)

    # 计算各个资源的增长率
    def calc_growth_rate(self,
            satrap, 
            order_incharge,
            farmer_incharge,
            trader_incharge):
        config_mgr = game_mgr.config_mgr

        order = config_mgr.calc_order_growth_rate(
            get_hero(satrap), get_hero(order_incharge)
        )

        rice = config_mgr.calc_rice_growth_rate(
            get_hero(satrap), get_hero(farmer_incharge)
        )
        
        money = config_mgr.calc_money_growth_rate(
            get_hero(satrap), get_hero(trader_incharge)
        )

        population = config_mgr.calc_population_growth_rate(
            get_hero(satrap)
        )
        army = config_mgr.calc_army_growth_rate(
            get_hero(satrap)
        )

        return order,rice,money,population,army

    def on_ai_tick(self, tick_time):
        city_unit = self.get_unit()
        
        def find_enemy_city(col,row):
            owner_player_id = self.get_unit().owner_player_id
            
            for dx,dy in narudo_range(4):
                tile = game_mgr.ground_mgr.get_tile_colrow(col+dx, row+dy)
                if not tile:
                    continue
                for unit in tile.get_unit_list():
                    if unit.unit_type == UT_CITY and \
                            (unit.owner_player_id == 0 or \
                            unit.owner_player_id != owner_player_id):
                        return unit

        # TODO: 这个要改,细化行为,要有各种行为
        # 测试行为，不断招兵，军队数量达到1000，就出兵征讨
        army_amount = city_unit.army_amount.value
        if army_amount > 1000:
            amount = city_unit.army_amount.get_value()
            city_unit.army_amount.value = 0

            x,y,z = city_unit.get_position()
            col,row = pos_to_colrow(x,z)
            target_city = find_enemy_city(col,row)
            if target_city:
                troop = game_mgr.game_play.create_troop(city_unit,
                    [],
                    x,y,z,
                    1000,
                    4)
                troop.target_unit_id = target_city.unit_id
                troop.get_controller().goto_state('start')

    # 驱动 ai tick
    def drive_ai_tick(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.3:
            self.on_ai_tick(self.ai_tick_time)
            self.ai_tick_time = 0

    def update(self):
        if game_mgr.enable_city_ai and self.get_unit().enable_ai:
            self.drive_ai_tick()

    def start(self):
        self.get_unit().load_model()
        

