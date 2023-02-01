#
# 2023年2月1日 bianpeng
#

#
class CoroutineMgr:
    def __init__(self):
        self.co_list = []

    def start_coroutine(self, co):
        self.co_list.append(co)


