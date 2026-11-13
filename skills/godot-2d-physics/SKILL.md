---
name: godot-2d-物理
description: "Godot 2D物理的专家模式，包括碰撞层/掩码、Area2D触发器、raycasting和PhysicsDirectSpaceState2D查询。用于实现碰撞检测、触发区域、视线系统或手动物理查询。触发关键词：CollisionShape2D, CollisionPolygon2D, collision_layer, collision_mask, set_collision_layer_value, set_collision_mask_value, Area2D, body_entered, body_exited, RayCast2D, force_raycast_update, PhysicsPointQueryParameters2D, PhysicsShapeQueryParameters2D, direct_space_state, move_and_collide, move_and_slide."
---

# 2D 物理

Godot 2D中碰撞检测、触发器和raycasting的专家指导。

## 绝对不要做的事

- **绝对不要缩放CollisionShape2D节点** — 使用编辑器中的形状手柄，而不是Node2D的scale属性。缩放会导致不可预测的物理行为和错误的碰撞法线。
- **绝对不要混淆collision_layer和collision_mask** — Layer = "我是什么？", Mask = "我检测什么？". 将两者设置为相同值几乎总是错误的。
- **使用move_and_slide()时绝对不要乘以delta乘以速度** — move_and_slide()在计算中自动包含时间步长。只将重力（加速度）乘以delta。
- **对于手动raycast，绝对不要忘记调用force_raycast_update()** — Raycast每物理帧更新一次。如果在帧中更改target_position/rotation，必须调用force_raycast_update()。
- **绝对不要每帧使用get_overlapping_bodies()** — 使用body_entered/body_exited信号缓存结果。连续查询昂贵且不必要。

---

## 可用脚本

> **强制**：在实现前阅读与您用例匹配的脚本。

### [collision_setup.gd](scripts/collision_setup.gd)
程序化的层/掩码管理，带有命名层常量和调试可视化。

### [physics_query_cache.gd](scripts/physics_query_cache.gd)
PhysicsDirectSpaceState2D查询的基于帧的缓存 - 消除冗余昂贵查询。

### [custom_physics.gd](scripts/custom_physics.gd)
CharacterBody2D的自定义物理集成模式。涵盖非标准重力、力和手动步进。用于非标准物理行为。

### [physics_queries.gd](scripts/physics_queries.gd)
PhysicsDirectSpaceState2D查询模式，用于raycasting、点查询和形状查询。用于视线、地面检测或区域扫描。

---

## 碰撞层与掩码（位掩码深入探讨）

### 心智模型

```gdscript
# collision_layer (32 位): 我在哪些广播频道上传输？
# collision_mask (32 位): 我监听哪些广播频道？

# 示例: 玩家 vs 敌人
# 玩家:
#   layer = 0b0001 (频道 1: "我是玩家")
#   mask  = 0b0110 (频道 2+3: "我监听敌人和墙壁")
# 敌人:
#   layer = 0b0010 (频道 2: "我是敌人")
#   mask  = 0b0101 (频道 1+3: "我监听玩家和墙壁")
```

### 位掩码助手

```gdscript
# ✅ 好: 使用助手函数以获得清晰度
func setup_player_collision() -> void:
    # 我是层 1
    set_collision_layer_value(1, true)
    
    # 我检测层 2 (敌人) 和 3 (世界)
    set_collision_mask_value(2, true)
    set_collision_mask_value(3, true)

# ✅ 好: 用于程序化层数学的位移
func enable_layers(base_layer: int, count: int) -> void:
    var mask := 0
    for i in range(count):
        mask |= (1 << (base_layer + i - 1))
    collision_mask = mask

# ❌ 坏: 没有文档的硬编码位掩码
collision_mask = 0b110110  # 这是什么意思？！
```

### 常见模式

```gdscript
# 模式: 击中敌人但忽略其他抛射物的抛射物
# projectile.gd
extends Area2D

func _ready() -> void:
    set_collision_layer_value(4, true)   # 层 4: "抛射物"
    set_collision_mask_value(2, true)    # 掩码层 2: "敌人"
    # 结果: 抛射物不相互碰撞

# 模式: 单向平台（玩家可以从下方跳入）
# platform.gd
extends StaticBody2D

@export var one_way := true

func _ready() -> void:
    set_collision_layer_value(3, true)   # 层 3: "世界"
    if one_way:
        # 使用 Area2D + 碰撞豁免替代
        # (标准单向平台使用不同技术)
        pass
```

---

## Area2D 专家模式

### 问题: 多碰撞形状上的重复触发器

```gdscript
# ❌ 坏: 如果Area2D有多个形状，body_entered会多次触发
extends Area2D

func _ready() -> void:
    body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
    print("进入！")  # 如果Area有3个CollisionShapes，触发3次！

# ✅ 好: 使用Set跟踪唯一身体
extends Area2D

var _active_bodies := {}  # 使用字典作为Set

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body not in _active_bodies:
        _active_bodies[body] = true
        print("首次进入！")  # 只触发一次

func _on_body_exited(body: Node2D) -> void:
    _active_bodies.erase(body)
```

### 带有免疫帧的伤害-over-time

```gdscript
# lava_zone.gd
extends Area2D

@export var damage_per_tick := 5
@export var tick_rate := 0.5  # 每0.5秒伤害一次

var _damage_timers := {}  # body -> time_until_next_tick

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node2D) -> void:
    if body.has_method("take_damage"):
        _damage_timers[body] = 0.0  # 立即第一次滴答

func _on_body_exited(body: Node2D) -> void:
    _damage_timers.erase(body)

func _process(delta: float) -> void:
    for body in _damage_timers.keys():
        _damage_timers[body] -= delta
        if _damage_timers[body] <= 0.0:
            body.take_damage(damage_per_tick)
            _damage_timers[body] = tick_rate
```

