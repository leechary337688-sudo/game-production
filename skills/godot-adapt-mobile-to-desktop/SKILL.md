---
名称：godot-adapt-mobile-to-desktop
描述："专家模式，用于将移动游戏扩展到桌面平台，包括鼠标/键盘控制、提高分辨率和图形保真度、扩展UI布局、设置菜单、窗口管理以及平台特定功能。使用于创建桌面端口或跨平台发布。触发关键词：鼠标控制、键盘快捷键、分辨率缩放、图形设置、全屏切换、窗口模式、Steam集成、桌面优化。"
---

# 适应：移动端到桌面端

专家指导，用于将移动游戏扩展到桌面平台。

## 绝不要做

- **绝不要保留仅触摸控制** — 添加鼠标/键盘替代方案。触摸控制在桌面上感觉笨拙且限制精度。
- **绝不要锁定到移动分辨率** — 桌面可以处理1920x1080及以上分辨率和更高帧率。放大UI，增加渲染距离。
- **绝不要隐藏图形设置** — 桌面玩家期望质量选项（分辨率、垂直同步、阴影、抗锯齿）。
- **绝不要使用移动尺寸UI** — 触摸目标（44pt）对鼠标来说太大。将按钮/文本大小减少30-50%。
- **绝不要忘记窗口管理** — 玩家期望全屏、无边框、最大化和多显示器支持。

---

## 可用脚本

> **强制**：在实现相应模式之前，阅读适当的脚本。

### [desktop_input_adapter.gd](scripts/desktop_input_adapter.gd)
桥接虚拟摇杆逻辑到键盘WASD。映射按键到输入向量并处理高DPI UI缩放。

### [hover_bridge.gd](scripts/hover_bridge.gd)
在移动优先的代码库中重新启用桌面悬停功能。添加工具提示、鼠标进入/退出信号和悬停视觉反馈。

---

## 控制方案扩展

### 触摸 → 鼠标转换

```gdscript
# 移动端：虚拟摇杆用于移动
var direction: Vector2 = virtual_joystick.get_direction()

# ⬇️ 桌面端：WASD + 鼠标瞄准

extends CharacterBody2D

func _physics_process(delta: float) -> void:
    # 键盘移动（WASD）
    var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = input.normalized() * SPEED
    
    # 鼠标瞄准
    var mouse_pos := get_global_mouse_position()
    look_at(mouse_pos)
    
    move_and_slide()

# 配置项目设置 → 输入映射：
# move_left: A, 左箭头
# move_right: D, 右箭头
# move_up: W, 上箭头
# move_down: S, 下箭头
```

### 添加键盘快捷键

```gdscript
# desktop_shortcuts.gd
extends Node

func _input(event: InputEvent) -> void:
    if event.is_action_pressed("toggle_fullscreen"):
        toggle_fullscreen()
    
    if event.is_action_pressed("quick_save"):
        save_game()
    
    if event.is_action_pressed("toggle_inventory"):
        $UI/Inventory.visible = not $UI/Inventory.visible

func toggle_fullscreen() -> void:
    if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
    else:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)

# 添加到项目设置 → 输入映射：
# toggle_fullscreen: F11
# quick_save: F5
# toggle_inventory: I, Tab
```

### 滚轮支持

```gdscript
# 移动端：捏合缩放
# 桌面端：滚轮缩放

func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_WHEEL_UP:
            camera.zoom *= 1.1
        elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
            camera.zoom *= 0.9
```

---

## 图形增强

### 分辨率缩放

```gdscript
# mobile_settings.gd（移动端）
func _ready() -> void:
    get_viewport().size = Vector2i(1280, 720)  # 移动分辨率

# ⬇️ desktop_settings.gd（桌面端）

extends Node

@export var supported_resolutions: Array[Vector2i] = [
    Vector2i(1280, 720),
    Vector2i(1920, 1080),
    Vector2i(2560, 1440),
    Vector2i(3840, 2160)
]

func _ready() -> void:
    if OS.get_name() in ["Windows", "macOS", "Linux"]:
        # 以原生分辨率开始
        var screen_size := DisplayServer.screen_get_size()
        get_window().size = screen_size
        
        # 启用更高品质
        enable_desktop_graphics()

func enable_desktop_graphics() -> void:
    # 启用MSAA
    get_viewport().msaa_2d = Viewport.MSAA_2X
    get_viewport().msaa_3d = Viewport.MSAA_4X
    
    # 启用屏幕空间AA
    get_viewport().screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
    
    # 更高阴影分辨率
    RenderingServer.directional_shadow_atlas_set_size(4096, true)
    
    # 启用后处理
    var env := get_viewport().world_3d.environment
    if env:
        env.glow_enabled = true
        env.ssao_enabled = true
        env.adjustment_enabled = true
```

