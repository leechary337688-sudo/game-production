---
name: godot-platform-mobile
description: "专家蓝图用于移动平台（Android/iOS），涵盖触摸控制、虚拟摇杆、响应式UI、安全区域（凹口）、电池优化和应用商店指南。适用于目标为移动发布或实现触摸输入的场景。关键词：移动、Android、iOS、触摸、InputEventScreenTouch、虚拟摇杆、安全区域、电池、应用商店、方向。"
---

# 平台：移动

触摸优先输入、安全区域处理和电池优化定义了移动开发。

## 可用脚本

### [mobile_safe_area_handler.gd](scripts/mobile_safe_area_handler.gd)
使用锚定边距的专家级安全区域处理，适用于凹口屏幕。

## 在移动开发中永远不要做

- **永远不要使用鼠标事件处理触摸** — 在移动设备上使用`InputEventMouseButton`？不可靠。使用`InputEventScreenTouch` + `InputEventScreenDrag`处理触摸。
- **永远不要忽略安全区域** — UI在iPhone凹口后面 = 不可用。调用`DisplayServer.get_display_safe_area()`，根据顶部/底部偏移调整UI。
- **永远不要在后台保持60 FPS** — 应用在后台运行于60 FPS = 电池耗尽 + 商店拒绝。在`NOTIFICATION_APPLICATION_FOCUS_OUT`时设置`Engine.max_fps = 0`。
- **永远不要使用桌面UI尺寸** — 在手机上使用12pt字体 = 不可读。移动设备最小16-18pt。使用`get_viewport().size`动态缩放。
- **永远不要忘记VRAM压缩** — 在移动设备上使用未压缩纹理 = 内存不足崩溃。在project.godot中启用`rendering/textures/vram_compression/import_etc2_astc=true`。
- **永远不要在主线程中阻塞保存操作** — 在触摸时保存大文件 = 冻结 = ANR（应用无响应）。在工作线程中使用`FileAccess`。
- **永远不要忽略方向变化** — 游戏锁定为纵向但设备旋转？刺眼。处理`size_changed`信号或在project.godot中指定`window/handheld/orientation`。

---

```gdscript
# 用触摸替换鼠标/键盘
func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            on_touch_start(event.position)
        else:
            on_touch_end(event.position)
    
    elif event is InputEventScreenDrag:
        on_touch_drag(event.position, event.relative)
```

## 虚拟摇杆

```gdscript
# virtual_joystick.gd
extends Control

signal joystick_moved(direction: Vector2)

var is_pressed := false
var center: Vector2
var touch_index := -1

func _gui_input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            is_pressed = true
            center = event.position
            touch_index = event.index
        elif event.index == touch_index:
            is_pressed = false
            joystick_moved.emit(Vector2.ZERO)
    
    elif event is InputEventScreenDrag and event.index == touch_index:
        var direction := (event.position - center).normalized()
        joystick_moved.emit(direction)
```

## 响应式UI

```gdscript
# 适应屏幕大小
func _ready() -> void:
    get_viewport().size_changed.connect(_on_viewport_resized)
    _on_viewport_resized()

func _on_viewport_resized() -> void:
    var viewport_size := get_viewport().get_visible_rect().size
    var aspect := viewport_size.x / viewport_size.y
    
    if aspect < 1.5:  # 高屏幕
        $UI.layout_mode = VBoxContainer.LAYOUT_MODE_VERTICAL
    else:  # 宽屏幕
        $UI.layout_mode = HBoxContainer.LAYOUT_MODE_HORIZONTAL
```

## 电池优化

```gdscript
# 不活跃时降低帧率
func _notification(what: int) -> void:
    match what:
        NOTIFICATION_APPLICATION_FOCUS_OUT:
            Engine.max_fps = 30
        NOTIFICATION_APPLICATION_FOCUS_IN:
            Engine.max_fps = 60
```

## 安全区域（凹口）

```gdscript
func apply_safe_area() -> void:
    var safe_area := DisplayServer.get_display_safe_area()
    
    # 调整UI边距
    $UI.offset_top = safe_area.position.y
    $UI.offset_left = safe_area.position.x
```

## 性能设置

```ini
# project.godot 移动设置
[rendering]
renderer/rendering_method="mobile"
textures/vram_compression/import_etc2_astc=true

[display]
window/handheld/orientation="landscape"
```

## 应用商店元数据

- 图标：512x512（Android），1024x1024（iOS）
- 截图：多种分辨率
- 隐私政策必需
- 年龄分级

## 最佳实践

1. **触摸优先** - 为手指设计，非鼠标
2. **性能** - 在中端设备上目标60 FPS
3. **电池** - 后台运行时降低FPS
4. **权限** - 仅请求所需权限

## 参考
- 相关：`godot-export-builds`, `godot-ui-containers`

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
