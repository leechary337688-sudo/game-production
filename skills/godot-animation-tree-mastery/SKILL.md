---
名称: godot-animation-tree-mastery
描述: "AnimationTree 的专家模式，包括状态机过渡、用于定向移动的 BlendSpace2D、用于分层动画的 BlendTree、根运动、过渡条件、高级表达式和状态机子状态。用于具有运动混合和状态管理的复杂角色动画系统。触发关键词：AnimationTree, AnimationNodeStateMachine, BlendSpace2D, BlendSpace1D, BlendTree, transition_request, blend_position, advance_expression, AnimationNodeAdd2, AnimationNodeBlend2, root_motion。"
---

# AnimationTree 精通

Godot 高级动画混合和状态机的专家指导。

## 绝对不要做

- **绝对不要在启用 AnimationTree 时调用 `play()`** — AnimationTree 控制播放器。直接调用 `play()` 会导致冲突。应使用 `set("parameters/transition_request")`。
- **绝对不要忘记设置 `active = true`** — AnimationTree 默认不活动。动画不会播放，除非设置 `$AnimationTree.active = true`。
- **绝对不要使用绝对路径进行 transition_request** — 使用相对路径。"parameters/StateMachine/transition_request"，而不是 "/root/.../transition_request"。
- **绝对不要无意中启用 auto_advance** — 自动前进过渡会在没有条件时立即触发。适用于连击链，但对于空闲→行走是致命的。
- **绝对不要将 BlendSpace2D 用于非定向混合** — 使用 BlendSpace1D 用于速度（行走→奔跑）或 Blend2 用于简单补间。BlendSpace2D 适用于 X+Y 轴（侧移动画）。

---

## 可用脚本

> **必需**：在实现相应模式前阅读相关脚本。

### [nested_state_machine.gd](scripts/nested_state_machine.gd)
分层状态机模式。展示 travel() 在子状态之间的切换以及深层参数路径（StateMachine/BlendSpace2D/blend_position）。

### [skeleton_ik_lookat.gd](scripts/skeleton_ik_lookat.gd)
用于头部跟踪的程序化 IK。通过平滑权重混合，从 AnimationTree 驱动 SkeletonModifier3D 的注视参数。

---

## 核心概念

### AnimationTree 结构

```
AnimationTree (节点)
  ├─ 根 (在编辑器中指定)
  │   ├─ StateMachine (常见)
  │   ├─ BlendTree (分层)
  │   └─ BlendSpace (定向)
  └─ anim_player: NodePath → 指向 AnimationPlayer
```

### 参数访问

```gdscript
# 使用字符串路径设置参数
$AnimationTree.set("parameters/StateMachine/transition_request", "run")
$AnimationTree.set("parameters/Movement/blend_position", Vector2(1, 0))

# 获取当前状态
var current_state = $AnimationTree.get("parameters/StateMachine/current_state")
```

---

## 状态机模式

### 基本设置

```gdscript
# 场景结构：
# CharacterBody2D
#   ├─ AnimationPlayer (包含：空闲、行走、奔跑、跳跃、着陆)
#   └─ AnimationTree
#       └─ 根：AnimationNodeStateMachine

# 状态机节点（在 AnimationTree 编辑器中创建）：
# - 空闲 (AnimationNode 引用 "空闲")
# - 行走 (AnimationNode 引用 "行走")
# - 奔跑 (AnimationNode 引用 "奔跑")
# - 跳跃 (AnimationNode 引用 "跳跃")
# - 着陆 (AnimationNode 引用 "着陆")

@onready var anim_tree: AnimationTree = $AnimationTree
@onready var state_machine: AnimationNodeStateMachinePlayback = anim_tree.get("parameters/StateMachine/playback")

func _ready() -> void:
    anim_tree.active = true

func _physics_process(delta: float) -> void:
    var velocity := get_velocity()
    
    # 基于游戏状态进行过渡
    if is_on_floor():
        if velocity.length() < 10:
            state_machine.travel("空闲")
        elif velocity.length() < 200:
            state_machine.travel("行走")
        else:
            state_machine.travel("奔跑")
    else:
        if velocity.y < 0:  # 上升
            state_machine.travel("跳跃")
        else:  # 下降
            state_machine.travel("着陆")
```

