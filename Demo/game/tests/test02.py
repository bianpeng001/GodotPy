import traceback

def test1():
    yield 1
    yield 2
    raise Exception('333')



try:
    a = test1()
    next(a)
    next(a)
    next(a)
except StopIteration as ex:
    pass
except Exception as err:
    print(err)
    traceback.print_exception(err)
    
    
