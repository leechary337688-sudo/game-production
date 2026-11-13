---
名称: godot-adapt-desktop-to-mobile
描述: "将桌面游戏移植到移动平台的专家模式，包括触摸控制方案（虚拟摇杆、手势检测）、小屏幕UI缩放、移动GPU性能优化、电池寿命管理和平台特定功能。用于创建移动端口或跨平台移动构建。触发关键词: TouchScreenButton, virtual_joystick, gesture_detector, InputEventScreenTouch, InputEventScreenDrag, mobile_optimization, battery_saving, adaptive_performance, MOBILE_ENABLED."
---

# 适配: 桌面到移动

为移植桌面游戏到移动平台提供专家指导。

## 绝对不要做

- **绝对不要直接使用鼠标位置** — 触摸没有“悬停”状态。用screen_drag替换mouse_motion，并检查InputEventScreenTouch.pressed。
- **绝对不要保留小的UI元素** — Apple HIG要求最小44pt触摸目标。Android Material: 48dp。将按钮放大2-3倍。
- **绝对不要忘记手指遮挡** — 用户手指会遮挡50-100px半径的区域。将关键信息放在触摸控制上方，而不是下方。
- **绝对不要在后台时全性能运行** — 移动操作系统会杀死在后台耗电的应用。当应用失去焦点时，暂停物理，将FPS降低到1-5。
- **绝对不要使用仅限桌面的功能** — 鼠标悬停、右键点击、键盘快捷键、滚动轮在移动设备上不存在。提供触摸替代方案。

---

## 可用脚本

> **强制**: 在实现相应模式之前阅读适当的脚本。

### [mobile_ui_adapter.gd](scripts/mobile_ui_adapter.gd)
自动移动覆盖：为触摸缩放按钮，应用安全区域边距，为电池/性能禁用重型效果（SSAO、SDFGI）。

### [virtual_joystick.gd](scripts/virtual_joystick.gd)
生产就绪的虚拟摇杆，支持多触摸、死区处理和视觉反馈。输出归一化的Vector2方向。

---

## 触摸控制方案

### 决策矩阵

| 类型 | 推荐控制 | 示例 |
|-------|-------------------|---------|
| 平台游戏 | 虚拟摇杆（左）+ 跳跃按钮（右） | Super Mario Run |
| 俯视角射击游戏 | 双摇杆（移动左，瞄准右） | Brawl Stars |
| 回合制 | 直接点击单位/瓦片 | Into the Breach |
| 益智游戏 | 点击、滑动、捏合手势 | Candy Crush |
| 卡牌游戏 | 拖放 | Hearthstone |
| 赛车游戏 | 倾斜转向或点击左/右 | Asphalt 9 |

### 虚拟摇杆

```gdscript
# virtual_joystick.gd
extends Control

signal direction_changed(direction: Vector2)

@export var dead_zone: float = 0.2
@export var max_distance: float = 100.0

var stick_center: Vector2
var is_pressed: bool = false
var touch_index: int = -1

@onready var base: Sprite2D = $Base
@onready var knob: Sprite2D = $Knob

func _ready() -> void:
    stick_center = base.position

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed and is_point_inside(event.position):
            is_pressed = true
            touch_index = event.index
        elif not event.pressed and event.index == touch_index:
            is_pressed = false
            reset_knob()
    
    elif event is InputEventScreenDrag and event.index == touch_index:
        update_knob(event.position)

func is_point_inside(point: Vector2) -> bool:
    return base.get_rect().has_point(base.to_local(point))

func update_knob(touch_pos: Vector2) -> void:
    var local_pos := to_local(touch_pos)
    var offset := local_pos - stick_center
    
    # 限制到最大距离
    if offset.length() > max_distance:
        offset = offset.normalized() * max_distance
    
    knob.position = stick_center + offset
    
    # 计算方向（-1到1）
    var direction := offset / max_distance
    if direction.length() < dead_zone:
        direction = Vector2.ZERO
    
    direction_changed.emit(direction)

func reset_knob() -> void:
    knob.position = stick_center
    direction_changed.emit(Vector2.ZERO)
```

### 手势检测

