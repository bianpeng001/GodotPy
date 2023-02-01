#
# 2023年2月1日 bianpeng
#


#
# 既然用了python，还是要做一下协程。发现用Iterator来做比较方便。
# 虽然Python有await, async关键字，用于Python的协程，但是awaitable的类型，不太方便。
#

#
class Waitable:
    def __init__(self):
        pass

    def is_done(self):
        return True

#
class _Coroutine(Waitable):
    def __init__(self, iterator):
        self.done = False
        self.error = False
        self.yield_value = None

        self.iterator = iterator

    def is_done(self):
        return self.done

    def next(self):
        # 这个我最喜欢了
        if self.yield_value and \
                isinstance(self.yield_value, Waitable):
            if not self.yield_value.is_done():
                return

        try:
            while(True):
                self.yield_value = next(self.iterator)
                
                if self.yield_value and\
                        isinstance(self.yield_value, Waitable):
                    if not self.yield_value.is_done():
                        break
                else:
                    self.yield_value = None
                    break
            
        except StopIteration:
            self.done = True
        except:
            self.done = True
            self.error = True


# 用Iterator来做Coroutine
class CoroutineMgr:
    def __init__(self):
        self.co_list = []
        self.back_list = []

    def start_coroutine(self, co):
        self.co_list.append(_Coroutine(co))

    def add(self, co):
        self.start_coroutine(co)

    def advance(self):
        tmp = self.co_list
        self.co_list = self.back_list
        self.back_list = tmp

        for a in self.back_list:
            a.next()
            if not a.is_done():
                self.co_list.append(a)
        self.back_list.clear()
    

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
    mgr.add(test_iter(10))
    mgr.add(test_iter(20))

    mgr.advance()
    mgr.advance()
    mgr.advance()
    mgr.advance()

    mgr.advance()
    mgr.advance()

test01()


