---
name: godot-csharp
description: Godot C# 编程技能，用于 .NET 集成、脚本模式和性能优化。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Godot C# 技能

用于 Godot 引擎开发的 C# 编程。

## 概述

此技能提供了使用 C# 在 Godot 中实现游戏逻辑的能力，充分利用 .NET 集成。

## 能力

### C# 集成
- 节点类继承
- 基于属性的导出
- 信号定义
- 可调用系统

### .NET 特性
- NuGet 包
- 异步/等待模式
- LINQ 查询
- .NET 库

### 互操作性
- 从 C# 调用 GDScript
- 向 GDScript 公开
- 处理 Variant 类型
- 管理信号

### 性能
- 结构体使用
- 内存管理
- 对象池
- Span 使用

## 先决条件

- 支持 .NET 的 Godot 4.0+
- 已安装 .NET SDK
- C# IDE（VS Code, Rider）

## 使用模式

### 节点脚本

```csharp
using Godot;

public partial class Player : CharacterBody2D
{
    [Export]
    public float Speed { get; set; } = 200f;

    [Signal]
    public delegate void HealthChangedEventHandler(int newHealth);

    private int _health = 100;

    public override void _Ready()
    {
        // 初始化
    }

    public override void _PhysicsProcess(double delta)
    {
        var velocity = Vector2.Zero;
        velocity.X = Input.GetAxis("move_left", "move_right");
        velocity.Y = Input.GetAxis("move_up", "move_down");
        Velocity = velocity.Normalized() * Speed;
        MoveAndSlide();
    }
}
```

### 信号连接

```csharp
button.Pressed += OnButtonPressed;
// 或
button.Connect("pressed", Callable.From(OnButtonPressed));
```

## 最佳实践

1. 使用分部类
2. 利用 NuGet 包
3. 处理节点生命周期
4. 分析内存使用情况
5. 使用源生成器

## 参考资料

- [Godot C# 文档](https://docs.godotengine.org/en/stable/tutorials/scripting/c_sharp/)
