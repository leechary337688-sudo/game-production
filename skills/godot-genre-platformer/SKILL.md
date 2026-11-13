---
name: godot-genre-platformer
description: "平台游戏专家蓝图，包括精确移动（缓冲跳跃、提前离地跳、可变跳跃高度）、游戏感觉优化（挤压/拉伸、粒子轨迹、相机震动）、关卡设计原则（难度曲线、检查点放置）、收集系统（进度奖励）和可访问性选项（辅助模式、可重映射控制）。基于Celeste/Hollow Knight的设计研究。触发关键词：platformer, coyote_time, jump_buffer, game_feel, level_design, precision_movement."
---

# 类型：平台游戏

专家蓝图，强调平台游戏的运动感觉、关卡设计和玩家满意度。

## 永远不要

- **永远不要跳过缓冲跳跃** — 离开边缘后没有6帧宽限期，跳跃会感觉无响应。玩家会责怪自己。
- **永远不要忽略跳跃缓冲** — 在落地前6帧按下跳跃应该排队跳跃。错过这点会使控制感觉迟钝。
- **永远不要使用固定跳跃高度** — 可变跳跃（按得更长=跳得更高）给玩家控制权。轻按为短跳，按住为全跳。
- **永远不要忘记相机平滑** — 瞬时相机捕捉会导致运动晕眩。使用position_smoothing或lerp进行平滑跟随。
- **永远不要跳过落地时的挤压/拉伸** — 落地没有视觉冲击会感觉轻飘飘。添加0.1秒的挤压以增加果汁感。
---

## 可用脚本

> **强制**：在实现相应模式之前，阅读适当的脚本。

### [advanced_platformer_controller.gd](scripts/advanced_platformer_controller.gd)
完整的平台游戏控制器，带有缓冲跳跃、跳跃缓冲、顶点浮力和可变重力。基于move_toward的摩擦力，用于抛光游戏感觉。

---

## 核心循环

`跳跃 → 导航障碍物 → 到达目标 → 下一关`

## 技能链

`godot-project-foundations`, `godot-characterbody-2d`, `godot-input-handling`, `animation`, `sound-manager`, `tilemap-setup`, `camera-2d`

---

## 运动感觉（“游戏感觉”）

平台游戏最关键的方向。玩家应该感觉**精确、响应灵敏、并处于控制中**。

### 输入响应性

```gdscript
# 瞬时方向变化 - 地面无加速
func _physics_process(delta: float) -> void:
    var input_dir := Input.get_axis("move_left", "move_right")
    
    # 地面移动：瞬时响应
    if is_on_floor():
        velocity.x = input_dir * MOVE_SPEED
    else:
        # 空中移动：轻微减少控制
        velocity.x = move_toward(velocity.x, input_dir * MOVE_SPEED, AIR_ACCEL * delta)
```

### 缓冲跳跃（宽限期）

允许在离开平台后短暂跳跃：

```gdscript
var coyote_timer: float = 0.0
const COYOTE_TIME := 0.1  # 100ms宽限期

func _physics_process(delta: float) -> void:
    if is_on_floor():
        coyote_timer = COYOTE_TIME
    else:
        coyote_timer = max(0, coyote_timer - delta)
    
    # 如果在地面上或处于缓冲时间内，可以跳跃
    if Input.is_action_just_pressed("jump") and coyote_timer > 0:
        velocity.y = JUMP_VELOCITY
        coyote_timer = 0
```

### 跳跃缓冲

注册在即将落地前按下的跳跃：

```gdscript
var jump_buffer: float = 0.0
const JUMP_BUFFER_TIME := 0.15

func _physics_process(delta: float) -> void:
    if Input.is_action_just_pressed("jump"):
        jump_buffer = JUMP_BUFFER_TIME
    else:
        jump_buffer = max(0, jump_buffer - delta)
    
    if is_on_floor() and jump_buffer > 0:
        velocity.y = JUMP_VELOCITY
        jump_buffer = 0
```

### 可变跳跃高度