### 设置菜单

```gdscript
# graphics_settings.gd
extends Control

@onready var resolution_option: OptionButton = $VBoxContainer/Resolution
@onready var quality_option: OptionButton = $VBoxContainer/Quality
@onready var vsync_check: CheckBox = $VBoxContainer/VSync
@onready var fullscreen_check: CheckBox = $VBoxContainer/Fullscreen

func _ready() -> void:
    populate_settings()
    load_settings()

func populate_settings() -> void:
    # 分辨率选项
    resolution_option.add_item("1280x720")
    resolution_option.add_item("1920x1080")
    resolution_option.add_item("2560x1440")
    resolution_option.add_item("3840x2160")
    
    # 品质预设
    quality_option.add_item("低")
    quality_option.add_item("中")
    quality_option.add_item("高")
    quality_option.add_item("超高")

func _on_resolution_selected(index: int) -> void:
    var resolutions := [
        Vector2i(1280, 720),
        Vector2i(1920, 1080),
        Vector2i(2560, 1440),
        Vector2i(3840, 2160)
    ]
    
    get_window().size = resolutions[index]
    save_settings()

func _on_quality_selected(index: int) -> void:
    match index:
        0:  # 低
            apply_low_quality()
        1:  # 中
            apply_medium_quality()
        2:  # 高
            apply_high_quality()
        3:  # 超高
            apply_ultra_quality()
    
    save_settings()

func apply_ultra_quality() -> void:
    get_viewport().msaa_3d = Viewport.MSAA_8X
    get_viewport().screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
    RenderingServer.directional_shadow_atlas_set_size(8192, true)
    
    var env := get_viewport().world_3d.environment
    if env:
        env.glow_enabled = true
        env.ssao_enabled = true
        env.ssil_enabled = true
        env.sdfgi_enabled = true

func _on_vsync_toggled(enabled: bool) -> void:
    if enabled:
        DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
    else:
        DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
    
    save_settings()

func _on_fullscreen_toggled(enabled: bool) -> void:
    if enabled:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
    else:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
    
    save_settings()

func save_settings() -> void:
    var config := ConfigFile.new()
    config.set_value("graphics", "resolution_index", resolution_option.selected)
    config.set_value("graphics", "quality", quality_option.selected)
    config.set_value("graphics", "vsync", vsync_check.button_pressed)
    config.set_value("graphics", "fullscreen", fullscreen_check.button_pressed)
    config.save("user://settings.cfg")

func load_settings() -> void:
    var config := ConfigFile.new()
    if config.load("user://settings.cfg") == OK:
        resolution_option.selected = config.get_value("graphics", "resolution_index", 1)
        quality_option.selected = config.get_value("graphics", "quality", 2)
        vsync_check.button_pressed = config.get_value("graphics", "vsync", true)
        fullscreen_check.button_pressed = config.get_value("graphics", "fullscreen", false)
        
        # 应用设置
        _on_resolution_selected(resolution_option.selected)
        _on_quality_selected(quality_option.selected)
        _on_vsync_toggled(vsync_check.button_pressed)
        _on_fullscreen_toggled(fullscreen_check.button_pressed)
```

---

## UI布局扩展

### 移动UI → 桌面UI

