from types import coroutine

@coroutine
def stop():
   yield 1234
   yield 4321
   
async def test1():
   await stop()
   await stop()

c = test1()
for i in range(10):
    a = c.send(None)
    print(f'{i}. yield', a)

    


