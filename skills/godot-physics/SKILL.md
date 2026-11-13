---
名称: godot-physics
描述: 适用于刚体、区域、碰撞层和射线投射的Godot物理技能。
允许使用的工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Godot 物理技能

Godot引擎的物理系统实现。

## 概述

此技能提供在Godot中实现基于物理的游戏玩法的能力。

## 功能

- 配置 RigidBody2D/3D（刚体2D/3D）
- 设置碰撞层和遮罩
- 实现射线投射和形状投射
- 处理 Area2D/3D（区域2D/3D）触发器
- 配置物理材质

## 使用模式

```gdscript
extends RigidBody2D

func _physics_process(delta):
    var space_state = get_world_2d().direct_space_state
    var query = PhysicsRayQueryParameters2D.create(position, target)
    var result = space_state.intersect_ray(query)
```

## 参考资料

- [Godot 物理](https://docs.godotengine.org/en/stable/tutorials/physics/)
