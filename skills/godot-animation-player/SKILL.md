---
name: godot-animation-player
描述："AnimationPlayer的专家模式，包括轨道类型（值、方法、音频、贝塞尔）、根运动提取、动画回调、程序化动画生成、调用模式优化和RESET轨道。用于基于时间线的动画、过场动画或UI过渡。触发关键词：AnimationPlayer、Animation、track_insert_key、root_motion、animation_finished、RESET_track、call_mode、animation_set_next、queue、blend_times。"
---

# AnimationPlayer

Godot基于时间线的关键帧动画系统的专家指南。

## 绝不这样做

- **绝不要忘记RESET轨道** — 没有RESET轨道，动画属性在切换场景时不会恢复为初始值。创建包含所有默认状态的RESET动画。
- **绝不要为函数调用使用Animation.CALL_MODE_CONTINUOUS** — 在关键帧期间每个帧都调用方法。使用CALL_MODE_DISCRETE（只调用一次）。连续模式会导致垃圾信息。
- **绝不要直接动画化资源属性** — 动画化`material.albedo_color`会创建嵌入资源，增加文件大小。将材质存储在变量中，动画化变量的属性。
- **绝不要为循环动画使用animation_finished** — 信号不会为循环动画触发。使用`animation_looped`或在_process()中检查`current_animation`。
- **绝不要到处硬编码动画名称作为字符串** — 使用常量或枚举。拼写错误会导致无声失败。

---

## 可用脚本

> **强制**：在实现相应模式之前，阅读适当的脚本。

### [audio_sync_tracks.gd](scripts/audio_sync_tracks.gd)
通过Animation.TYPE_AUDIO轨道实现子帧音频同步。脚步声设置，带自动混合处理用于交叉淡入淡出。

### [programmatic_anim.gd](scripts/programmatic_anim.gd)
程序化动画生成：通过代码创建Animation资源，包括关键帧、缓动和过渡曲线，用于动态运行时动画。

---

## 轨道类型深入探讨

### 值轨道（属性动画）

```gdscript
# 动画化任何属性：位置、颜色、音量、自定义变量
var anim := Animation.new()
anim.length = 2.0

# 位置轨道
var pos_track := anim.add_track(Animation.TYPE_VALUE)
anim.track_set_path(pos_track, ".:position")
anim.track_insert_key(pos_track, 0.0, Vector2(0, 0))
anim.track_insert_key(pos_track, 1.0, Vector2(100, 0))
anim.track_set_interpolation_type(pos_track, Animation.INTERPOLATION_CUBIC)

# 颜色轨道（调制）
var color_track := anim.add_track(Animation.TYPE_VALUE)
anim.track_set_path(color_track, "Sprite2D:modulate")
anim.track_insert_key(color_track, 0.0, Color.WHITE)
anim.track_insert_key(color_track, 2.0, Color.TRANSPARENT)

$AnimationPlayer.add_animation("fade_move", anim)
$AnimationPlayer.play("fade_move")
```

### 方法轨道（函数调用）

```gdscript
# 在特定时间戳调用函数
var method_track := anim.add_track(Animation.TYPE_METHOD)
anim.track_set_path(method_track, ".")  # 路径到节点

# 插入方法调用
anim.track_insert_key(method_track, 0.5, {
    "method": "spawn_particle",
    "args": [Vector2(50, 50)]
})

anim.track_insert_key(method_track, 1.5, {
    "method": "play_sound",
    "args": ["res://sounds/explosion.ogg"]
})

# 关键：将调用模式设置为DISCRETE
anim.track_set_call_mode(method_track, Animation.CALL_MODE_DISCRETE)

# 方法必须存在于目标节点上：
func spawn_particle(pos: Vector2) -> void:
    # 在位置生成粒子
    pass

func play_sound(sound_path: String) -> void:
    $AudioStreamPlayer.stream = load(sound_path)
    $AudioStreamPlayer.play()
```

### 音频轨道

