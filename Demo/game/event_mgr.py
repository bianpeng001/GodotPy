#
# 2023年2月21日 bianpeng
#

#------------------------------------------------------------
# event mgr
#------------------------------------------------------------
class EventMgr:
    def __init__(self):
        self.map = {}

    def add(self, name, handler):
        if not name in self.map:
            self.map[name] = [handler]
        else:
            self.map[name].append(handler)

    def remove(self, name, handler):
        if name in self.map:
            self.map[name].remove(handler)

    def emit(self, name, *args, **kwargs):
        if name in self.map:
            for handler in self.map[name]:
                handler.__call__(*args, **kwargs)

    def post(self, name, *args, **kwargs):
        pass

    def execute(self):
        pass
        