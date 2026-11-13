---
name: godot-genre-racing
description: "赛车游戏专家蓝图，包括车辆物理（VehicleBody3D、悬挂、摩擦）、检查点系统（防止捷径）、橡皮筋AI（保持比赛竞争性）、漂移机制（减少摩擦、退出时加速）、相机感觉（速度增加时FOV增加、运动模糊）和UI（速度表、圈计时器、小地图）。适用于街机赛车、卡丁车赛车或真实模拟。触发关键词：racing_game、vehicle_physics、checkpoint_system、rubber_banding、drifting_mechanics、camera_feel。"
---

# 类型：赛车

赛车游戏专家蓝图，平衡物理、竞争和速度感。

## 永远不要做

- **永远不要刚性相机附着** — 相机锁定到汽车会导致晕动症。使用带有轻微延迟的lerp实现平滑跟随。
- **永远不要忽略速度感** — 随着速度增加FOV，添加相机抖动、风线、运动模糊。隧道视野破坏沉浸感。
- **永远不要使物理过于真实** — “漂浮”的街机感觉通常比模拟更有趣。增加重力2-3倍，调整车轮摩擦。
- **永远不要忘记检查点** — 没有验证，玩家会利用捷径。强制执行检查点序列以完成圈数。
- **永远不要忽略橡皮筋效应** — AI太远领先或落后会使比赛无聊。根据玩家距离动态调整AI速度。
---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [spline_ai_controller.gd](scripts/spline_ai_controller.gd)
基于Path3D的赛车AI。将位置投影到曲线上，计算前瞻以转向，根据目标速度与速度应用油门。

---

## 核心循环
1.  **比赛**：玩家在赛道上控制车辆。
2.  **竞争**：玩家超越对手或击败时间。
3.  **升级**：玩家赚取货币/点数购买零件/汽车。
4.  **调整**：玩家调整车辆统计（抓地力、加速度）。
5.  **掌握**：玩家学习赛道布局和最佳线路。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 物理 | `physics-bodies`、`vehicle-wheel-3d` | 汽车移动、悬挂、碰撞 |
| 2. AI | `navigation`、`steering-behaviors` | 对手路径查找、橡皮筋效应 |
| 3. 输入 | `input-mapping` | 模拟转向、加速、刹车 |
| 4. UI | `progress-bars`、`labels` | 速度表、圈计时器、小地图 |
| 5. 感觉 | `camera-shake`、`godot-particles` | 速度感知、轮胎烟雾、火花 |

## 架构概述

### 1. 车辆控制器
处理移动的物理。

```gdscript
# car_controller.gd
extends VehicleBody3D

@export var max_torque: float = 300.0
@export var max_steering: float = 0.4

func _physics_process(delta: float) -> void:
    steering = lerp(steering, Input.get_axis("right", "left") * max_steering, 5 * delta)
    engine_force = Input.get_axis("back", "forward") * max_torque
```

### 2. 检查点系统
追踪进度和防止作弊的关键。

```gdscript
# checkpoint_manager.gd
extends Node

var checkpoints: Array[Area3D] = []
var current_checkpoint_index: int = 0
signal lap_completed

func _on_checkpoint_entered(body: Node3D, index: int) -> void:
    if index == current_checkpoint_index + 1:
        current_checkpoint_index = index
    elif index == 0 and current_checkpoint_index == checkpoints.size() - 1:
        complete_lap()
```

### 3. 比赛管理器
高级状态机。

```gdscript
# race_manager.gd
enum State { COUNTDOWN, RACING, FINISHED }
var current_state: State = State.COUNTDOWN

func start_race() -> void:
    # 3.. 2.. 1.. GO!
    await countdown()
    current_state = State.RACING
    start_timer()
```

## 关键机制实现

### 漂移
街机漂移通常涉及伪造物理。减少摩擦或应用横向力。

```gdscript
func apply_drift_mechanic() -> void:
    if is_drifting:
        # 减少横向牵引力
        wheel_friction_slip = 1.0 
        # 退出时添加轻微向前加速
    else:
        wheel_friction_slip = 3.0 # 高抓地力
```

### 橡皮筋效应AI
通过根据玩家距离调整AI速度来保持比赛竞争性。

```gdscript
func update_ai_speed(ai_car: VehicleBody3D, player: VehicleBody3D) -> void:
    var dist = ai_car.global_position.distance_to(player.global_position)
    if ai_car_is_ahead_of_player(ai_car, player):
        ai_car.max_speed = base_speed * 0.9 # 减速
    else:
        ai_car.max_speed = base_speed * 1.1 # 加速
```

## Godot特定提示

*   **VehicleBody3D**：Godot内置的车辆物理节点。对于街机游戏来说不错，但对于模拟游戏，您可能想要自定义RayCast悬挂。
*   **Path3D / PathFollow3D**：适用于简单的AI交通或固定路径赛车（轨道上）。
*   **AudioBus**：在AudioListener上使用`Doppler`效果来实现真实的通过声音。
*   **SubViewport**：用于后视镜或小地图纹理。

## 常见陷阱

1.  **漂浮物理**：汽车感觉像在冰上。**修复**：增加重力比例（2-3倍）并调整车轮摩擦。真实感 < 趣味性。
2.  **坏相机**：相机刚性附着到汽车。**修复**：使用带有`lerp`脚本的`Marker3D`以轻微延迟平滑跟随汽车。
3.  **隧道视野**：没有速度感。**修复**：随着速度增加FOV，添加相机抖动、风线和运动模糊。

## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
