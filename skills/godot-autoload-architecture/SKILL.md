---
name: godot-autoload-architecture
description: "Godot AutoLoad（单例）架构的专家模式，包括全局状态管理、场景转换、基于信号的通信、依赖注入、自动加载初始化顺序以及要避免的反模式。适用于游戏管理器、保存系统、音频控制器或跨场景资源。触发关键词：AutoLoad、单例、GameManager、SceneTransitioner、SaveManager、global_state、autoload_order、signal_bus、dependency_injection。"
---

# AutoLoad 架构

AutoLoad 是 Godot 的单例模式，允许脚本在整个项目生命周期中全局可访问。本技能指导实现健壮、可维护的单例架构。

## 切勿做

- **切勿在 `_init()` 中访问 AutoLoad** — 在 _init() 期间，AutoLoad 尚未保证存在。请使用 `_ready()` 或 `_enter_tree()` 代替。
- **切勿创建循环依赖** — 如果 GameManager 依赖 SaveManager 且 SaveManager 依赖 GameManager，初始化会死锁。使用信号或依赖注入。
- **切勿在 AutoLoad 中存储场景特定状态** — AutoLoad 在场景更改间持续存在。存储临时状态（当前敌人数量、UI 状态）会导致泄漏。在 `_ready()` 中重置。
- **切勿为所有事情使用 AutoLoad** — 过度依赖会创建“上帝对象”和紧密耦合。最多限制为 5-10 个 AutoLoad。使用场景树处理本地逻辑。
- **切勿假设 AutoLoad 初始化顺序** — AutoLoad 在项目设置中从上到下初始化。如果顺序重要，添加显式 `initialize()` 调用或谨慎使用 `@onready`。
---

## 可用脚本

> **强制要求**：在实现相应模式之前阅读适当的脚本。

### [service_locator.gd](scripts/service_locator.gd)
服务定位器模式，用于解耦系统访问。允许交换实现（例如 MockAudioManager）而不更改游戏代码。

### [stateless_bus.gd](scripts/stateless_bus.gd)
无状态信号总线模式。特定领域的信号（玩家健康变化、关卡完成）不存储状态。总线是邮局，不是仓库。

### [autoload_initializer.gd](scripts/autoload_initializer.gd)
管理显式初始化顺序和依赖注入以避免循环依赖。

> **不要加载** service_locator.gd，除非实现依赖注入模式。

---

## 何时使用 AutoLoad

**良好用例：**
- **游戏管理器**：PlayerManager、GameManager、LevelManager
- **全局状态**：分数、库存、玩家属性
- **场景转换**：SceneTransitioner 用于加载/卸载场景
- **音频管理**：全局音乐/音效控制器
- **保存/加载系统**：持久数据管理

**避免使用 AutoLoad：**
- 场景特定逻辑（使用场景树代替）
- 临时状态（使用信号或直接引用）
- 为简单项目过度架构

## 实现模式

### 步骤 1：创建单例脚本

**示例：GameManager.gd**
```gdscript
extends Node

# 全局事件的信号
signal game_started
signal game_paused(is_paused: bool)
signal player_died

# 全局状态
var score: int = 0
var current_level: int = 1
var is_paused: bool = false

func _ready() -> void:
    # 初始化 autoload 状态
    print("GameManager 已初始化")

func start_game() -> void:
    score = 0
    current_level = 1
    game_started.emit()

func pause_game(paused: bool) -> void:
    is_paused = paused
    get_tree().paused = paused
    game_paused.emit(paused)

func add_score(points: int) -> void:
    score += points
```

### 步骤 2：注册为 AutoLoad

**项目 → 项目设置 → AutoLoad**

1. 点击文件夹图标，选择 `game_manager.gd`
2. 设置节点名称：`GameManager`（PascalCase 约定）
3. 启用全局功能（如果需要）
4. 点击“添加”

**在 `project.godot` 中验证：**
```ini
[autoload]
GameManager="*res://autoloads/game_manager.gd"
```

`*` 前缀使其在启动时立即激活。

### 步骤 3：从任何脚本访问

```gdscript
extends Node2D

func _ready() -> void:
    # 访问单例
    GameManager.connect("game_paused", _on_game_paused)
    GameManager.start_game()

func _on_button_pressed() -> void:
    GameManager.add_score(100)

func _on_game_paused(is_paused: bool) -> void:
    print("游戏暂停：", is_paused)
```

## 最佳实践

### 1. 使用静态类型
```gdscript
# ✅ 良好
var score: int = 0

# ❌ 不佳
var score = 0
```

### 2. 为状态更改发射信号
```gdscript
# ✅ 良好 - 允许解耦监听器
signal score_changed(new_score: int)

func add_score(points: int) -> void:
    score += points
    score_changed.emit(score)

# ❌ 不佳 - 紧密耦合
func add_score(points: int) -> void:
    score += points
    ui.update_score(score)  # 不要直接调用 UI
```

### 3. 按功能组织 AutoLoad
```
res://autoloads/
    game_manager.gd
    audio_manager.gd
    scene_transitioner.gd
    save_manager.gd
```

### 4. 场景转换模式
```gdscript
# scene_transitioner.gd
extends Node

signal scene_changed(scene_path: String)

func change_scene(scene_path: String) -> void:
    # 淡出效果（可选）
    await get_tree().create_timer(0.3).timeout
    get_tree().change_scene_to_file(scene_path)
    scene_changed.emit(scene_path)
```

## 常见模式

### 游戏状态机
```gdscript
enum GameState { MENU, PLAYING, PAUSED, GAME_OVER }

var current_state: GameState = GameState.MENU

func change_state(new_state: GameState) -> void:
    current_state = new_state
    match current_state:
        GameState.MENU:
            # 加载菜单
            pass
        GameState.PLAYING:
            get_tree().paused = false
        GameState.PAUSED:
            get_tree().paused = true
        GameState.GAME_OVER:
            # 显示游戏结束屏幕
            pass
```

### 资源预加载
```gdscript
# 预加载重资源一次
const PLAYER_SCENE := preload("res://scenes/player.tscn")
const EXPLOSION_EFFECT := preload("res://effects/explosion.tscn")

func spawn_player(position: Vector2) -> Node2D:
    var player := PLAYER_SCENE.instantiate()
    player.global_position = position
    return player
```

## 测试 AutoLoad

由于 AutoLoad 总是加载，**避免在 `_ready()` 中进行大量初始化**。使用惰性初始化或显式初始化函数：

```gdscript
var _initialized: bool = false

func initialize() -> void:
    if _initialized:
        return
    _initialized = true
    # 重型设置在此处
```

## 参考
- [Godot 文档：单例（AutoLoad）](https://docs.godotengine.org/en/stable/tutorials/scripting/singletons_autoload.html)
- [最佳实践：场景组织](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
