---
名称: godot-genre-fighting
描述: "专家蓝图，适用于格斗游戏，包括帧数据（启动/活动/恢复帧，命中/格挡优势帧）、命中框/受伤框系统、输入缓冲（5-10帧）、动作输入检测（QCF、DP）、连击系统（伤害缩放、取消层级）、角色状态（空闲/攻击/受击硬直/格挡硬直）和回滚网络代码。基于格斗游戏竞争设计。触发关键词：fighting_game, frame_data, hitbox_hurtbox, input_buffer, motion_inputs, combo_system, rollback_netcode, cancel_system, advantage_frames。"
---

# 类型: 格斗游戏

专为2D/3D格斗游戏设计的专家蓝图，强调帧完美战斗和竞争平衡。

## 绝对不要做

- **绝对不要使用可变帧率** — 格斗游戏需要固定的60fps。实现自定义基于帧的循环，而非使用 `_physics_process(delta)`。
- **绝对不要跳过输入缓冲** — 如果没有5-10帧缓冲，玩家会错过输入。指令输入感觉不响应。
- **绝对不要忘记伤害缩放** — 无限连击破坏竞争玩法。在连击中每次命中应用10%伤害减少。
- **绝对不要使所有招式在格挡时安全** — 如果所有攻击在格挡时有+0或更好优势，防御就无价值。混合安全和危险招式。
- **绝对不要在网络对战中使用客户端命中检测** — 客户端预测，服务器验证。点对点需要回滚网络代码，否则会发生不同步。
---

## 可用脚本

> **强制**: 在实现相应模式前阅读适当脚本。

### [fighting_input_buffer.gd](scripts/fighting_input_buffer.gd)
帧锁定输入轮询，带有动作指令检测。存储20帧历史，模糊匹配QCF/DP输入，使用 _physics_process 以确保确定性时序。

---

## 核心循环

`中立游戏 → 确认命中 → 执行连击 → 优势状态 → 重复`

## 技能链

`godot-project-foundations`, `godot-characterbody-2d`, `godot-input-handling`, `animation`, `godot-combat-system`, `godot-state-machine-advanced`, `multiplayer-lobby`

---

## 基于帧的战斗系统

格斗游戏基于 **帧数据** 运作——离散时间单位（通常为60fps）。

### 帧数据基础

```gdscript
class_name Attack
extends Resource

@export var name: String
@export var startup_frames: int  # 命中框激活前的帧数
@export var active_frames: int   # 命中框活动的帧数
@export var recovery_frames: int # 命中框失活后的帧数
@export var on_hit_advantage: int # 攻击命中时的帧优势
@export var on_block_advantage: int # 格挡时的帧优势
@export var damage: int
@export var hitstun: int  # 对手受击硬直的帧数
@export var blockstun: int # 对手格挡硬直的帧数

func get_total_frames() -> int:
    return startup_frames + active_frames + recovery_frames

func is_safe_on_block() -> bool:
    return on_block_advantage >= 0
```

### 帧精确处理

```gdscript
extends Node

var frame_count: int = 0
const FRAME_DURATION := 1.0 / 60.0
var accumulator: float = 0.0

func _process(delta: float) -> void:
    accumulator += delta
    while accumulator >= FRAME_DURATION:
        process_game_frame()
        frame_count += 1
        accumulator -= FRAME_DURATION

func process_game_frame() -> void:
    # 所有游戏逻辑在此以固定60fps运行
    for fighter in fighters:
        fighter.process_frame()
```

---

## 输入系统

### 输入缓冲

存储输入并在有效时执行：

```gdscript
class_name InputBuffer
extends Node

const BUFFER_FRAMES := 8  # 行业标准：5-10帧
var buffer: Array[InputEvent] = []

func add_input(input: InputEvent) -> void:
    buffer.append(input)
    if buffer.size() > BUFFER_FRAMES:
        buffer.pop_front()

func consume_input(action: StringName) -> bool:
    for i in range(buffer.size() - 1, -1, -1):
        if buffer[i].is_action(action):
            buffer.remove_at(i)
            return true
    return false
```

### 动作输入检测（Quarter Circle, DP等）

```gdscript
class_name MotionDetector
extends Node

const QCF := ["down", "down_forward", "forward"]  # 前下前（Quarter Circle Forward）
const DP := ["forward", "down", "down_forward"]   # 升龙拳（Dragon Punch）
const MOTION_WINDOW := 15  # 完成动作的帧数窗口

var direction_history: Array[String] = []

func add_direction(dir: String) -> void:
    if direction_history.is_empty() or direction_history[-1] != dir:
        direction_history.append(dir)
    # 保留最后N个方向
    if direction_history.size() > 20:
        direction_history.pop_front()

func check_motion(motion: Array[String]) -> bool:
    if direction_history.size() < motion.size():
        return false
    # 检查动作是否出现在最近历史中
    var recent := direction_history.slice(-MOTION_WINDOW)
    return _contains_sequence(recent, motion)

func _contains_sequence(haystack: Array, needle: Array) -> bool:
    var idx := 0
    for dir in haystack:
        if dir == needle[idx]:
            idx += 1
            if idx >= needle.size():
                return true
    return false
```

