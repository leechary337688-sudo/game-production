---
名称: unity-ecs
描述: Unity DOTS/ECS技能，用于面向数据的设计、作业系统、Burst编译器优化和高性能游戏系统开发。
允许使用的工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity ECS 技能

面向数据的技术栈（DOTS）和Unity实体组件系统开发。

## 概述

本技能提供使用Unity的实体组件系统、作业系统和Burst编译器实现高性能游戏系统的能力。

## 能力

### 实体组件系统
- 创建 IComponentData 结构体
- 实现 ISystem 和 SystemBase
- 管理实体原型
- 处理实体查询和批处理

### 作业系统
- 创建 IJob 实现
- 实现 IJobEntity 以处理实体
- 处理作业依赖关系和调度
- 管理原生容器

### Burst 编译器
- 为作业启用 Burst 编译
- 使用 SIMD 指令优化
- 分析 Burst 编译后的代码
- 处理 Burst 的限制

### 混合工作流
- 将 ECS 与 GameObject 桥接
- 使用伴随组件
- 将现有系统转换为 ECS
- 实现烘焙工作流

## 先决条件

- 推荐 Unity 2022.3+
- Entities 包 (1.0+)
- Mathematics 包
- Burst 包

## 使用模式

### 组件数据

```csharp
public struct MoveSpeed : IComponentData
{
    public float Value;
}

public struct Velocity : IComponentData
{
    public float3 Value;
}
```

### 系统实现

```csharp
[BurstCompile]
public partial struct MovementSystem : ISystem
{
    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        float deltaTime = SystemAPI.Time.DeltaTime;

        foreach (var (transform, velocity) in
            SystemAPI.Query<RefRW<LocalTransform>, RefRO<Velocity>>())
        {
            transform.ValueRW.Position += velocity.ValueRO.Value * deltaTime;
        }
    }
}
```

### 作业示例

```csharp
[BurstCompile]
public partial struct MovementJob : IJobEntity
{
    public float DeltaTime;

    void Execute(ref LocalTransform transform, in Velocity velocity)
    {
        transform.Position += velocity.Value * DeltaTime;
    }
}
```

## 最佳实践

1. 保持组件小巧且功能聚焦
2. 对所有性能关键的作业使用 Burst
3. 批处理实体操作
4. 最小化结构性更改
5. 使用实体调试器进行分析

## 参考资料

- [Unity DOTS 文档](https://docs.unity3d.com/Packages/com.unity.entities@latest)
- [Burst 手册](https://docs.unity3d.com/Packages/com.unity.burst@latest)
