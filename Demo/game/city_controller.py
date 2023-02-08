#
# 2023年2月2日 bianpeng
#

from game.core import *
from game.game_mgr import game_mgr

# 城池
class CityController(BaseController):
    def __init__(self):
        super().__init__()

        self.ai_tick_time = 0

    def set_title(self, text):
        title_node = find_node(self.model_node, 'HUD/Title')
        Label3D.set_text(title_node, text)

    def process_ai(self):
        self.ai_tick_time += game_mgr.delta_time
        if self.ai_tick_time > 0.3:
            self.ai_tick_time = 0
            self.on_ai_tick()

    def on_ai_tick(self):
        pass

    def update(self):
        self.process_ai()

