# GodotPy

## 学习一下godot + python。

一直有关注godot，非常佩服这群人的毅力和实力，godot已经很厉害了。给他做一点小模块，用实际行动,支持一下godot engine。2023.3.2, godot engine 4.0正式发布. 作为一个年轻的游戏引擎，他已经足够优秀。由于没有沉重的历史包袱和商业包袱，可以发现很多新想法, 新思路在godot身上得以体现. 而且,我觉得godot最大的好处就是,肯定还没能达到大型商业引擎的层次,尽管已经很方便好用了.这一点正说明是上车的绝佳机会,等到成熟稳定的那一天,就像堆满了物品的老房子,让人无从下手了.

本人对python非常喜欢，不过之前在工作中都是用lua的。想做一个简单的python绑定，没啥太多的追求，当简单的脚本使用，也是一个自我学的习的。如果我的一些不成熟的idea，对别人产生一点点帮助甚至启发，将不胜荣幸。


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

详细情况，见[开发记录](Demo/README.md)和[我的博客](https://bianpeng001.github.io/GodotPy/blog.htm)

## 文档
文档用markdownjs来从md生成页面，[marked](https://github.com/markedjs/marked)
[markdown-css](https://github.com/sindresorhus/github-markdown-css)


## 目录

Python: 编译python的scons脚本，和一些平台相关的配置。

Godot: Godot的一个自定义模块，和构造脚本。目前仅支持 godot 4.0。

Demo: 测试用的工程，写一个小游戏

所以,为了验证python模块能用,且足够好用. 我会努力把Demo,完善成自己最喜欢的游戏,三国9,光荣三国志系列最令人印象深刻的一代作品. 可能的话,再添加一点三国10的内容. 当然画面立绘和音乐, 我就不追随了. 不是不想, 应该毫无可能吧.

## godot engine
[website](https://godotengine.org)
![icon](https://godotengine.org/assets/logo_dark.svg)


