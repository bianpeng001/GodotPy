# GodotPy


## 起因
2023年1月18日，快过年了，有点时间。

一直在关注godot engine，最近4.0快发布了，共襄盛举。对比成熟引擎，很多人比较过优缺点了。我觉得godot比较简单精致，参与感更强一些。

python现在越来越好，想继续用，况且长远看python在服务器端也有机会一展拳脚。

因此，godot + python 有没有搞头？

其实python是godot抛弃的脚本语言，因为官方解释得很清楚了，gdscript更合适godot的特性。但毕竟那是很久以前的事情了，python和godot都今非昔比。此外找了一下，发现已经有一个python绑定了，但是看着比较重量级。而我只想当脚本用用，越轻量级越好。

## python对比lua
在游戏脚本领域，其实lua是更主流的选择，lua来做很多事情就会简单直接很多，比如嵌入扩展啥的。但是，lua本身相比于python，相对弱一些，各种工具和开发者数量上都不足。所以，我还是想尝试一下用python的实现，权当是一次学习。

然后接入过程里，我已经感受到了python的烦人之处了。

## 目录
Demo: 试验工程，测试和完善GodotPy

Godot: godot的扩展和构造脚本

Python: python的构造脚本和扩展

GameFormula: 一个公式的实现，旧代码保留


## 做一个小游戏试试看

进行中

## 协程
协程是个好东西，给godot做一个吧。

## 开发笔记

_ready 是子节点先收到，最后是根节点。_enter_tree顺序相反。所以在根节点做了一个MainLoop，用于控制初始化顺序。

scenetree任意一个子树，可以存成tscn(scn表示scene，t表示text)文件，然后复用。类似于prefab。感觉godot更舒服一些，有种面向xml的感觉。
场景文件，tscn格式。用parent字段来维护一个树结构。头部声明 ext_resource，用到的依赖资源。然后在节点里面指定关联。节点定义后，紧接着属性修改。资源用uid来确定。
出现uid重复的处理。把引用错误的资源，reimport，目前遇到的几次是glb里面导入的mesh。
```c++
    // 加载一个场景文件
    Ref<PackedScene> res = ResourceLoader::load(path);
    // 实例化
    auto node = Object::cast_to<Node3D>(res->instantiate(PackedScene::GEN_EDIT_STATE_DISABLED));
    // 加入场景树
    auto st = SceneTree::get_singleton();
    auto scene = st->get_current_scene();
    scene->add_child(node);
```

对node，set_process，才能收到process信号。set_process_input，才能收到input事件。

godot editor, 有一定的remote调试功能，即在编辑器里面启动后，能对scenetree里面的内容，在编辑器和运行时之间有一些反馈。在monitor里面，有详细的fps,drawcall,memory,object count...信息

node只提供了基础功能。node3d才有transform的信息。

没有提供基于组件的开发模式。所以都是用节点来完成的。比如这个python的脚本，我是放了一个FPyObject的节点来提供脚本运行。

ProjectSetting里面有很多宝藏，Cursor，icon...。

gltb格式在导入后，最好把mesh单独保存，这样才能被单独读取。材质也要设置为外部的，不然会从gltb里面把贴图带过来(疑似如此)

UI开发

Python的Py_INCREF, Py_DECREF，这两项的使用，有一些注意点。目前从容器中Get出来的值是borrowed reference，即，不需要修改引用计数。
注意，PyObject_CallMethod返回值，如果不需要保留，则必须减掉引用计数。如果返回NULL，则说明有运行异常。需要自行打印错误信息。

由于godot对stdout,stderr有自己的处理。为了接收python的报错信息，需要做一些额外的处理。看Python的PyErr_Print,最后会调用到python的sys.stdout, sys.stderr的PyObject对象上去write。所以，我的做法是，在boot.py里面，一开始，就把Python的sys.stdout, sys.stderr,换成一个假的IO对象。
```Python
class PrintLine:
    def write(self, s):
        print_line(s)

saved_stderr = sys.stderr
sys.stderr = PrintLine()

saved_stdout = sys.stdout
sys.stdout = PrintLine()

```

windows desktop下面的发布。
1. 构造，scons p=windows tools=no bits=64 -j6 target=template_release，发布版本。命名为Demo.exe
2. 导出数据包，bin\godot.windows.editor.dev.x86_64.console.exe --path h:\GodotPy\Demo -w --export-pack "Windows Desktop" ..\Build\Demo.pck
3. 复制其他依赖的文件，比如Lib, python3.dll，**/*.py
4. 完毕

直接打开工程运行
bin\godot.windows.editor.dev.x86_64.console.exe -w --path d:\OpenSource\GodotPy\Demo

直接打开工程编辑
bin\godot.windows.editor.dev.x86_64.console.exe -w --path d:\OpenSource\GodotPy\Demo -e


实现coroutine，先看用例
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

    print(OS.get_time())
    yield WaitForSeconds(3)
    print(OS.get_time())

game_mgr.co_mgr.start(co_print_number())
```
coroutine是用Unity3D的时候，非常喜欢的一个机制，很多小的任务，用timer太麻烦，还有一些精确到帧的任务，都可以用coroutine来做。比如等一帧，等几帧，或者等到某个前置条件成立。



