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
```c++
    // 加载
    Ref<PackedScene> res = ResourceLoader::load(path);
    // 实例化
    auto node = Object::cast_to<Node3D>(res->instantiate(PackedScene::GEN_EDIT_STATE_DISABLED));
    // 加入场景树
    auto st = SceneTree::get_singleton();
    auto scene = st->get_current_scene();
    scene->add_child(node);
```

对node，set_process，才能收到process信号。set_process_input，才能收到input事件。

godot editor, 有一定的remote功能，即在编辑器里面启动后，能对scenetree里面的内容，在编辑器和运行时之间有一些反馈。

node, 只提供了基础功能。node3d才有transform的信息。

没有提供组件的开发模式。所以都是用节点来完成的。比如这个python的脚本，我是放了一个FPyObject的节点来提供脚本运行。

ProjectSetting里面有很多宝藏

gltb格式在导入后，最好把mesh单独保存，这样才能被单独读取。

UI开发

Python的Py_INCREF, Py_DECREF，这两项的使用，有一些注意点。目前从容器中Get出来的值是borrowed reference，即，不需要修改引用计数。
但是，PyObject_CallMethod返回值，如果不需要保留，则必须减掉引用计数。