---

## 命中框/受伤框系统

```gdscript
class_name HitboxComponent
extends Area2D

enum BoxType { HITBOX, HURTBOX, THROW, PROJECTILE }

@export var box_type: BoxType
@export var attack_data: Attack
@export var owner_fighter: Fighter

signal hit_confirmed(target: Fighter, attack: Attack)

func _ready() -> void:
    monitoring = (box_type == BoxType.HITBOX or box_type == BoxType.THROW)
    monitorable = (box_type == BoxType.HURTBOX)
    connect("area_entered", _on_area_entered)

func _on_area_entered(area: Area2D) -> void:
    if area is HitboxComponent:
        var other := area as HitboxComponent
        if other.box_type == BoxType.HURTBOX and other.owner_fighter != owner_fighter:
            hit_confirmed.emit(other.owner_fighter, attack_data)
```

---

## 连击系统

### 命中确认和连击计数器

```gdscript
class_name ComboTracker
extends Node

var combo_count: int = 0
var combo_damage: int = 0
var in_combo: bool = false
var damage_scaling: float = 1.0

const SCALING_PER_HIT := 0.9  # 每次命中减少10%

func start_combo() -> void:
    in_combo = true
    combo_count = 0
    combo_damage = 0
    damage_scaling = 1.0

func add_hit(base_damage: int) -> int:
    combo_count += 1
    var scaled_damage := int(base_damage * damage_scaling)
    combo_damage += scaled_damage
    damage_scaling *= SCALING_PER_HIT
    return scaled_damage

func drop_combo() -> void:
    in_combo = false
    combo_count = 0
    damage_scaling = 1.0
```

### 取消系统

```gdscript
enum CancelType { NONE, NORMAL, SPECIAL, SUPER }

func can_cancel_into(from_attack: Attack, to_attack: Attack) -> bool:
    # 正常 → 特殊 → 超必杀层级
    match to_attack.cancel_type:
        CancelType.NORMAL:
            return from_attack.cancel_type == CancelType.NONE
        CancelType.SPECIAL:
            return from_attack.cancel_type in [CancelType.NONE, CancelType.NORMAL]
        CancelType.SUPER:
            return true  # 超必杀可以取消任何东西
    return false
```

---

## 角色状态

```gdscript
enum FighterState {
    IDLE, WALKING, CROUCHING, JUMPING,
    ATTACKING, BLOCKING, HITSTUN, BLOCKSTUN,
    KNOCKDOWN, WAKEUP, THROW, THROWN
}

class_name FighterStateMachine
extends Node

var current_state: FighterState = FighterState.IDLE
var state_frame: int = 0

func transition_to(new_state: FighterState) -> void:
    exit_state(current_state)
    current_state = new_state
    state_frame = 0
    enter_state(new_state)

func is_actionable() -> bool:
    return current_state in [
        FighterState.IDLE,
        FighterState.WALKING,
        FighterState.CROUCHING
    ]
```

---

## 网络代码考虑

### 回滚基础

```gdscript
class_name GameState
extends Resource

# 序列化完整游戏状态以用于回滚
func save_state() -> Dictionary:
    return {
        "frame": frame_count,
        "fighters": fighters.map(func(f): return f.serialize()),
        "projectiles": projectiles.map(func(p): return p.serialize())
    }

func load_state(state: Dictionary) -> void:
    frame_count = state["frame"]
    for i in fighters.size():
        fighters[i].deserialize(state["fighters"][i])
    # 重构投射物...
```

---

## 平衡指南

| 元素 | 指南 |
|---------|-----------|
| 生命值 | 10,000-15,000 约20秒回合 |
| 连击伤害 | 每次接触最大30-40%生命值 |
| 最快招式 | 3-5帧启动（轻攻击） |
| 最慢招式 | 20-40帧（超必杀、上段攻击） |
| 投掷范围 | 短但可靠 |
| 能量槽增益 | 约接收2次连击充满槽 |

---

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 无限连击 | 实现受击硬直衰减和重力缩放 |
| 无法格挡的设定 | 确保所有攻击有反制玩法 |
| 延迟输入丢失 | 稳健的输入缓冲（8+帧） |
| 网络对战不同步 | 确定性物理，回滚网络代码 |

---

## Godot特定提示

1. **谨慎使用 `_physics_process`** - 实现自己的基于帧的循环
2. **AnimationPlayer**：将命中框激活绑定到动画帧
3. **自定义碰撞**：可能需要自定义命中框系统而非物理引擎
4. **回滚的保存/加载**：保持状态可序列化

## 参考

- 大师技能：[godot-master](../godot-master/SKILL.md)
