---
名称: godot-genre-sports
描述: "用于体育游戏（如FIFA、NBA 2K、Rocket League、Tony Hawk）的专家蓝图，涵盖基于物理的球体交互、团队AI阵型、上下文输入和广播相机系统。在构建足球、篮球、曲棍球、赛车运动或街机体育游戏时使用。关键词：球体物理、马格努斯效应、阵型AI、团队战术、上下文控制、转向行为。"
---

# 类型: 体育

## 可用脚本

### [sports_ball_physics.gd](scripts/sports_ball_physics.gd)
专家级球体物理，包括阻力、马格努斯效应（曲线）和适当的反弹处理。

## 核心循环
1.  **控制**: 玩家或AI控制球/冰球
2.  **移动**: 玩家避开对手（带球、传球）
3.  **射门**: 玩家尝试得分（射门、扣篮）
4.  **防守**: 对方球队试图抢断或阻挡
5.  **得分**: 时间结束后，分数决定胜者

## 体育游戏中永远不要做的事

- **永远不要将球父级到玩家变换** — 球必须是基于物理的，不是子节点。父级化会导致磁吸感，不真实。使用 `apply_central_impulse()` 进行带球触球。
- **永远不要让所有AI追逐球** — 幼儿园足球问题。使用阵型槽位：只有1-2名球员压迫球，其他球员覆盖空间/标记对手。
- **永远不要使用完美即时守门员反射** — 添加反应时间延迟（0.2-0.5秒）和基于射门速度的错误率。即时反应不公平且令人沮丧。
- **永远不要忽略玩家移动的动画根运动** — 体育游戏需要真实的动量/转向。传送到动画结束位置会破坏感觉。使用 `AnimationTree` 根运动。
- **永远不要对玩家身体使用单个碰撞形状** — 头、躯干、腿需要单独的命中框，以实现真实的球接触（头球 vs 脚射）。
- **永远不要让球穿过门柱** — 对快速移动的球使用连续碰撞检测（`continuous_cd`）。标准离散物理在高速时会导致隧道效应。

---

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 物理 | `physics-bodies`, `vehicle-wheel-3d` | 球反弹、摩擦、玩家碰撞 |
| 2. AI | `steering-behaviors`, `godot-state-machine-advanced` | 阵型、标记、群集 |
| 3. 动画 | `godot-animation-tree-mastery` | 混合奔跑、射门、抢断 |
| 4. 输入 | `input-mapping` | 上下文按钮（传球/抢断共享按钮） |
| 5. 相机 | `godot-camera-systems` | 动态广播视图、动作缩放 |

## 架构概述

### 1. 球（物理核心）
最重要的对象。必须感觉正确。

```gdscript
# ball.gd
extends RigidBody3D

@export var drag_coefficient: float = 0.5
@export var magnus_effect_strength: float = 2.0

func _integrate_forces(state: PhysicsDirectBodyState3D) -> void:
    # 应用空气阻力
    var velocity = state.linear_velocity
    var speed = velocity.length()
    var drag_force = -velocity.normalized() * (drag_coefficient * speed * speed)
    state.apply_central_force(drag_force)
    
    # 马格努斯效应（曲线）
    var spin = state.angular_velocity
    var magnus_force = spin.cross(velocity) * magnus_effect_strength
    state.apply_central_force(magnus_force)
```

### 2. 团队AI（阵型）
AI球员不只是跑向球。他们跑到相对于球/场地的*位置*。

```gdscript
# team_manager.gd
extends Node

enum Strategy { ATTACK, DEFEND }
var current_strategy: Strategy = Strategy.DEFEND
var formation_slots: Array[Node3D] # 标记父级到“阵型锚点”

func update_tactics(ball_pos: Vector3) -> void:
    # 移动整个阵型锚点
    formation_anchor.position = lerp(formation_anchor.position, ball_pos, 0.5)
    
    # 分配最佳球员到每个槽位
    for player in players:
        var best_slot = find_closest_slot(player)
        player.set_target(best_slot.global_position)
```

### 3. 比赛管理器
裁判逻辑。

```gdscript
# match_manager.gd
var score_team_a: int = 0
var score_team_b: int = 0
var match_timer: float = 300.0
enum State { KICKOFF, PLAYING, GOAL, END }

func goal_scored(team: int) -> void:
    if team == 0: score_team_a += 1
    else: score_team_b += 1
    current_state = State.GOAL
    play_celebration()
    await get_tree().create_timer(5.0).timeout
    reset_positions()
    current_state = State.KICKOFF
```

## 关键机制实现

### 上下文输入
“A”按钮根据上下文做不同的事情。

```gdscript
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("action_main"):
        if has_ball:
            pass_ball()
        elif is_near_ball:
            slide_tackle()
        else:
            switch_player()
```

### 转向行为
用于自然移动（寻找、逃离、到达）。

```gdscript
func seek(target_pos: Vector3) -> Vector3:
    var desired_velocity = (target_pos - global_position).normalized() * max_speed
    var steering = desired_velocity - velocity
    return steering.limit_length(max_force)
```

## Godot特定提示

*   **NavigationServer3D**: 对于避开障碍物（其他球员/裁判）至关重要。
*   **AnimationTree (BlendSpace2D)**: 对体育游戏至关重要。您需要平滑混合空闲 -> 行走 -> 慢跑 -> 冲刺在所有方向。
*   **PhysicsMaterial**: 仔细调整球和场地碰撞器的 `bounce` 和 `friction`。

## 常见陷阱

1.  **AI聚集**: 所有22名球员跑向球（幼儿园足球）。**修复**: 使用阵型槽位。只有1-2名球员“压迫”球；其他球员覆盖空间。
2.  **磁吸球**: 球完美粘在球员上。**修复**: 使用“带球”机制，球员通过物理方式将球稍微踢向前方，而不是父级化它。
3.  **不公平守门员**: 守门员即时反应。**修复**: 添加“反应时间”延迟和基于射门速度/统计的“错误率”。


## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
