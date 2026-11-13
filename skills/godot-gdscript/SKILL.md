---
name: godot-gdscript
description: 用于Godot引擎的GDScript编程技能，包括信号、协程和性能优化。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Godot GDScript 技能

用于Godot引擎开发的GDScript编程。

## 概述

此技能提供了使用GDScript（Godot类似Python的脚本语言）实现游戏逻辑的能力。

## 能力范围

### 语言特性
- 类和继承
- 信号和连接
- 使用await的协程
- 静态类型

### 节点交互
- 场景树导航
- 节点引用
- 组管理
- 信号连接

### 性能优化
- 对象池模式
- 缓存节点引用
- 优化循环
- 使用类型化数组

### 最佳模式
- 状态机
- 单例（自动加载）
- 资源管理
- 导出变量

## 先决条件

- Godot 4.0+
- GDScript知识

## 使用模式

### 信号模式

```gdscript
class_name Player extends CharacterBody2D

signal health_changed(new_health: int)
signal died

@export var max_health: int = 100
var health: int = max_health

func take_damage(amount: int) -> void:
    health = max(0, health - amount)
    health_changed.emit(health)
    if health <= 0:
        died.emit()
```

### 协程模式

```gdscript
func spawn_enemies() -> void:
    for i in range(10):
        spawn_enemy()
        await get_tree().create_timer(1.0).timeout
```

## 最佳实践

1. 使用静态类型
2. 在_ready中缓存节点引用
3. 使用信号进行解耦
4. 优先使用组合而非继承
5. 使用内置分析器进行性能分析

## 参考资料

- [GDScript 文档](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/)
