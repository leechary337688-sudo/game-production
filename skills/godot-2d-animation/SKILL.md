---
name: godot-2d-animation
description: "Godot中2D动画的专家模式，使用AnimatedSprite2D和骨骼剪裁骨架。适用于实现精灵帧动画、程序化动画（挤压/拉伸）、剪裁骨骼层次结构或帧精确计时系统。触发关键词：AnimatedSprite2D、SpriteFrames、animation_finished、animation_looped、frame_changed、frame_progress、set_frame_and_progress、剪裁动画、骨骼2D、Bone2D、程序化动画、动画状态机、advance(0)。"
---

# 2D动画

Godot中基于帧和骨骼的2D动画的专家级指导。

## 绝不这样做

- **绝不在循环动画中使用`animation_finished`** — 该信号仅在非循环动画中触发。对于循环检测，请使用`animation_looped`。
- **绝不调用`play()`并期望即时状态变化** — AnimatedSprite2D在下一个处理帧应用`play()`。如果需要同步属性更新（例如，在更改动画和flip_h同时），请在`play()`后立即调用`advance(0)`。
- **绝不直接设置`frame`以保留动画进度** — 设置`frame`会将`frame_progress`重置为0.0。在动画中间切换时，使用`set_frame_and_progress(frame, progress)`以保持平滑过渡。
- **绝不忘缓存`@onready var anim_sprite`** — 在热路径如`_physics_process()`中，节点查找getter非常慢。始终使用`@onready`。
- **绝不混合AnimationPlayer轨道与代码驱动的AnimatedSprite2D** — 为每个精灵选择一个动画权威。混合会导致闪烁和状态冲突。

---

## 可用脚本

> **强制**：在实现相应模式前阅读适当脚本。

### [animation_sync.gd](scripts/animation_sync.gd)
用于帧精确逻辑（SFX/VFX命中框）、信号驱动的异步游戏编排和AnimationTree混合空间管理的方法轨道触发。在将游戏事件同步到动画帧时使用。

### [animation_state_sync.gd](scripts/animation_state_sync.gd)
具有过渡队列的帧精确状态驱动动画 — 对于响应式角色动画至关重要。

### [shader_hook.gd](scripts/shader_hook.gd)
通过AnimationPlayer属性轨道动画ShaderMaterial uniforms。涵盖命中闪光、溶解效果和批量精灵的实例uniforms。用于与动画状态相关的视觉反馈。

---

## AnimatedSprite2D信号（专家用法）

### animation_looped 与 animation_finished

```gdscript
extends CharacterBody2D

@onready var anim: AnimatedSprite2D = $AnimatedSprite2D

func _ready() -> void:
    # ✅ 正确：对重复动画使用animation_looped
    anim.animation_looped.connect(_on_loop)
    
    # ✅ 正确：仅对一次性动画使用animation_finished
    anim.animation_finished.connect(_on_finished)
    
    anim.play("run")  # 循环动画

func _on_loop() -> void:
    # 每次循环迭代触发
    emit_particle_effect("dust")

func _on_finished() -> void:
    # 仅对非循环动画触发
    anim.play("idle")
```

### frame_changed 用于事件触发

```gdscript
# 帧精确事件系统（攻击、脚步声等）
extends AnimatedSprite2D

signal attack_hit
signal footstep

# 定义每个动画的事件帧
const EVENT_FRAMES := {
    "attack": {3: "attack_hit", 7: "attack_hit"},
    "run": {2: "footstep", 5: "footstep"}
}

func _ready() -> void:
    frame_changed.connect(_on_frame_changed)

func _on_frame_changed() -> void:
    var events := EVENT_FRAMES.get(animation, {})
    if frame in events:
        emit_signal(events[frame])
```

---

## 高级模式：动画状态同步

### 问题：play() 时序故障

当同时更新动画和精灵属性（如`flip_h` + 动画更改）时，`play()`直到下一帧才应用，导致一帧视觉故障。

```gdscript
# ❌ 错误：故障一帧
func change_direction(dir: int) -> void:
    anim.flip_h = (dir < 0)
    anim.play("run")  # 下一帧应用
    # 结果：一帧错误动画但正确翻转

# ✅ 正确：强制即时同步
func change_direction(dir: int) -> void:
    anim.flip_h = (dir < 0)
    anim.play("run")
    anim.advance(0)  # 强制即时更新
```

---

## set_frame_and_progress() 用于平滑过渡

在动画中间更改动画而不产生视觉卡顿时使用：

