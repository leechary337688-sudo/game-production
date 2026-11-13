---
name: godot-project-templates
description: "专家蓝图，用于特定游戏类型的项目模板（2D平台游戏、俯视视角RPG、3D FPS），包括目录结构、AutoLoad模式和核心系统。适用于启动新项目或迁移架构时使用。关键词：项目模板、样板、2D平台游戏、RPG、FPS、AutoLoad、场景结构。"
---

# 项目模板

特定游戏类型的脚手架、AutoLoad模式和模块化架构定义了快速原型开发。

## 可用脚本

### [base_game_manager.gd](scripts/base_game_manager.gd)
专家AutoLoad模板，用于游戏状态管理（暂停、场景转换、计分）。

## 项目模板中永远不要做的事

- **永远不要硬编码场景路径** — 在20个地方使用`get_tree().change_scene_to_file("res://levels/level_1.tscn")`？重构噩梦。使用AutoLoad + 常量或场景注册表。
- **永远不要忘记AutoLoad注册** — 模板包含`game_manager.gd`但未添加到项目设置？脚本不会加载。必须添加到项目 → AutoLoad。
- **永远不要使用`get_tree().paused`而不分组** — 暂停整个树 = 暂停菜单也冻结。使用处理模式组（`PROCESS_MODE_PAUSABLE` vs `PROCESS_MODE_ALWAYS`）。
- **永远不要在FPS中跳过Input.MOUSE_MODE_CAPTURED** — 没有鼠标捕获的FPS模板 = 游戏过程中光标可见。在玩家`_ready()`中设置。
- **永远不要直接复制粘贴模板** — 使用平台游戏模板做RPG？会导致架构债务。理解结构，然后适配。

---

### 目录结构

```
my_platformer/
├── project.godot
├── autoloads/
│   ├── game_manager.gd
│   ├── audio_manager.gd
│   └── scene_transitioner.gd
├── scenes/
│   ├── main_menu.tscn
│   ├── game.tscn
│   └── pause_menu.tscn
├── entities/
│   ├── player/
│   │   ├── player.tscn
│   │   ├── player.gd
│   │   └── player_states/
│   └── enemies/
│       ├── base_enemy.gd
│       └── goblin/
├── levels/
│   ├── level_1.tscn
│   └── tilesets/
├── ui/
│   ├── hud.tscn
│   └── themes/
├── audio/
│   ├── music/
│   └── sfx/
└── resources/
    └── data/
```

### 核心脚本

**game_manager.gd:**
```gdscript
extends Node

signal game_started
signal game_paused(paused: bool)
signal level_completed

var current_level: int = 1
var score: int = 0
var is_paused: bool = false

func start_game() -> void:
    score = 0
    current_level = 1
    SceneTransitioner.change_scene("res://levels/level_1.tscn")
    game_started.emit()

func pause_game(paused: bool) -> void:
    is_paused = paused
    get_tree().paused = paused
    game_paused.emit(paused)

func complete_level() -> void:
    current_level += 1
    level_completed.emit()
```

---

## 俯视视角RPG模板

### 目录结构

```
my_rpg/
├── autoloads/
│   ├── game_data.gd
│   ├── dialogue_manager.gd
│   └── inventory_manager.gd
├── entities/
│   ├── player/
│   ├── npcs/
│   └── interactables/
├── maps/
│   ├── overworld/
│   ├── dungeons/
│   └── interiors/
├── systems/
│   ├── combat/
│   ├── dialogue/
│   ├── quests/
│   └── inventory/
├── ui/
│   ├── inventory_ui.tscn
│   ├── dialogue_box.tscn
│   └── quest_log.tscn
└── resources/
    ├── items/
    ├── quests/
    └── dialogues/
```

### 核心系统

**inventory_manager.gd:**
```gdscript
extends Node

signal item_added(item: Resource)
signal item_removed(item: Resource)

var inventory: Array[Resource] = []

func add_item(item: Resource) -> void:
    inventory.append(item)
    item_added.emit(item)

func remove_item(item: Resource) -> bool:
    if item in inventory:
        inventory.erase(item)
        item_removed.emit(item)
        return true
    return false

func has_item(item_id: String) -> bool:
    for item in inventory:
        if item.id == item_id:
            return true
    return false
```

---

## 3D FPS模板

### 目录结构

```
my_fps/
├── autoloads/
│   ├── game_manager.gd
│   └── weapon_manager.gd
├── player/
│   ├── player.tscn
│   ├── player.gd
│   ├── camera_controller.gd
│   └── weapons/
│       ├── weapon_base.gd
│       ├── pistol/
│       └── rifle/
├── enemies/
│   ├── ai_controller.gd
│   └── soldier/
├── levels/
│   ├── level_1/
│   └── level_2/
├── ui/
│   ├── hud.tscn
│   └── crosshair.tscn
└── resources/
    ├── weapons/
    └── pickups/
```

### 玩家控制器

**player.gd:**
```gdscript
extends CharacterBody3D

@export var speed := 5.0
@export var jump_velocity := 4.5

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

@onready var camera: Camera3D = $Camera3D
@onready var weapon_holder: Node3D = $Camera3D/WeaponHolder

func _ready() -> void:
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
    
    var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_backward")
    var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)
    
    move_and_slide()
```

---

## 输入映射模板

```ini
# 所有模板都应包含这些操作：

[input]
move_left=Keys: A, Left, Gamepad Left
move_right=Keys: D, Right, Gamepad Right
move_up=Keys: W, Up, Gamepad Up
move_down=Keys: S, Down, Gamepad Down
jump=Keys: Space, Gamepad A
interact=Keys: E, Gamepad X
pause=Keys: Escape, Gamepad Start
ui_accept=Keys: Enter, Gamepad A
ui_cancel=Keys: Escape, Gamepad B
```

## 用法

1. 复制模板结构
2. 在`project.godot`中重命名项目
3. 注册AutoLoads
4. 配置输入映射
5. 开始开发

## 参考
- [GDSkills godot-project-foundations](../godot-project-foundations/SKILL.md)

### 相关
- 大师技能: [godot-master](../godot-master/SKILL.md)
