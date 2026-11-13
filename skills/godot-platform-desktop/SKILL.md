---
name: godot-platform-desktop
description: "桌面平台专家蓝图，适用于Windows/Linux/macOS，涵盖键盘/鼠标控制、设置菜单、窗口管理（全屏、分辨率）、键位重映射和Steam集成。当针对PC平台或实现桌面特定功能时使用。关键词：桌面、Windows、Linux、macOS、设置、键位、ConfigFile、DisplayServer、Steam、全屏。"
---

# 平台: 桌面

设置的灵活性、窗口管理和键盘/鼠标精度定义了桌面游戏。

## 可用脚本

### [desktop_integration_manager.gd](scripts/desktop_integration_manager.gd)
专家级桌面集成（Steam成就、设置持久化、窗口管理）。

## 桌面开发中永远不要做的事

- **永远不要硬编码分辨率/全屏** — 在4K显示器上使用1920x1080全屏？模糊的混乱。始终提供带有分辨率下拉菜单和全屏切换的设置菜单。
- **永远不要保存设置到`res://`** — `res://`在导出的构建中是只读的。使用`user://settings.cfg`通过ConfigFile进行持久化配置。
- **永远不要忽略Alt+F4或Cmd+Q** — 玩家按下Alt+F4，什么都没发生=挫败感。处理`NOTIFICATION_WM_CLOSE_REQUEST`以优雅退出。
- **永远不要锁定重绑定** — 固定的WASD移动忽略了AZERTY/Dvorak键盘。必须允许通过设置进行InputMap重绑定。
- **永远不要错误使用`linear_to_db()`** — 音量滑块0-1直接到AudioServer？感知错误的曲线。使用`AudioServer.set_bus_volume_db(0, linear_to_db(slider.value))`。
- **永远不要跳过无边框全屏选项** — 独占全屏在Windows上破坏Alt+Tab。提供`WINDOW_MODE_EXCLUSIVE_FULLSCREEN` + `WINDOW_MODE_FULLSCREEN`（无边框）。

---

```gdscript
# settings.gd
extends Control

func _ready() -> void:
    load_settings()
    apply_settings()

func load_settings() -> void:
    var config := ConfigFile.new()
    config.load("user://settings.cfg")
    
    $Graphics/ResolutionDropdown.selected = config.get_value("graphics", "resolution", 0)
    $Graphics/FullscreenCheck.button_pressed = config.get_value("graphics", "fullscreen", false)
    $Audio/MasterSlider.value = config.get_value("audio", "master_volume", 1.0)

func save_settings() -> void:
    var config := ConfigFile.new()
    config.set_value("graphics", "resolution", $Graphics/ResolutionDropdown.selected)
    config.set_value("graphics", "fullscreen", $Graphics/FullscreenCheck.button_pressed)
    config.set_value("audio", "master_volume", $Audio/MasterSlider.value)
    config.save("user://settings.cfg")

func apply_settings() -> void:
    # 分辨率
    var resolutions := [Vector2i(1920, 1080), Vector2i(2560, 1440), Vector2i(3840, 2160)]
    var resolution := resolutions[$Graphics/ResolutionDropdown.selected]
    get_window().size = resolution
    
    # 全屏
    if $Graphics/FullscreenCheck.button_pressed:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
    else:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
    
    # 音频
    AudioServer.set_bus_volume_db(0, linear_to_db($Audio/MasterSlider.value))
```

## 键盘重映射

```gdscript
# 允许玩家重绑定按键
func rebind_action(action: String, new_key: Key) -> void:
    # 移除现有的
    InputMap.action_erase_events(action)
    
    # 添加新的
    var event := InputEventKey.new()
    event.keycode = new_key
    InputMap.action_add_event(action, event)
    
    # 保存
    save_input_map()
```

## 窗口管理

```gdscript
# 切换全屏
func toggle_fullscreen() -> void:
    if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
    else:
        DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
```

## Steam集成（如果使用）

```gdscript
# 使用GodotSteam插件
var steam_id: int

func _ready() -> void:
    if Steam.isSteamRunning():
        steam_id = Steam.getSteamID()
        Steam.achievement_progress.connect(_on_achievement_progress)

func unlock_achievement(name: String) -> void:
    Steam.setAchievement(name)
    Steam.storeStats()
```

## 最佳实践

1. **设置** - 广泛的图形/音频选项
2. **键位** - 允许重映射
3. **Alt+F4** - 支持退出快捷键
4. **保存位置** - 使用`user://`目录

## 参考
- 相关: `godot-export-builds`, `godot-save-load-systems`


### 相关
- 主技能: [godot-master](../godot-master/SKILL.md)