```gdscript
const JUMP_VELOCITY := -400.0
const JUMP_RELEASE_MULTIPLIER := 0.5

func _physics_process(delta: float) -> void:
    # 当按钮释放时缩短跳跃
    if Input.is_action_just_released("jump") and velocity.y < 0:
        velocity.y *= JUMP_RELEASE_MULTIPLIER
```

### 重力调整

```gdscript
const GRAVITY := 980.0
const FALL_GRAVITY_MULTIPLIER := 1.5  # 更快下落感觉更好
const MAX_FALL_SPEED := 600.0

func apply_gravity(delta: float) -> void:
    var grav := GRAVITY
    if velocity.y > 0:  # 下落中
        grav *= FALL_GRAVITY_MULTIPLIER
    velocity.y = min(velocity.y + grav * delta, MAX_FALL_SPEED)
```

---

## 关卡设计原则

### “教学三部曲”

1. **介绍**：安全环境学习机制
2. **挑战**：应用机制，中等风险
3. **转折**：与其他机制或时间压力结合

### 视觉语言

- **安全平台**：独特的颜色/纹理
- **危险**：红/橙色调、尖刺、发光效果
- **可收集物**：明亮、动画、粒子效果
- **秘密**：微妙的环境提示

### 流动和节奏

```
简单 → 简单 → 中等 → 检查点 → 中等 → 困难 → 检查点 → Boss
```

### 相机设计

```gdscript
# 平台游戏的前瞻相机
extends Camera2D

@export var look_ahead_distance := 100.0
@export var look_ahead_speed := 3.0

var target_offset := Vector2.ZERO

func _process(delta: float) -> void:
    var player_velocity: Vector2 = target.velocity
    var desired_offset := player_velocity.normalized() * look_ahead_distance
    target_offset = target_offset.lerp(desired_offset, look_ahead_speed * delta)
    offset = target_offset
```

---

## 平台游戏子类型

### 精确平台游戏 (Celeste, Super Meat Boy)

- 死亡后即时重生
- 非常紧的控制（无加速）
- 每隔几秒游戏时间就有检查点
- 死亡是学习，不是惩罚

### 收集马拉松 (Mario 64, Banjo-Kazooie)

- 具有目标的大型枢纽世界
- 随着时间的推移解锁多个能力
- 鼓励回溯
- 星星/可收集物作为进度门

### 益智平台游戏 (Limbo, Inside)

- 缓慢、深思熟虑的节奏
- 环境谜题
- 基于物理的机制
- 大气叙事

### 银河城 (Hollow Knight)

- 参见 `godot-genre-metroidvania` 技能
- 能力锁定的探索
- 相互连接的世界地图

---

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 飘忽跳跃 | 增加重力，尤其是在下降时 |
| 不精确落地 | 添加缓冲跳跃和视觉落地反馈 |
| 不公平死亡 | 确保危险在遭遇前清晰可见 |
| 盲目跳跃 | 下落期间相机前瞻或缩放 |
| 无聊中期游戏 | 每2-3关引入新机制 |

---

## 抛光清单

- [ ] 落地/奔跑时的灰尘Godot粒子
- [ ] 重落地时的屏幕震动
- [ ] 挤压/拉伸动画
- [ ] 每个动作的音效（跳跃、落地、墙壁滑动）
- [ ] 死亡和重生动画
- [ ] 检查点视觉/音频反馈
- [ ] 可访问难度选项（辅助模式）

---

## Godot特定提示

1. **CharacterBody2D vs RigidBody2D**：对于平台游戏角色，始终使用 `CharacterBody2D` — 精确控制是必须的
2. **物理帧率**：考虑120Hz物理以获取更平滑移动
3. **单向平台**：使用 `set_collision_mask_value()` 或专用碰撞层
4. **墙壁检测**：使用 `is_on_wall()` 和 `get_wall_normal()` 进行墙壁跳跃

---

## 参考游戏

- **Celeste** - 完美的游戏感觉，辅助模式可访问性
- **Hollow Knight** - 战斗+平台游戏集成
- **Super Mario Bros. Wonder** - 视觉抛光和惊喜
- **Shovel Knight** - 复古机制与现代感觉


## 参考
- 主技能: [godot-master](../godot-master/SKILL.md)
