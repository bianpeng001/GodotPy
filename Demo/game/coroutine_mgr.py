#
# 2023年2月1日 bianpeng
#

import traceback
import sys

from game.core import *

#
# 既然用了python，还是要做一下协程。发现用Iterator来做比较方便。
# 虽然Python有await, async关键字，用于Python的协程，但是awaitable的类型，不太方便。
#


# TODO: 还是要把父子coroutine的机制加进来，减少等待
# 即，子co先执行，父co后执行，这样当子co都已经完成的话，则父co可以本帧判断完成
# 否则，需要下一帧判断完毕。

#
# 可以等待的，用来yield的
#
class Waitable:
    def __init__(self):
        pass

    def is_done(self):
        return True

#
# wait for seconds
#
class WaitForSeconds(Waitable):
    def __init__(self, sec):
        super().__init__()
        self.stop = sec + get_cache_time()

    def is_done(self):
        return get_cache_time() >= self.stop
    
#
# 协程
#
class _Coroutine(Waitable):
    def __init__(self, iterator):
        self.done = False
        self.canceled = False
        self.error = None
        
        self.last_yield_value = None
        self.iterator = iterator

    def is_done(self):
        return self.done or self.canceled

    def next(self):
        # 这个我最喜欢了
        if self.last_yield_value and \
                isinstance(self.last_yield_value, Waitable) and \
                not self.last_yield_value.is_done():
            return
        self.last_yield_value = None
        try:
            while True:
                yield_value = next(self.iterator)
                
                if yield_value:
                    if isinstance(yield_value, Waitable):
                        if not yield_value.is_done():
                            self.last_yield_value = yield_value
                            break
                    else:
                        # TODO: 加一个自动把浮点转成时间的语法糖, yield 1.0 => yield WaitForSeconds(1.0)
                        if (isinstance(yield_value, int) or \
                                isinstance(yield_value, float)) and \
                                yield_value >= 0:
                            self.last_yield_value = WaitForSeconds(yield_value)
                        break
                    
        except StopIteration:
            self.done = True
            self.error = None
            
        except Exception as err:
            self.done = True
            self.error = err
            
            print('coroutine exception', err)
            #traceback.print_exc()
            traceback.print_exception(err)

# 用Iterator来做Coroutine
class CoroutineMgr:
    def __init__(self):
        self.co_list = []
        self.back_co_list = []

    def start_coroutine(self, co):
        co1 = _Coroutine(co)
        self.co_list.append(co1)
        return co1

    def start(self, co):
        return self.start_coroutine(co)

    def update(self):
        tmp = self.co_list
        self.co_list = self.back_co_list
        self.back_co_list = tmp
        
        for co in self.back_co_list:
            co.next()
            if not co.is_done():
                self.co_list.append(co)
        self.back_co_list.clear()
        
    def cancel(self, co):
        co.canceled = True
    

if __name__ == '__main__':
    def test01():
        def test_iter(start):
            print(start+1)
            yield 1
            print(start+2)
            yield 2
            print(start+3)
            yield 3
            print(start+4)

        mgr = CoroutineMgr()
        mgr.start(test_iter(10))
        mgr.start(test_iter(20))

        mgr.execute()
        mgr.execute()
        mgr.execute()
        mgr.execute()

        mgr.execute()
        mgr.execute()

    test01()


