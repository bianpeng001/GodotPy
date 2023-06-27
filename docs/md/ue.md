[TOC]

# UE学习笔记

## UnrealBuildTool
构造工具是用C#实现的, 非常方便好用.

执行的流程为:
```
UnrealBuildTool\Executors\ParallelExecutor.cs:293
async Task<ExecuteResults> RunAction(LinkedAction Action, ManagedProcessGroup ProcessGroup, CancellationToken CancellationToken)
```
开一个子进程来执行对应的命令行

比如: 编译cpp文件, 
```
Action.CommandPath   => cl.exe
Action.CommandArcuments => @G:\UEWorks\DSDemo\Intermediate\Build\Win64\x64\UnrealEditor\Development\DSDemo\DSDemoCharacter.cpp.obj.response
```
这里的.response文件, 是命令行的参数

这里会选一个Executor
```
ActionGraph.cs:349
ActionExecutor SelectExecutor(BuildConfiguration BuildConfiguration, int ActionCount, List<TargetDescriptor> TargetDescriptors, ILogger Logger)
```

## GC
标记清除

## TWeakObjectPtr<T>
实现很简单, 构思巧妙

## Blueprint
蓝图做一些简单的参数化, 是挺好用的. 
但是没有发现大规模使用的时候, 有啥优势, 尤其是相对于c++, 更有甚者lua.

## Pawn, Controller
这几个之间的关系, 算是UE的一个设计思路.

## Network
包括同步和RPC

## U++
有元信息的部分, 虽然还是c++代码, 但实际上认为是U++, UE加了不少反射的功能. 赋予了大量功能.
最直接的一条, 当Actor销毁的时候, UPROPERTY的字段里面会被通知到.

## Builtin Types

1. TArray: 最常用且好用的
2. FString: 

## Script
lua vs python, or c#


