---
name: godot-input-handling
description: "输入处理的专家模式，涵盖InputMap动作、InputEvent处理、控制器支持、重绑定、死区和输入缓冲。在设置玩家控制、实现输入系统或添加游戏手柄/可访问性功能时使用。关键词：InputMap, InputEvent, 游戏手柄, 控制器, 重绑定, 死区, 输入缓冲。"
---

# 输入处理

处理键盘、鼠标、游戏手柄和触摸输入，带有适当的缓冲和可访问性支持。

## 可用脚本

### [input_buffer.gd](scripts/input_buffer.gd)
响应式控制的输入缓冲 - 缓冲动作150毫秒以确保紧密的游戏感。

### [input_remapper](scripts/input_remapper.gd)
运行时输入重绑定，带有冲突检测和保存/加载持久性。

> **强制 - 为了响应式控制**：在实现跳跃/冲刺机制之前阅读input_buffer.gd。

## 输入处理中永不做的事情

- **永不 在`_process()`中轮询输入进行游戏动作** — 使用`_physics_process()`或`_unhandled_input()`。`_process()`依赖于帧率，低FPS时会导致输入丢失。
- **永不 使用硬编码的按键检查（`KEY_W`, `KEY_SPACE`）** — 使用InputMap动作。硬编码的按键 = 无法重绑定，破坏非QWERTY键盘。
- **永不 忽略控制器死区** — 摇杆漂移在0.05幅度 = 角色自行行走。始终使用0.15-0.2死区实现`Input.get_axis()`。
- **永不 假设单一输入设备** — 玩家可能中途切换键盘 → 游戏手柄。监听`Input.joy_connection_changed`并动态更新UI提示。
- **永不 使用`_input()`进行游戏动作** — `_input()`触发所有事件（包括UI）。使用`_unhandled_input()`，只有当UI未消耗事件时才触发。
- **永不 忘记响应式控制的输入缓冲** — 玩家在落地前50毫秒按下跳跃？没有缓冲，跳跃就丢失了。缓冲输入100-150毫秒以获得紧密的游戏感。

---

## InputMap动作

**设置：** 项目设置 → 输入映射 → 添加动作

```gdscript
# 检查动作是否在本帧按下
if Input.is_action_just_pressed("jump"):
    jump()

# 检查动作是否被按住
if Input.is_action_pressed("fire"):
    shoot()

# 检查动作是否被释放
if Input.is_action_just_released("jump"):
    release_jump()

# 获取轴（-1到1）
var direction := Input.get_axis("move_left", "move_right")

# 获取向量
var input_vector := Input.get_vector("left", "right", "up", "down")
```

## InputEvent处理

```gdscript
func _input(event: InputEvent) -> void:
    if event is InputEventKey:
        if event.keycode == KEY_ESCAPE and event.pressed:
            pause_game()
    
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
            click_position = event.position
```

## 游戏手柄支持

```gdscript
# 检测控制器连接
func _ready() -> void:
    Input.joy_connection_changed.connect(_on_joy_connection_changed)

func _on_joy_connection_changed(device: int, connected: bool) -> void:
    if connected:
        print("控制器 ", device, " 已连接")
```

## 参考
- [Godot 文档：InputEvent](https://docs.godotengine.org/en/stable/tutorials/inputs/inputevent.html)

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