```gdscript
# 移动端：紧凑HUD，大触摸按钮
# 场景：MobileHUD.tscn
# - 虚拟摇杆（左下角）
# - 操作按钮（右下角，80x80px）

# ⬇️ 桌面端：分散UI，较小元素

# 场景：DesktopHUD.tscn
# - 生命/法力条（左上角，40px高）
# - 小地图（右上角，200x200px）
# - 快捷栏（底部中央，50x50px槽位）
# - 聊天（左下角，可调整大小）

extends Control

func _ready() -> void:
    if OS.has_feature("mobile"):
        _setup_mobile_ui()
    else:
        _setup_desktop_ui()

func _setup_mobile_ui() -> void:
    # 大按钮，底部角落
    $VirtualJoystick.visible = true
    $ActionButtons.scale = Vector2(1.5, 1.5)
    $Minimap.visible = false  # 太拥挤

func _setup_desktop_ui() -> void:
    # 紧凑，角落和边缘
    $VirtualJoystick.visible = false
    $ActionButtons.scale = Vector2(0.8, 0.8)
    $Minimap.visible = true
    $ChatBox.visible = true
```

---

## 窗口管理

### 多显示器支持

```gdscript
# window_manager.gd
extends Node

func _ready() -> void:
    # 检测显示器
    var screen_count := DisplayServer.get_screen_count()
    print("检测到 %d 个显示器" % screen_count)
    
    # 允许窗口在显示器之间拖动
    DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)

func move_to_monitor(monitor_index: int) -> void:
    var screen_pos := DisplayServer.screen_get_position(monitor_index)
    var screen_size := DisplayServer.screen_get_size(monitor_index)
    
    # 在目标显示器上居中窗口
    var window_size := get_window().size
    var centered_pos := screen_pos + (screen_size - window_size) / 2
    
    DisplayServer.window_set_position(centered_pos)
```

### 无边框全屏

```gdscript
func set_borderless_fullscreen(enabled: bool) -> void:
    if enabled:
        # 获取屏幕尺寸
        var screen_size := DisplayServer.screen_get_size()
        
        # 将窗口设置为屏幕尺寸
        get_window().size = screen_size
        get_window().position = Vector2i.ZERO
        
        # 移除边框
        DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
    else:
        DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, false)
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
```

---

## 平台特定功能

### Steam集成（示例）

```gdscript
# 需要GodotSteam插件
extends Node

var steam_initialized := false

func _ready() -> void:
    if OS.get_name() in ["Windows", "Linux", "macOS"]:
        initialize_steam()

func initialize_steam() -> void:
    var init_result := Steam.steamInit()
    if init_result.status == Steam.STEAM_OK:
        steam_initialized = true
        print("Steam已初始化")
        
        # 启用成就
        Steam.requestStats()

func unlock_achievement(achievement_id: String) -> void:
    if steam_initialized:
        Steam.setAchievement(achievement_id)
        Steam.storeStats()
```

### Discord丰富状态

```gdscript
# 需要Discord SDK集成
extends Node

func update_presence(state: String, details: String) -> void:
    if OS.get_name() == "Windows":
        # 更新Discord状态
        # （需要插件）
        pass
```

---

## 性能增强

### 解锁帧率

```gdscript
# 移动端：锁定到60 FPS
Engine.max_fps = 60

# 桌面端：解锁或匹配显示器刷新率
func _ready() -> void:
    if not OS.has_feature("mobile"):
        Engine.max_fps = 0  # 无限（使用垂直同步来限制）
        
        # 或匹配显示器：
        var refresh_rate := DisplayServer.screen_get_refresh_rate()
        Engine.max_fps = int(refresh_rate)
```

### 增加绘制距离

```gdscript
# 移动端：低绘制距离
var camera: Camera3D
camera.far = 100.0

# 桌面端：更高
camera.far = 500.0

# 同时增加阴影距离
var sun: DirectionalLight3D
sun.directional_shadow_max_distance = 200.0  # 从50增加
```

---

## 测试清单

- [ ] 鼠标控制感觉精确（无加速问题）
- [ ] 所有移动触摸控制都有键盘/鼠标等效
- [ ] 图形设置菜单正常工作
- [ ] 全屏、窗口化、无边框模式都功能正常
- [ ] 多显示器设置工作（拖动窗口、居中）
- [ ] 分辨率变化不崩溃或扭曲UI
- [ ] 垂直同步切换工作
- [ ] 在高端硬件上以144+ FPS运行
- [ ] 设置跨会话持久化
- [ ] 游戏良好扩展到超宽显示器（21:9, 32:9）


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