---

## RayCast2D 高级用法

### 动态Raycast旋转

```gdscript
# enemy_vision.gd - 敌人看向玩家
extends CharacterBody2D

@onready var vision_ray: RayCast2D = $VisionRay

func can_see_target(target: Node2D) -> bool:
    var direction := global_position.direction_to(target.global_position)
    vision_ray.target_position = direction * 300  # 300像素范围
    vision_ray.force_raycast_update()  # 关键: 在帧中更新
    
    if vision_ray.is_colliding():
        return vision_ray.get_collider() == target
    return false
```

### 多raycast用于边缘检测

```gdscript
# platformer_controller.gd
extends CharacterBody2D

@onready var floor_front: RayCast2D = $FloorCheckFront
@onready var floor_back: RayCast2D = $FloorCheckBack

func at_ledge() -> bool:
    return floor_front.is_colliding() and not floor_back.is_colliding()

func _physics_process(delta: float) -> void:
    if at_ledge() and is_on_floor():
        # 敌人AI: 在边缘转身
        velocity.x *= -1
```

### Raycast排除

```gdscript
# 忽略特定身体（例如，自己）
func _ready() -> void:
    $RayCast2D.add_exception(self)
    $RayCast2D.add_exception($Weapon)  # 忽略附加武器碰撞器

# 重置排除
$RayCast2D.clear_exceptions()
```

---

## PhysicsDirectSpaceState2D（手动查询）

### 点查询: 点击检测

```gdscript
# 检查鼠标点击是否击中任何物理身体
func get_body_at_mouse() -> Node2D:
    var mouse_pos := get_global_mouse_position()
    var space := get_world_2d().direct_space_state
    
    var query := PhysicsPointQueryParameters2D.new()
    query.position = mouse_pos
    query.collide_with_areas = false
    query.collision_mask = 0b11111111  # 所有层
    
    var results := space.intersect_point(query, 1)  # 最大1个结果
    if results.is_empty():
        return null
    return results[0].collider
```

### 形状投射: AOE攻击

```gdscript
# 在玩家周围圆圈内的AOE伤害
func damage_nearby_enemies(center: Vector2, radius: float, damage: int) -> void:
    var space := get_world_2d().direct_space_state
    var query := PhysicsShapeQueryParameters2D.new()
    
    var circle := CircleShape2D.new()
    circle.radius = radius
    query.shape = circle
    query.transform = Transform2D(0.0, center)
    query.collision_mask = 0b0010  # 层 2: 敌人
    
    var hits := space.intersect_shape(query)
    for hit in hits:
        var enemy: Node2D = hit.collider
        if enemy.has_method("take_damage"):
            enemy.take_damage(damage)
```

### Raycast: 即时命中武器

```gdscript
# 命中扫描武器（无抛射物）
func fire_hitscan_weapon(from: Vector2, direction: Vector2, max_range: float) -> void:
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(from, from + direction * max_range)
    query.exclude = [self]
    query.collision_mask = 0b0010  # 敌人
    
    var result := space.intersect_ray(query)
    if result:
        var hit_enemy: Node2D = result.collider
        var hit_point: Vector2 = result.position
        
        spawn_hit_effect(hit_point)
        if hit_enemy.has_method("take_damage"):
            hit_enemy.take_damage(25)
```

---

## 决策树: 碰撞检测方法

| 用例 | 方法 | 原因 |
|----------|--------|-----|
| 连续触发区域 | Area2D + 信号 | 内部记忆，信号高效 |
| 一次性拾取（硬币） | Area2D + 进入时queue_free() | 简单，自动清理 |
| 视线检查 | RayCast2D | 高效，内置 |
| 点击选择单位 | PhysicsPointQueryParameters2D | 单次查询，无永久节点 |
| AOE法术 | PhysicsShapeQueryParameters2D | 一次性查询，灵活形状 |
| 即时命中武器 | PhysicsRayQueryParameters2D | 命中扫描，无抛射物物理 |
| 平台地面检查 | RayCast2D 或 向下raycast | 精确边缘检测 |

---

## 边界情况

### _ready()中的碰撞

```gdscript
# ❌ 坏: Raycast在_ready()中不工作（物理未初始化）
func _ready() -> void:
    if $RayCast2D.is_colliding():  # 总是false！
        print("击中某物")

# ✅ 好: 等待物理帧
func _ready() -> void:
    await get_tree().physics_frame
    if $RayCast2D.is_colliding():
        print("击中某物")
```

### Area2D 不检测 CharacterBody2D

```gdscript
# 问题: CharacterBody2D 默认 collision_layer = 0
# 解决方案: 显式设置层

# character.gd
func _ready() -> void:
    collision_layer = 0b0001  # 层 1: 玩家
```

### Raycast 击中背面

```gdscript
# Raycast 击中碰撞形状的前后两面
# 要raycast单向（仅前面），使用 Area2D 监控
```

---

## 性能

```gdscript
# ✅ 好: 不需要时禁用raycast
func _ready() -> void:
    $OptionalRaycast.enabled = false

func check_vision() -> void:
    $OptionalRaycast.enabled = true
    $OptionalRaycast.force_raycast_update()
    var sees_player := $OptionalRaycast.is_colliding()
    $OptionalRaycast.enabled = false
    return sees_player

# ❌ 坏: 对于很少使用的检查，始终开启raycast
# 对于每秒一次的视线检查，保持 RayCast2D.enabled = true
```


## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
