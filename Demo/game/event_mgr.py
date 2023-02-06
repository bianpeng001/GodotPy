#
# 2023年2月1日 bianpeng
#

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
                #pass


# class Test:
#     def __init__(self):
#         self.event_mgr = EventMgr()
#         self.event_mgr.add('hello', self.on_hello)
#         self.event_mgr.emit('hello', 1234)
    
#     def on_hello(self, msg, *args):
#         print('on_hello', msg)

# Test()

