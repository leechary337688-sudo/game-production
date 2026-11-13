---
名称: godot-genre-tower-defense
描述: "塔防游戏（如Bloons TD、Kingdom Rush、Fieldrunners）的专家蓝图，覆盖波管理、塔目标逻辑、路径算法、经济平衡和迷宫机制。在构建塔防、线路防御或塔放置策略游戏时使用。关键词：塔防、波生成器、路径查找、目标优先级、迷宫、NavigationServer烘焙。"
---

# 类型: 塔防游戏

战略放置、资源管理和难度递增定义了塔防游戏。

## 核心循环
1.  **准备**: 用可用货币建造/升级塔
2.  **波**: 敌人生成并沿路径向目标移动
3.  **防御**: 塔自动瞄准并伤害敌人
4.  **奖励**: 击杀给予货币
5.  **升级**: 波的难度/复杂度增加

## 塔防游戏中永远不要做的事

- **永远不要让所有塔同样可行** — 如果狙击手和机枪的DPS相同，就没有战略选择。每个塔必须有明显的专长（范围伤害、减速、穿甲、防空）。
- **永远不要使用同步NavigationServer烘焙进行迷宫生成** — `NavigationRegion2D.bake_navigation_polygon()`会阻塞主线程。使用`NavigationServer2D.get_maps()` + 工作线程或固定路径。
- **永远不要让玩家完全封锁出口路径** — 在迷宫塔防中，在放置塔之前验证`NavigationServer2D.map_get_path(start, goal)`。空路径 = 非法建造。
- **永远不要每一帧都使用`Area2D.get_overlapping_bodies()`** — 500个敌人 × 60fps = 30k碰撞检查。将`bodies_entered`存储在数组中，在`body_exited`时移除。查询一次。
- **永远不要让早期波感觉像繁忙工作** — 前三波应该引入机制，而不是无聊。将计时器设为50%或给予“提前呼叫”奖励跳过。
- **永远不允许没有追赶机制的死亡螺旋** — 1个敌人逃脱 → 钱更少 → 下一波更难 → 不可避免的失败。添加存款利息或离散波难度。

---

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 网格/路径 | `godot-tilemap-mastery`, `navigation-2d` | 定义敌人行走和塔建造的位置 |
| 2. 塔 | `math-geometry`, `area-2d` | 范围检查、旋转、弹道预测 |
| 3. 敌人 | `path-following`, `steering-behaviors` | 沿路径移动 |
| 4. 管理 | `state-machines`, `loop-management` | 波生成逻辑、游戏阶段 |
| 5. 用户界面 | `ui-system`, `drag-and-drop` | 建造塔、检查状态 |

## 架构概述

### 1. 波管理器
处理敌人波的定时和Godot组合。

```gdscript
# wave_manager.gd
extends Node

signal wave_started(wave_index: int)
signal wave_cleared
signal enemy_spawned(enemy: Node2D)

@export var waves: Array[Resource] # 波定义资源的数组
var current_wave_index: int = 0
var active_enemies: int = 0

func start_next_wave() -> void:
    if current_wave_index >= waves.size():
        print("所有波已清除！")
        return
        
    var wave_data = waves[current_wave_index]
    wave_started.emit(current_wave_index)
    _spawn_wave(wave_data)
    current_wave_index += 1

func _spawn_wave(wave: WaveResource) -> void:
    for group in wave.groups:
        await get_tree().create_timer(group.delay).timeout
        for i in group.count:
            var enemy = group.enemy_scene.instantiate()
            add_child(enemy)
            active_enemies += 1
            enemy.tree_exiting.connect(_on_enemy_died)
            await get_tree().create_timer(group.interval).timeout

func _on_enemy_died() -> void:
    active_enemies -= 1
    if active_enemies <= 0:
        wave_cleared.emit()
```

### 2. 塔逻辑（状态机）
塔作为自主代理。

*   **状态**: `Idle`, `AcquireTarget`, `Attack`, `Cooldown`.
*   **目标优先级**: `First`, `Last`, `Strongest`, `Weakest`, `Closest`.

```gdscript
# tower.gd
extends Node2D

var targets_in_range: Array[Node2D] = []
var current_target: Node2D

func _physics_process(delta: float) -> void:
    if current_target == null or not is_instance_valid(current_target):
        _acquire_target()
    
    if current_target:
        _rotate_turret(current_target.global_position)
        if can_fire():
            fire_projectile()

func _acquire_target() -> void:
    # 示例：目标沿路径进度最大的敌人
    var max_progress = -1.0
    for enemy in targets_in_range:
        if enemy.progress > max_progress:
            current_target = enemy
            max_progress = enemy.progress
```

### 3. 路径查找变体

#### A. 固定路径（Kingdom Rush风格）
敌人遵循预定义的`Path2D`。
*   **实现**: 将`PathFollow2D`作为敌人的父节点。
*   **优点**: 确定性，易于平衡，优化。
*   **缺点**: 玩家在塑造路径方面的代理权较少。

#### B. 迷宫（Fieldrunners风格）
玩家建造塔来阻挡/重定向敌人。
*   **实现**: 敌人使用`NavigationAgent2D`。塔更新`NavigationRegion2D`（在单独线程上烘焙）。
*   **优点**: 战略深度高。
*   **缺点**: 计算量大，需要反阻塞逻辑（不要让玩家封死出口）。

## 关键机制实现

### 目标数学（弹道预测）
要击中移动目标，必须预测它将在哪里。

```gdscript
func get_predicted_position(target: Node2D, projectile_speed: float) -> Vector2:
    var to_target = target.global_position - global_position
    var time_to_hit = to_target.length() / projectile_speed
    return target.global_position + (target.velocity * time_to_hit)
```

### 经济
资金管理是次要核心循环。
*   **击杀奖励**: 成功的直接反馈。
*   **利息/收入**: 奖励保存资金（风险/回报）。
*   **提前呼叫**: 提前开始下一波的额外奖金。

## 常见陷阱

1.  **死亡螺旋**: 如果玩家漏掉一个敌人，他们会失去金钱/生命，使得下一波更难，导致不可避免的失败。**修复**: 追赶机制或离散波难度。
2.  **无用塔**: 每个塔类型必须有明显的专长（范围伤害、减速、穿甲、防空）。
3.  **路径阻塞**: 在迷宫游戏中，确保玩家不能完全封锁出口路径。使用`NavigationServer2D.map_get_path`在建造前验证放置。

## Godot特定提示

*   **物理层**: 将敌人放在特定层（如层2），塔的“范围”区域放在不同的掩码上，以避免塔检测到彼此或墙壁。
*   **Area2D性能**: 对于大量敌人，如果可能，避免每帧都使用`monitorable/monitoring`。如果敌人数量 > 500，使用`PhysicsServer2D`查询进行优化。
*   **对象池**: 对于弹道和敌人至关重要，以避免激烈波时的垃圾收集卡顿。

## 参考
- 主要技能: [godot-master](../godot-master/SKILL.md)