```gdscript
# 将音频与动画同步
var audio_track := anim.add_track(Animation.TYPE_AUDIO)
anim.track_set_path(audio_track, "AudioStreamPlayer")

# 插入音频播放
var audio_stream := load("res://sounds/footstep.ogg")
anim.audio_track_insert_key(audio_track, 0.3, audio_stream)
anim.audio_track_insert_key(audio_track, 0.6, audio_stream)  # 第二步

# 为特定键设置音量
anim.audio_track_set_key_volume(audio_track, 0, 1.0)  # 全音量
anim.audio_track_set_key_volume(audio_track, 1, 0.7)  # 更安静
```

### 贝塞尔轨道（自定义曲线）

```gdscript
# 用于平滑、自定义插值曲线
var bezier_track := anim.add_track(Animation.TYPE_BEZIER)
anim.track_set_path(bezier_track, ".:custom_value")

# 插入带手柄的贝塞尔点
anim.bezier_track_insert_key(bezier_track, 0.0, 0.0)
anim.bezier_track_insert_key(bezier_track, 1.0, 100.0,
    Vector2(0.5, 0),    # 进手柄
    Vector2(-0.5, 0))   # 出手柄

# 在_process中读取值
func _process(delta: float) -> void:
    var value := $AnimationPlayer.get_bezier_value("custom_value")
    # 使用值进行自定义效果
```

---

## 根运动提取

### 问题：动画运动与物理断开

```gdscript
# 角色在动画中行走，但位置在世界中不变
# 动画修改骨架骨骼，而不是CharacterBody3D根节点
```

### 解决方案：根运动

```gdscript
# 场景结构：
# CharacterBody3D（根）
#   ├─ MeshInstance3D
#   │   └─ Skeleton3D
#   └─ AnimationPlayer

# AnimationPlayer设置：
@onready var anim_player: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
    # 启用根运动（指向根骨骼）
    anim_player.root_motion_track = NodePath("MeshInstance3D/Skeleton3D:root")
    anim_player.play("walk")

func _physics_process(delta: float) -> void:
    # 提取根运动
    var root_motion_pos := anim_player.get_root_motion_position()
    var root_motion_rot := anim_player.get_root_motion_rotation()
    var root_motion_scale := anim_player.get_root_motion_scale()
    
    # 应用到CharacterBody3D
    var transform := Transform3D(basis.rotated(basis.y, root_motion_rot.y), Vector3.ZERO)
    transform.origin = root_motion_pos
    global_transform *= transform
    
    # 从根运动获取速度
    velocity = root_motion_pos / delta
    move_and_slide()
```

---

## 动画序列与队列

### 链接动画

```gdscript
# 按顺序播放动画
@onready var anim: AnimationPlayer = $AnimationPlayer

func play_attack_combo() -> void:
    anim.play("attack_1")
    await anim.animation_finished
    anim.play("attack_2")
    await anim.animation_finished
    anim.play("idle")

# 或使用队列：
func play_with_queue() -> void:
    anim.play("attack_1")
    anim.queue("attack_2")
    anim.queue("idle")  # 在attack_2后自动播放
```

### 混合时间

```gdscript
# 动画之间的平滑过渡
anim.play("walk")

# 0.5秒从行走混合到跑步
anim.play("run", -1, 1.0, 0.5)  # custom_blend = 0.5

# 或设置默认混合
anim.set_default_blend_time(0.3)  # 所有过渡0.3秒
anim.play("idle")
```

---

## RESET轨道模式

### 问题：属性不重置

```gdscript
# 动画精灵位置从(0,0) → (100, 0)
# 切换场景，精灵停留在(100, 0)！
```

### 解决方案：RESET动画

```gdscript
# 创建带默认值的RESET动画
var reset_anim := Animation.new()
reset_anim.length = 0.01  # 非常短

var track := reset_anim.add_track(Animation.TYPE_VALUE)
reset_anim.track_set_path(track, "Sprite2D:position")
reset_anim.track_insert_key(track, 0.0, Vector2(0, 0))  # 默认位置

track = reset_anim.add_track(Animation.TYPE_VALUE)
reset_anim.track_set_path(track, "Sprite2D:modulate")
reset_anim.track_insert_key(track, 0.0, Color.WHITE)  # 默认颜色

anim_player.add_animation("RESET", reset_anim)

# AnimationPlayer在场景加载时自动播放RESET
# 如果AnimationPlayer设置中启用了“保存时重置”
```