```gdscript
# gesture_detector.gd
extends Node

signal swipe_detected(direction: Vector2)  # 归一化
signal pinch_detected(scale: float)  # > 1.0 = 放大
signal tap_detected(position: Vector2)

const SWIPE_THRESHOLD := 100.0  # 像素
const TAP_MAX_DISTANCE := 20.0
const TAP_MAX_DURATION := 0.3  # 秒

var touch_start: Dictionary = {}  # index → {position: Vector2, time: float}
var pinch_start_distance: float = 0.0

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            touch_start[event.index] = {
                "position": event.position,
                "time": Time.get_ticks_msec() * 0.001
            }
        else:
            _handle_release(event)
    
    elif event is InputEventScreenDrag:
        _handle_drag(event)

func _handle_release(event: InputEventScreenTouch) -> void:
    if event.index not in touch_start:
        return
    
    var start_data = touch_start[event.index]
    var distance := event.position.distance_to(start_data.position)
    var duration := (Time.get_ticks_msec() * 0.001) - start_data.time
    
    # 点击检测
    if distance < TAP_MAX_DISTANCE and duration < TAP_MAX_DURATION:
        tap_detected.emit(event.position)
    
    # 滑动检测
    elif distance > SWIPE_THRESHOLD:
        var direction := (event.position - start_data.position).normalized()
        swipe_detected.emit(direction)
    
    touch_start.erase(event.index)

func _handle_drag(event: InputEventScreenDrag) -> void:
    # 捏合检测（需要2个触摸）
    if touch_start.size() == 2:
        var positions := []
        for idx in touch_start.keys():
            if idx == event.index:
                positions.append(event.position)
            else:
                positions.append(touch_start[idx].position)
        
        var current_distance := positions[0].distance_to(positions[1])
        
        if pinch_start_distance == 0.0:
            pinch_start_distance = current_distance
        else:
            var scale := current_distance / pinch_start_distance
            pinch_detected.emit(scale)
            pinch_start_distance = current_distance
```

---

## UI缩放

### 响应式布局

```gdscript
# 根据不同屏幕大小调整UI
extends Control

func _ready() -> void:
    get_viewport().size_changed.connect(_on_viewport_resized)
    _on_viewport_resized()

func _on_viewport_resized() -> void:
    var viewport_size := get_viewport_rect().size
    var aspect_ratio := viewport_size.x / viewport_size.y
    
    # 为不同宽高比调整
    if aspect_ratio > 2.0:  # 超宽（平板横向）
        scale_ui_for_tablet()
    elif aspect_ratio < 0.6:  # 高（手机纵向）
        scale_ui_for_phone()
    
    # 调整触摸按钮大小
    for button in get_tree().get_nodes_in_group("touch_buttons"):
        var min_size := 88  # 44pt * 2 for Retina
        button.custom_minimum_size = Vector2(min_size, min_size)

func scale_ui_for_tablet() -> void:
    # 将UI分散到边缘，使用水平空间
    $LeftControls.position.x = 100
    $RightControls.position.x = get_viewport_rect().size.x - 100

func scale_ui_for_phone() -> void:
    # 保持UI在底部，垂直紧凑
    $LeftControls.position.y = get_viewport_rect().size.y - 200
    $RightControls.position.y = get_viewport_rect().size.y - 200
```

---

## 性能优化

### 移动特定设置

```gdscript
# project.godot 或 autoload
extends Node

func _ready() -> void:
    if OS.get_name() in ["Android", "iOS"]:
        apply_mobile_optimizations()

func apply_mobile_optimizations() -> void:
    # 降低渲染质量
    get_viewport().msaa_2d = Viewport.MSAA_DISABLED
    get_viewport().msaa_3d = Viewport.MSAA_DISABLED
    get_viewport().screen_space_aa = Viewport.SCREEN_SPACE_AA_DISABLED
    
    # 降低阴影质量
    RenderingServer.directional_shadow_atlas_set_size(2048, false)  # 从4096降低
    
    # 减少粒子数量
    for particle in get_tree().get_nodes_in_group("godot-particles"):
        if particle is GPUParticles2D:
            particle.amount = max(10, particle.amount / 2)
    
    # 降低物理滴答率
    Engine.physics_ticks_per_second = 30  # 从60降低
    
    # 禁用昂贵效果
    var env := get_viewport().world_3d.environment
    if env:
        env.glow_enabled = false
        env.ssao_enabled = false
        env.ssr_enabled = false
```

### 自适应性能

