---
名称: unity-profiler
描述: Unity Profiler技能，用于性能分析、帧调试、内存剖析和优化工作流。
允许工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity Profiler 技能

使用Unity Profiler工具进行性能剖析和优化。

## 概述

此技能提供使用Profiler、Frame Debugger和Memory Profiler分析和优化Unity游戏性能的能力。

## 能力

### CPU剖析
- 分析帧时间
- 识别性能瓶颈
- 剖析自定义代码标记
- 处理深度剖析

### GPU剖析
- 分析渲染通道
- 剖析着色器性能
- 识别过度绘制
- 调试绘制调用

### 内存剖析
- 跟踪内存分配
- 识别内存泄漏
- 分析纹理内存
- 剖析托管堆

### 自动化分析
- 创建剖析器脚本
- 设置性能测试
- 生成报告
- 监控性能回归

## 先决条件

- Unity 2021.3+
- Profiler模块（内置）
- Memory Profiler包（可选）

## 使用模式

### 自定义剖析器标记

```csharp
using Unity.Profiling;

public class OptimizedSystem : MonoBehaviour
{
    static readonly ProfilerMarker s_UpdateMarker =
        new ProfilerMarker("MySystem.Update");

    void Update()
    {
        using (s_UpdateMarker.Auto())
        {
            // 要剖析的代码
            ProcessEntities();
        }
    }
}
```

### 性能测试

```csharp
[Test, Performance]
public void TestSpawnPerformance()
{
    Measure.Method(() =>
    {
        for (int i = 0; i < 1000; i++)
        {
            SpawnEnemy();
        }
    })
    .WarmupCount(3)
    .MeasurementCount(10)
    .Run();
}
```

## 最佳实践

1. 在目标硬件上剖析
2. 使用剖析器标记
3. 使用真实数据进行测试
4. 监控帧预算
5. 长期跟踪内存

## 参考资料

- [Profiler文档](https://docs.unity3d.com/Manual/Profiler.html)
