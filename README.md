# GodotPy

## 学习一下godot + python。

一直有关注godot，非常佩服这群人的毅力和实力，godot已经很厉害了。写点小东西，支持一把godot engine。godot engine 4.0，改进了好多，作为一个年轻的游戏引擎，他已经足够优秀。由于没有沉重的历史包袱和商业包袱，看到有一些模块非常优秀的吐故纳新。例如，抛弃一个大包袱mono，投入.net core的怀抱。

本人对python非常喜欢，不过之前在工作中都是用lua的。想做一个简单的python绑定，没啥太多的追求，当简单的脚本使用，也是一个自我学的习的。如果我的一些不成熟的idea，对别人产生一点点帮助，将不胜荣幸。


## 对Godot的提升
利用Python的语言特性，给godot引擎做一些方便的功能。比如，协程。
```python
    def co_print_number():
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)
        yield None
        print(game_mgr.frame_number)

        print(f'{OS.get_time()} {game_mgr.sec_time}')
        yield WaitForSeconds(3)
        print(f'{OS.get_time()} {game_mgr.sec_time}')
```

## 目录

Python: 编译python的scons脚本，和一些平台相关的配置。

Godot: Godot的一个自定义模块，和构造脚本。目前仅支持 godot 4.0。

Demo: 测试用的工程，写一个小游戏


