#
# 2023年1月31日 bianpeng
#

class GameMgr():
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()

        # init in boot.py
        self._event_mgr = None
        self._input_mgr = None
        self.co_mgr = None

        self.camera_mgr = None
        self.ground_mgr = None
        self.troop_mgr = None
        self.unit_mgr = None
        self.ui_mgr = None
        self.hero_mgr = None

        self.game_data = None

        # cached time/delta_time
        self.time = 0
        self.delta_time = 0
        self.frame_number = 0

    @property
    def event_mgr(self):
        return self._event_mgr

    @property
    def input_mgr(self):
        return self._input_mgr

game_mgr = GameMgr.get_instance()