### 过渡条件（高级表达式）

```gdscript
# 在 AnimationTree 编辑器中：
# 添加从 空闲 → 行走 的过渡
# 设置 "前进条件" 为 "is_walking"

# 在代码中：
anim_tree.set("parameters/conditions/is_walking", true)

# 当条件变为 true 时，过渡自动触发
# 适用于事件驱动的过渡（受伤、死亡等）

# 示例：伤害过渡
anim_tree.set("parameters/conditions/is_damaged", false)  # 每帧重置

func take_damage() -> void:
    anim_tree.set("parameters/conditions/is_damaged", true)
    # 立即触发到 "受伤" 状态的过渡
```

### 自动前进（连击链）

```gdscript
# 在 AnimationTree 编辑器中：
# 从 攻击1 → 攻击2 的过渡
# 启用 "自动前进"（无需条件）

# 代码：
state_machine.travel("攻击1")
# 攻击1 动画播放
# 当攻击1 完成时，自动过渡到攻击2
# 当攻击2 完成时，过渡到空闲（下一个自动前进）

# 适用于：
# - 攻击连击
# - 死亡 → 重生
# - 过场动画序列
```

---

## BlendSpace2D（定向移动）

### 8 方向移动

```gdscript
# 在 AnimationTree 编辑器中创建 BlendSpace2D：
# - 在位置添加动画：
#   - (0, -1)：向上行走
#   - (0, 1)：向下行走
#   - (-1, 0)：向左行走
#   - (1, 0)：向右行走
#   - (-1, -1)：左上行走
#   - (1, -1)：右上行走
#   - (-1, 1)：左下行走
#   - (1, 1)：右下行走
#   - (0, 0)：空闲（中心）

# 在代码中：
func _physics_process(delta: float) -> void:
    var input := Input.get_vector("左", "右", "上", "下")
    
    # 设置混合位置（AnimationTree 在动画之间插值）
    anim_tree.set("parameters/Movement/blend_position", input)
    
    # BlendSpace2D 根据输入自动混合动画
    # input = (0.5, -0.5) → 混合向右行走和向上行走
```

### BlendSpace1D（速度混合）

```gdscript
# 用于行走 → 奔跑过渡
# 创建 BlendSpace1D：
#   - 位置 0.0：行走
#   - 位置 1.0：奔跑

func _physics_process(delta: float) -> void:
    var speed := velocity.length()
    var max_speed := 400.0
    var blend_value := clamp(speed / max_speed, 0.0, 1.0)
    
    anim_tree.set("parameters/SpeedBlend/blend_position", blend_value)
    # 随着速度增加，平滑地从行走 → 奔跑混合
```

---

## BlendTree（分层动画）

### 添加上半身动画

```gdscript
# 问题：想在行走时瞄准枪支
# 解决方案：混合上半身（瞄准）和下半身（行走）

# 在 AnimationTree 编辑器中：
# 根 → BlendTree
#   ├─ 行走（下半身动画）
#   ├─ 瞄准（上半身动画）
#   └─ Add2 节点（组合它们）
#       - 输入：行走、瞄准
#       - filter_enabled：true
#       - 过滤器：仅启用瞄准的上半身骨骼

# 代码：
# 无需代码！BlendTree 自动组合
# 确保动画已分配
```

### Blend2（淡入淡出）

```gdscript
# 动态混合两个动画
# 根 → BlendTree
#   └─ Blend2
#       ├─ 输入 A：空闲
#       └─ 输入 B：攻击

# 代码：
var blend_amount := 0.0

func _process(delta: float) -> void:
    # 逐渐从空闲 → 攻击混合
    blend_amount += delta
    blend_amount = clamp(blend_amount, 0.0, 1.0)
    
    anim_tree.set("parameters/IdleAttackBlend/blend_amount", blend_amount)
    # 0.0 = 100% 空闲
    # 0.5 = 50% 空闲, 50% 攻击
    # 1.0 = 100% 攻击
```