```gdscript
# 示例：皮肤交换而不重置动画
func swap_skin(new_skin: String) -> void:
    var current_frame := anim.frame
    var current_progress := anim.frame_progress
    
    # 加载新的SpriteFrames资源
    anim.sprite_frames = load("res://skins/%s.tres" % new_skin)
    
    # ✅ 保留精确动画状态
    anim.play(anim.animation)  # 重新应用动画
    anim.set_frame_and_progress(current_frame, current_progress)
    # 结果：动画中间无缝皮肤交换
```

---

## 决策树：AnimatedSprite2D 与 AnimationPlayer

| 场景 | 使用 |
|----------|-----|
| 简单的基于帧的精灵交换 | AnimatedSprite2D |
| 需要动画其他属性（位置、缩放、旋转） | AnimationPlayer |
| 具有可交换皮肤/调色板的角色 | AnimatedSprite2D（交换SpriteFrames） |
| 具有10+骨骼的剪裁动画 | AnimationPlayer（更干净的轨道管理） |
| 需要混合/交叉淡入淡出动画 | AnimationPlayer（AnimationTree支持） |
| 像素完美的复古游戏 | AnimatedSprite2D（更简单的帧控制） |

---

## 专家模式：程序化挤压与拉伸

```gdscript
# 物理驱动的挤压/拉伸以提升游戏感
extends CharacterBody2D

@onready var sprite: Sprite2D = $Sprite2D
var _base_scale := Vector2.ONE

func _physics_process(delta: float) -> void:
    var prev_velocity := velocity
    move_and_slide()
    
    # 着陆时挤压
    if not is_on_floor() and is_on_floor():
        var impact_strength := clamp(abs(prev_velocity.y) / 800.0, 0.0, 1.0)
        _squash_and_stretch(Vector2(1.0 + impact_strength * 0.3, 1.0 - impact_strength * 0.3))
    
    # 跳跃时拉伸
    elif velocity.y < -200:
        sprite.scale = _base_scale.lerp(Vector2(0.9, 1.1), delta * 5.0)
    else:
        sprite.scale = sprite.scale.lerp(_base_scale, delta * 10.0)

func _squash_and_stretch(target_scale: Vector2) -> void:
    var tween := create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    tween.tween_property(sprite, "scale", target_scale, 0.08)
    tween.tween_property(sprite, "scale", _base_scale, 0.12)
```

---

## 剪裁动画（Bone2D 骨骼）

对于复杂的骨骼动画，使用Bone2D而非手动Sprite2D父子关系：

### 骨骼设置

```
Player (Node2D)
  └─ Skeleton2D
      ├─ Bone2D (Root - Torso)
      │   ├─ Sprite2D (Body)
      │   └─ Bone2D (Head)
      │       └─ Sprite2D (Head)
      ├─ Bone2D (ArmLeft)
      │   └─ Sprite2D (Arm)
      └─ Bone2D (ArmRight)
          └─ Sprite2D (Arm)
```

### AnimationPlayer 轨道

```gdscript
# 在AnimationPlayer中关键帧骨骼旋转
# 轨道：
# - "Skeleton2D/Bone2D:rotation"
# - "Skeleton2D/Bone2D/Bone2D2:rotation" (头部)
# - "Skeleton2D/Bone2D3:rotation" (左臂)
```

**为什么使用Bone2D而非手动父子关系？**
- 支持正向运动学（FK）和逆运动学（IK）
- 更容易装配和权重绘画
- 与动画重定向更好地集成

---

## 性能：SpriteFrames 优化

```gdscript
# ✅ 正确：跨实例共享SpriteFrames资源
const SHARED_FRAMES := preload("res://characters/player_frames.tres")

func _ready() -> void:
    anim_sprite.sprite_frames = SHARED_FRAMES
    # 所有玩家实例在内存中共享相同资源

# ❌ 错误：每个实例单独加载
func _ready() -> void:
    anim_sprite.sprite_frames = load("res://characters/player_frames.tres")
    # 每个实例在内存中复制资源
```

---

## 边缘情况：像素艺术居中

```gdscript
# 像素艺术纹理在像素之间居中时可能出现模糊
# 解决方案1：禁用居中
anim_sprite.centered = false
anim_sprite.offset = Vector2.ZERO

# 解决方案2：启用全局像素吸附（项目设置）
# rendering/2d/snap/snap_2d_vertices_to_pixel = true
# rendering/2d/snap/snap_2d_transforms_to_pixel = true
```

### SpriteFrames 纹理过滤

```gdscript
# 问题：SpriteFrames使用双线性过滤（对像素艺术模糊）
# 解决方案：在导入选项卡中对每个纹理：
# - 过滤器：最近（针对像素艺术）
# - Mipmaps：关闭（防止远距离混合）

# 或在项目设置中全局设置：
# rendering/textures/canvas_textures/default_texture_filter = Nearest
```

## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
