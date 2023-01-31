#
# 2023年1月31日 bianpeng
#

from game.core import Singleton

# 管理配置信息
class ConfigMgr(Singleton)
    def __init__(self):
        pass


config_mgr = ConfigMgr.get_instance()

