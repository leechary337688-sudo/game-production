---
名称: godot-genre-battle-royale
描述: "专家蓝图用于战斗皇家游戏，包括缩小的区域/风暴机制（基于阶段、伤害缩放）、大规模网络（相关性、滴答率优化）、部署系统（飞机、自由落体、降落伞）、战利品生成（加权表、稀有度）、以及性能优化（LOD、遮挡剔除、对象池）。用于多人在线生存游戏或最后一人站立模式。触发关键词: battle_royale, zone_shrink, storm_damage, deployment_system, loot_spawn, networking_optimization, relevancy_system, snapshot_interpolation."
---

# 类型: 战斗皇家

专家蓝图用于战斗皇家游戏，包括区域机制、大规模网络和生存游戏玩法。

## 永不这样做

- **永不每帧同步所有100名玩家** — 使用相关性系统：只同步视觉范围内的玩家。远处的玩家以4Hz更新，附近的以20Hz+更新。
- **永不使区域中心完全随机** — 新圆圈必须与旧圆圈显著重叠，否则玩家会传送。限制偏移为 `当前半径 - 目标半径`。
- **永不使用客户端侧击中检测** — 客户端说“我朝方向X射击”，服务器验证“是否击中？”。防止作弊。
- **永不生成战利品时不使用池化** — 1000+战利品项目导致GC尖峰。池化战利品拾取并重用实例。
- **永不为远处玩家忘记VisibilityNotifier3D** — 禁用 `_process()` 和 AnimationPlayer 对于在背后或远处的玩家。节省60-80% CPU。
---

## 可用脚本

> **强制性**：在实现相应模式之前阅读适当的脚本。

### [kill_feed_bus.gd](scripts/kill_feed_bus.gd)
全局淘汰信号总线，带有比赛统计跟踪。UI/日志记录的单发射点，为终局总结排序杀手排名。

### [storm_system.gd](scripts/storm_system.gd)
动态区域缩小与伤害插值。平滑调整中心/半径，按区域大小缩放伤害以增强终局强度。

---

## 核心循环
1.  **部署**：玩家从空中载具选择着陆点。
2.  **战利品**：玩家搜刮武器和护甲。
3.  **移动**：玩家跑到安全区域以避免受到伤害。
4.  **交战**：玩家与他们遇到的其他玩家战斗。
5.  **生存**：玩家尝试成为最后一人站立。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 网络 | `godot-multiplayer-networking` | 权威服务器，延迟补偿 |
| 2. 地图 | `godot-3d-world-building`, `level-of-detail` | 大地形，分块，远处的树木 |
| 3. 物品 | `godot-inventory-system` | 管理背包，附件，护甲 |
| 4. 战斗 | `shooter-mechanics`, `ballistics` | 弹道物理，伤害计算 |
| 5. 逻辑 | `game-manager` | 管理风暴/区域状态 |

## 架构概览

### 1. 区域管理器（风暴）
管理缩小的安全区域。

```gdscript
# zone_manager.gd
extends Node

@export var phases: Array[ZonePhase]
var current_phase_index: int = 0
var current_radius: float = 2000.0
var target_radius: float = 2000.0
var center: Vector2 = Vector2.ZERO
var target_center: Vector2 = Vector2.ZERO
var shrink_speed: float = 0.0

func start_next_phase() -> void:
    var phase = phases[current_phase_index]
    target_radius = phase.end_radius
    # 在新半径内选择新中心，但要尊重旧圆圈
    var random_angle = randf() * TAU
    var max_offset = current_radius - target_radius
    var offset = Vector2.RIGHT.rotated(random_angle) * (randf() * max_offset)
    target_center = center + offset
    
    shrink_speed = (current_radius - target_radius) / phase.shrink_time

func _process(delta: float) -> void:
    if current_radius > target_radius:
        current_radius -= shrink_speed * delta
        center = center.move_toward(target_center, (shrink_speed * delta) * (center.distance_to(target_center) / (current_radius - target_radius)))
```

### 2. 战利品生成器
高效填充世界。

```gdscript
# loot_manager.gd
func spawn_loot() -> void:
    for spawn_point in get_tree().get_nodes_in_group("loot_spawns"):
        if randf() < spawn_point.spawn_chance:
            var item_id = loot_table.roll_item()
            var loot_instance = loot_scene.instantiate()
            loot_instance.setup(item_id)
            add_child(loot_instance)
```

### 3. 部署系统
从飞机过渡到地面。

```gdscript
# player_controller.gd
enum State { IN_PLANE, FREEFALL, PARACHUTE, GROUNDED }

func _physics_process(delta: float) -> void:
    match current_state:
        State.FREEFALL:
            velocity.y = move_toward(velocity.y, -50.0, gravity * delta)
            move_and_slide()
            if position.y < auto_deploy_height:
                deploy_parachute()
```

## 关键机制实现

### 区域伤害
检查玩家是否在圆圈外。

```gdscript
func check_zone_damage() -> void:
    var dist = Vector2(global_position.x, global_position.z).distance_to(ZoneManager.center)
    if dist > ZoneManager.current_radius:
        take_damage(ZoneManager.dps * delta)
```

### 网络优化
你不能每帧同步100名玩家。
*   **相关性**：只发送视觉范围内玩家的更新。
*   **频率**：更新远处的玩家以4Hz，附近的以20Hz+（服务器滴答率）。
*   **快照插值**：客户端缓冲头部以平滑播放。

## Godot特定提示

*   **MultiplayerSynchronizer**：使用 `replication_interval` 降低远处对象的带宽。
*   **VisibilityNotifier3D**：关键。禁用 `_process` 和 AnimationPlayer 对于在你背后或远处的玩家。
*   **遮挡剔除**：对于有建筑物的大地图至关重要。烘焙遮挡数据。
*   **HLOD**：使用层次级别细节对于地形和大型结构。

## 常见陷阱

1.  **太多战利品**：太多战利品导致延迟。**修复**：使用对象池对于战利品拾取。
2.  **营地**：玩家永远隐藏。**修复**：区域强制移动。此外，反营地机制如“扫描揭示”（可选）。
3.  **作弊**：客户端侧击中检测。**修复**：权威服务器逻辑。客户端说“我朝方向X射击”，服务器计算“是否击中？”。


## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
