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

        self.input_mgr = None
        self.camera_mgr = None
        self.ground_mgr = None
        self._event_mgr = None
        self._troop_mgr = None

    @property
    def event_mgr(self):
        return self._event_mgr

    @property
    def troop_mgr(self):
        return self._troop_mgr

game_mgr = GameMgr.get_instance()

