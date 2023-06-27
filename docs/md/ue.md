[TOC]

# UE学习笔记

## UnrealBuildTool
构造工具是用C#实现的, 非常方便好用.

执行的流程为: 为每一个Action, 创建一个Task, 异步的方式来执行.

UnrealBuildTool\Executors\ParallelExecutor.cs:193
```c#
// Create a task for every action
foreach (LinkedAction Action in InputActions)
{
    if (ExecuteTasks.ContainsKey(Action))
    {
        continue;
    }

    Task<ExecuteResults> ExecuteTask = CreateExecuteTask(Action, InputActions, ExecuteTasks, ProcessGroup, MaxProcessSemaphore, CancellationToken);
    Task LogTask = ExecuteTask.ContinueWith(antecedent => LogCompletedAction(Action, antecedent, CancellationTokenSource, ProgressWriter, TotalActions, ref NumCompletedActions, Logger), CancellationToken);

    ExecuteTasks.Add(Action, ExecuteTask);
    LogTasks.Add(LogTask);
}

Task SummaryTask = Task.Factory.ContinueWhenAll(LogTasks.ToArray(), (AntecedentTasks) => TraceSummary(ExecuteTasks, ProcessGroup, Logger), CancellationToken);
SummaryTask.Wait();
```

```
UnrealBuildTool\Executors\ParallelExecutor.cs:293
async Task<ExecuteResults> RunAction(LinkedAction Action, ManagedProcessGroup ProcessGroup, CancellationToken CancellationToken)
```
开一个子进程来执行对应的命令行

比如: 编译cpp文件, 这里的.response文件, 是命令行的参数
```
Action.CommandPath   => cl.exe
Action.CommandArcuments => @G:\UEWorks\DSDemo\Intermediate\Build\Win64\x64\UnrealEditor\Development\DSDemo\DSDemoCharacter.cpp.obj.response
```

这个是打印每一个任务的简报

UnrealBuildTool\Executors\ParallelExecutor.cs:317
```c#
void LogCompletedAction(LinkedAction Action, Task<ExecuteResults> ExecuteTask, CancellationTokenSource CancellationTokenSource, ProgressWriter ProgressWriter, int TotalActions, ref int NumCompletedActions, ILogger Logger)
```

这里是创建任务的时候, 有考虑前置依赖任务

UnrealBuildTool\Executors\ParallelExecutor.cs:
```c#
Task<ExecuteResults> CreateExecuteTask(LinkedAction Action, List<LinkedAction> InputActions, Dictionary<LinkedAction, Task<ExecuteResults>> ExecuteTasks, ManagedProcessGroup ProcessGroup, SemaphoreSlim MaxProcessSemaphore, CancellationToken CancellationToken)
```
这里会选一个Executor
```
ActionGraph.cs:349
ActionExecutor SelectExecutor(BuildConfiguration BuildConfiguration, int ActionCount, List<TargetDescriptor> TargetDescriptors, ILogger Logger)
```

## GC
标记清除

## TWeakObjectPtr<T>
实现很简单, 构思巧妙. 之所以说他简单, 因为这样的结构, 你肯定自己实现过好多次了. 之所以巧妙, 因为真的很好用.

## Blueprint
蓝图做一些简单的参数化, 是挺好用的. 
但是没有发现大规模使用的时候, 有啥优势, 尤其是相对于c++, 比lua就差更远了.

可视化的工具, 除了可视, 就都是减分了.

## Pawn, Controller
这几个之间的关系, 算是UE的一个设计思路.

## Network

### 同步

### RPC

## U++
有元信息的部分, 虽然还是C++代码, 但实际上认为是U++, UE加了不少反射的功能. 赋予了大量功能.
最直接的一条, 当Actor销毁的时候, UPROPERTY的字段里面会被通知到.

## Some Classes
* TArray: 最常用且好用的
* FString: 

## Script

### lua

### python

###  c#