```gdscript
# 根据FPS动态调整质量
extends Node

@export var target_fps: int = 60
@export var check_interval: float = 2.0

var timer: float = 0.0
var quality_level: int = 2  # 0=低, 1=中, 2=高

func _process(delta: float) -> void:
    timer += delta
    if timer >= check_interval:
        var current_fps := Engine.get_frames_per_second()
        
        if current_fps < target_fps - 10 and quality_level > 0:
            quality_level -= 1
            apply_quality(quality_level)
        elif current_fps > target_fps + 5 and quality_level < 2:
            quality_level += 1
            apply_quality(quality_level)
        
        timer = 0.0

func apply_quality(level: int) -> void:
    match level:
        0:  # 低
            get_viewport().scaling_3d_scale = 0.5
        1:  # 中
            get_viewport().scaling_3d_scale = 0.75
        2:  # 高
            get_viewport().scaling_3d_scale = 1.0
```

---

## 电池寿命管理

### 后台行为

```gdscript
#  mobile_lifecycle.gd
extends Node

func _ready() -> void:
    get_tree().on_request_permissions_result.connect(_on_permissions_result)

func _notification(what: int) -> void:
    match what:
        NOTIFICATION_APPLICATION_PAUSED:
            _on_app_backgrounded()
        NOTIFICATION_APPLICATION_RESUMED:
            _on_app_foregrounded()

func _on_app_backgrounded() -> void:
    # 大幅降低FPS
    Engine.max_fps = 5
    
    # 暂停物理
    get_tree().paused = true
    
    # 停止音频
    AudioServer.set_bus_mute(AudioServer.get_bus_index("Master"), true)

func _on_app_foregrounded() -> void:
    # 恢复FPS
    Engine.max_fps = 60
    
    # 恢复
    get_tree().paused = false
    AudioServer.set_bus_mute(AudioServer.get_bus_index("Master"), false)
```

---

## 平台特定功能

### 安全区域插入（iPhone刘海）

```gdscript
# 处理刘海/状态栏
func _ready() -> void:
    if OS.get_name() == "iOS":
        var safe_area := DisplayServer.get_display_safe_area()
        var viewport_size := get_viewport_rect().size
        
        # 调整UI边距
        $TopBar.position.y = safe_area.position.y
        $BottomControls.position.y = viewport_size.y - safe_area.end.y - 100
```

### 振动反馈

```gdscript
func trigger_haptic(intensity: float) -> void:
    if OS.has_feature("mobile"):
        # Android
        if OS.get_name() == "Android":
            var duration_ms := int(intensity * 100)
            OS.vibrate_handheld(duration_ms)
        
        # iOS（需要插件）
        # 使用第三方插件进行iOS触觉反馈
```

---

## 输入重映射

### 鼠标 → 触摸转换

```gdscript
# 桌面鼠标输入
func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        _on_click(event.position)
# ⬇️ 转换为触摸:

func _input(event: InputEvent) -> void:
    # 支持鼠标（桌面测试）和触摸
    if event is InputEventMouseButton and event.pressed:
        _on_click(event.position)
    elif event is InputEventScreenTouch and event.pressed:
        _on_click(event.position)

func _on_click(position: Vector2) -> void:
    # 处理点击/触摸
    pass
```

---

## 边缘情况

### 键盘弹出阻挡UI

```gdscript
# 问题: 虚拟键盘覆盖文本输入
# 解决方案: 检测键盘，向上滚动UI

func _on_text_edit_focus_entered() -> void:
    if OS.has_feature("mobile"):
        # 键盘高度变化；估计300px
        var keyboard_offset := 300
        $UI.position.y -= keyboard_offset

func _on_text_edit_focus_exited() -> void:
    $UI.position.y = 0
```

### 意外触摸输入

```gdscript
# 问题: 手掌靠在屏幕上触发输入
# 解决方案: 忽略屏幕边缘附近的触摸

func is_valid_touch(position: Vector2) -> bool:
    var viewport_size := get_viewport_rect().size
    var edge_margin := 50.0
    
    return (position.x > edge_margin and
            position.x < viewport_size.x - edge_margin and
            position.y > edge_margin and
            position.y < viewport_size.y - edge_margin)
```

---

## 测试清单

- [ ] 触摸控制适用于粗手指（在真实设备上测试）
- [ ] UI不阻挡游戏关键元素
- [ ] 游戏在应用进入后台时暂停
- [ ] 在目标设备上性能达到60 FPS（iPhone 12, Galaxy S21）
- [ ] 电池消耗每小时<10%
- [ ] 安全区域被尊重（刘海、状态栏）
- [ ] 在纵向和横向模式下都能工作
- [ ] 文本在最小目标设备上可读（iPhone SE）

## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
