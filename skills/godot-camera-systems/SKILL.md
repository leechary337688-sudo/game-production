---
名称: godot-camera-systems
描述: "用于2D/3D相机控制的专家模式，包括平滑跟随（lerp、position_smoothing）、相机抖动（创伤系统）、带频率参数的屏幕抖动、平台游戏的死区/拖拽、超前预测和相机过渡。适用于玩家相机、电影序列或多相机系统。触发关键词：Camera2D, Camera3D, SpringArm3D, position_smoothing, camera_shake, trauma_system, look_ahead, drag_margin, camera_limits, camera_transition。"
---

# 相机系统

为2D和3D游戏中创建平滑、响应迅速的相机提供专家指导。

## 绝不要做

- **绝不要每帧使用 `global_position = target.global_position`** — 即时位置匹配会导致抖动移动。使用 `lerp()` 或 `position_smoothing_enabled = true`。
- **绝不要忘记为Camera2D设置 `limit_smoothed = true`** — 硬限制会导致在边缘突然停止。平滑防止突兀停顿。
- **绝不要使用偏移进行永久相机定位** — `offset` 仅用于抖动/摇摆效果。使用 `position` 进行永久相机放置。
- **绝不要同时启用多个Camera2D节点** — 只有一台相机可以处于活动状态。其他必须设置为 `enabled = false`。
- **绝不要在没有碰撞掩码的情况下使用SpringArm3D** — 如果 `collision_mask` 为空，SpringArm会穿透墙壁。设置为世界层。

---

## 可用脚本

> **强制**: 在实现相机行为前阅读。

### [camera_follow_2d.gd](scripts/camera_follow_2d.gd)
平滑相机跟随，带超前预测、死区和边界限制。

### [camera_shake_trauma.gd](scripts/camera_shake_trauma.gd)
基于创伤的相机抖动，使用Perlin噪声 - 行业标准的屏幕抖动实现。使用FastNoiseLite进行平滑相机抖动（平方创伤以获得感觉），带自动衰减。

### [phantom_decoupling.gd](scripts/phantom_decoupling.gd)
幻影相机模式：分离"我们看哪里"和"我们跟随什么"。相机跟随幻影节点，实现电影偏移和区域边界。

---

## Camera2D基础

```gdscript
extends Camera2D

@export var target: Node2D
@export var follow_speed := 5.0

func _process(delta: float) -> void:
    if target:
        global_position = global_position.lerp(
            target.global_position,
            follow_speed * delta
        )
```

## 位置平滑

```gdscript
extends Camera2D

func _ready() -> void:
    # 内置平滑
    position_smoothing_enabled = true
    position_smoothing_speed = 5.0
```

## 相机限制

```gdscript
extends Camera2D

func _ready() -> void:
    # 将相机约束到关卡边界
    limit_left = 0
    limit_top = 0
    limit_right = 1920
    limit_bottom = 1080
    
    # 平滑限制
    limit_smoothed = true
```

## 相机抖动

```gdscript
extends Camera2D

var shake_amount := 0.0
var shake_decay := 5.0

func _process(delta: float) -> void:
    if shake_amount > 0:
        shake_amount = max(shake_amount - shake_decay * delta, 0)
        offset = Vector2(
            randf_range(-shake_amount, shake_amount),
            randf_range(-shake_amount, shake_amount)
        )
    else:
        offset = Vector2.ZERO

func shake(intensity: float) -> void:
    shake_amount = intensity

# 用法：
$Camera2D.shake(10.0)  # 爆炸时屏幕抖动
```

## 缩放控制

```gdscript
extends Camera2D

@export var zoom_speed := 0.1
@export var min_zoom := 0.5
@export var max_zoom := 2.0

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_WHEEL_UP:
            zoom_in()
        elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
            zoom_out()

func zoom_in() -> void:
    zoom = zoom.move_toward(
        Vector2.ONE * max_zoom,
        zoom_speed
    )

func zoom_out() -> void:
    zoom = zoom.move_toward(
        Vector2.ONE * min_zoom,
        zoom_speed
    )
```

## 超前相机

```gdscript
extends Camera2D

@export var look_ahead_distance := 50.0
@export var target: CharacterBody2D

func _process(delta: float) -> void:
    if target:
        var look_ahead := target.velocity.normalized() * look_ahead_distance
        global_position = target.global_position + look_ahead
```

## 分屏（多相机）

```gdscript
# 玩家1相机
@onready var cam1: Camera2D = $Player1/Camera2D

# 玩家2相机
@onready var cam2: Camera2D = $Player2/Camera2D

func _ready() -> void:
    # 分割视口
    cam1.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
    cam2.anchor_mode = Camera2D.ANCHOR_MODE_DRAG_CENTER
```

## Camera3D模式

### 第三人称相机

```gdscript
extends Camera3D

@export var target: Node3D
@export var distance := 5.0
@export var height := 2.0
@export var rotation_speed := 3.0

var rotation_angle := 0.0

func _process(delta: float) -> void:
    if not target:
        return
    
    # 绕目标旋转
    rotation_angle += Input.get_axis("camera_left", "camera_right") * rotation_speed * delta
    
    # 计算位置
    var offset := Vector3(
        sin(rotation_angle) * distance,
        height,
        cos(rotation_angle) * distance
    )
    
    global_position = target.global_position + offset
    look_at(target.global_position, Vector3.UP)
```

### 第一人称相机

```gdscript
extends Camera3D

@export var mouse_sensitivity := 0.002
@export var max_pitch := deg_to_rad(80)

var pitch := 0.0

func _ready() -> void:
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        # 偏航（水平）
        get_parent().rotate_y(-event.relative.x * mouse_sensitivity)
        
        # 俯仰（垂直）
        pitch -= event.relative.y * mouse_sensitivity
        pitch = clamp(pitch, -max_pitch, max_pitch)
        rotation.x = pitch
```

## 相机过渡

```gdscript
# 平滑相机位置变化
func move_to_position(target_pos: Vector2, duration: float = 1.0) -> void:
    var tween := create_tween()
    tween.tween_property(self, "global_position", target_pos, duration)
    tween.set_ease(Tween.EASE_IN_OUT)
    tween.set_trans(Tween.TRANS_CUBIC)
```

## 电影相机

```gdscript
# 相机路径跟随
extends Path2D

@onready var path_follow: PathFollow2D = $PathFollow2D
@onready var camera: Camera2D = $PathFollow2D/Camera2D

func play_cutscene(duration: float) -> void:
    var tween := create_tween()
    tween.tween_property(path_follow, "progress_ratio", 1.0, duration)
    await tween.finished
```

## 最佳实践

### 1. 一台活动相机

```gdscript
# 一次只应启用一台Camera2D
# 其他应设置为 enabled = false
```

### 2. 将相机父级设为玩家

```gdscript
# 场景结构：
# 玩家 (CharacterBody2D)
#   └─ Camera2D
```

### 3. 使用锚点进行UI定位

```gdscript
# 相机不影响使用锚点定位的UI
# UI保持在屏幕空间
```

### 4. 平台游戏的死区

```gdscript
extends Camera2D

func _ready() -> void:
    drag_horizontal_enabled = true
    drag_vertical_enabled = true
    drag_left_margin = 0.3
    drag_right_margin = 0.3
```

## 参考
- [Godot 文档: Camera2D](https://docs.godotengine.org/en/stable/classes/class_camera2d.html)
- [Godot 文档: Camera3D](https://docs.godotengine.org/en/stable/classes/class_camera3d.html)


### 相关
- 主技能: [godot-master](../godot-master/SKILL.md)