---

## 使用 AnimationTree 的根运动

```gdscript
# 在 AnimationTree 中启用
anim_tree.root_motion_track = NodePath("CharacterBody3D/Skeleton3D:Root")

func _physics_process(delta: float) -> void:
    # 获取根运动
    var root_motion := anim_tree.get_root_motion_position()
    
    # 应用到角色（非速度！）
    global_position += root_motion.rotated(rotation.y)
    
    # 对于使用 move_and_slide 的 CharacterBody3D：
    velocity = root_motion / delta
    move_and_slide()
```

---

## 高级模式

### 子状态机

```gdscript
# 嵌套状态机用于复杂行为
# 根 → StateMachine
#   ├─ 地面（子状态机）
#   │   ├─ 空闲
#   │   ├─ 行走
#   │   └─ 奔跑
#   └─ 空中（子状态机）
#       ├─ 跳跃
#       ├─ 坠落
#       └─ 滑翔

# 访问嵌套状态：
var sub_state = anim_tree.get("parameters/Grounded/playback")
sub_state.travel("奔跑")
```

### 时间缩放（慢动作）

```gdscript
# 减慢特定动画而不影响其他
anim_tree.set("parameters/TimeScale/scale", 0.5)  # 50% 速度

# 适用于：
# - 子弹时间
# - 受伤/眩晕效果
# - 充能动画
```

### 动画间同步

```gdscript
# 问题：从行走 → 奔跑切换导致脚步滑动
# 解决方案：在过渡上使用 "同步"

# 在 AnimationTree 编辑器中：
# 过渡：行走 → 奔跑
# 启用 "同步" 复选框

# Godot 自动同步动画播放位置
# 在过渡期间脚保持接地
```

---

## 调试 AnimationTree

### 打印当前状态

```gdscript
func _process(delta: float) -> void:
    var current_state = anim_tree.get("parameters/StateMachine/current_state")
    print("当前状态：", current_state)
    
    # 打印混合位置
    var blend_pos = anim_tree.get("parameters/Movement/blend_position")
    print("混合位置：", blend_pos)
```

### 常见问题

```gdscript
# 问题：动画不播放
# 解决方案：
if not anim_tree.active:
    anim_tree.active = true

# 问题：过渡不工作
# 检查：
# 1. 是否设置了前进条件？
# 2. 过渡优先级是否正确？
# 3. 是否无意中启用了自动前进？

# 问题：混合不流畅
# 解决方案：增加过渡 xfade_time（0.1 - 0.3秒）
```

---

## 性能优化

### 不需要时禁用

```gdscript
# AnimationTree 开销大
# 对屏幕外实体禁用
extends VisibleOnScreenNotifier3D

func _ready() -> void:
    screen_exited.connect(_on_screen_exited)
    screen_entered.connect(_on_screen_entered)

func _on_screen_exited() -> void:
    $AnimationTree.active = false

func _on_screen_entered() -> void:
    $AnimationTree.active = true
```

---

## 决策树：何时使用 AnimationTree

| 特性 | 仅使用 AnimationPlayer | AnimationTree |
|---------|---------------------|---------------|
| 简单状态切换 | ✅ play("空闲") | ❌ 过度复杂 |
| 定向移动 | ❌ 复杂 | ✅ BlendSpace2D |
| 状态机（5+ 状态） | ❌ 代码混乱 | ✅ StateMachine |
| 分层动画 | ❌ 手动混合 | ✅ BlendTree |
| 根运动 | ✅ 可能 | ✅ 内置 |
| 过渡混合 | ❌ 手动 | ✅ 自动 |

**使用 AnimationTree 用于**：具有 5+ 状态的复杂角色、定向移动、分层动画
**使用 AnimationPlayer 用于**：简单动画、UI、过场动画、道具


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