---

## 程序化动画生成

### 从代码生成动画

```gdscript
# 程序化创建弹跳动画
func create_bounce_animation() -> void:
    var anim := Animation.new()
    anim.length = 1.0
    anim.loop_mode = Animation.LOOP_LINEAR
    
    # 位置轨道（Y弹跳）
    var track := anim.add_track(Animation.TYPE_VALUE)
    anim.track_set_path(track, ".:position:y")
    
    # 生成正弦波关键帧
    for i in range(10):
        var time := float(i) / 9.0  # 0.0 到 1.0
        var value := sin(time * TAU) * 50.0  # 弹跳高度50像素
        anim.track_insert_key(track, time, value)
    
    anim.track_set_interpolation_type(track, Animation.INTERPOLATION_CUBIC)
    $AnimationPlayer.add_animation("bounce", anim)
    $AnimationPlayer.play("bounce")
```

---

## 高级模式

### 反向播放动画

```gdscript
# 反向播放动画（用于关门等）
anim.play("door_open", -1, -1.0)  # speed = -1.0 = 反向

# 暂停并反向
anim.pause()
anim.play("current_animation", -1, -1.0, false)  # from_end = false
```

### 动画回调（基于信号）

```gdscript
# 在特定帧发射自定义信号
func _ready() -> void:
    $AnimationPlayer.animation_finished.connect(_on_anim_finished)

func _on_anim_finished(anim_name: String) -> void:
    match anim_name:
        "attack":
            deal_damage()
        "die":
            queue_free()
```

### 跳转到特定时间

```gdscript
# 跳到动画的50%
anim.seek(anim.current_animation_length * 0.5)

# 在动画中擦洗（过场动画编辑器）
func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and scrubbing:
        var normalized_pos := event.position.x / get_viewport_rect().size.x
        anim.seek(anim.current_animation_length * normalized_pos)
```

---

## 性能优化

### 当不在屏幕时禁用

```gdscript
extends VisibleOnScreenNotifier2D

func _ready() -> void:
    screen_exited.connect(_on_screen_exited)
    screen_entered.connect(_on_screen_entered)

func _on_screen_exited() -> void:
    $AnimationPlayer.pause()

func _on_screen_entered() -> void:
    $AnimationPlayer.play()
```

---

## 边缘情况

### 动画不播放

```gdscript
# 问题：忘记将动画添加到播放器
# 解决方案：检查动画是否存在
if anim.has_animation("walk"):
    anim.play("walk")
else:
    push_error("动画'walk'未找到！")

# 更好：使用常量
const ANIM_WALK = "walk"
const ANIM_IDLE = "idle"

if anim.has_animation(ANIM_WALK):
    anim.play(ANIM_WALK)
```

### 方法轨道不触发

```gdscript
# 问题：调用模式是CONTINUOUS
# 解决方案：设置为DISCRETE
var method_track_idx := anim.find_track(".:method_name", Animation.TYPE_METHOD)
anim.track_set_call_mode(method_track_idx, Animation.CALL_MODE_DISCRETE)
```

---

## 决策矩阵：AnimationPlayer vs Tween

| 特性 | AnimationPlayer | Tween |
|---------|-----------------|-------|
| **时间线编辑** | ✅ 视觉编辑器 | ❌ 仅代码 |
| **多属性** | ✅ 多个轨道 | ❌ 一个属性 |
| **可重用** | ✅ 保存为资源 | ❌ 每次创建 |
| **动态运行时** | ❌ 静态 | ✅ 完全动态 |
| **方法调用** | ✅ 方法轨道 | ❌ 使用回调 |
| **性能** | ✅ 优化 | ❌ 稍慢 |

**使用AnimationPlayer用于**：过场动画、角色动画、复杂UI
**使用Tween用于**：简单的运行时效果、一次性过渡


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
