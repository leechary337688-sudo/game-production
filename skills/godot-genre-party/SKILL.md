---
name: godot-genre-party
description: "用于派对游戏的专家蓝图，包括迷你游戏资源系统（通过.tres文件定义）、本地多人游戏输入（4玩家控制器管理）、不对称游戏玩法（1v3平衡）、场景管理（干净地加载/卸载迷你游戏）、持久计分（跨回合跟踪胜利）和分屏渲染（每个玩家一个SubViewport）。适用于马里奥派对风格游戏或瓦里奥制造集合。触发关键词：party_game, minigame_collection, local_multiplayer, asymmetric_gameplay, split_screen, dynamic_input_mapping。"
---

# 类型：派对 / 迷你游戏集合

派对游戏的专家蓝图，平衡易用性、多样性和社交乐趣。

## 绝不做的

- **绝不做冗长教程** — 玩家想要即时乐趣。3秒循环GIF + 1句话指令是理想的。
- **绝不做过多停机时间** — 在10秒迷你游戏之间的加载会破坏节奏。保持资源轻量，使用线程加载或持久棋盘场景。
- **绝不做不一致的控制** — 迷你游戏A使用A跳跃，B使用B。标准化：A=接受/行动，B=返回/取消在所有迷你游戏中。
- **绝不做忘记动态输入映射** — 在运行时重映射InputMap（InputMap.action_add_event）为"p1_jump"、"p2_jump"每个控制器。
- **绝不做忽略无障碍性** — 色盲模式、视觉事件的音频提示、可调整难度。派对游戏需要包容性设计。
---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [party_input_router.gd](scripts/party_input_router.gd)
4玩家设备隔离用于本地多人游戏。映射device_id到player_id，处理加入请求，路由输入到玩家特定信号。

---

## 核心循环
1.  **大厅**：玩家加入并选择角色/颜色。
2.  **元游戏**：玩家在棋盘上移动或投票选择下一个游戏。
3.  **游玩**：简短、激烈的迷你游戏（30秒 - 2分钟）。
4.  **计分**：赢家获得点数/金币。
5.  **重复**：循环继续直到回合限制或分数限制。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 输入 | `input-mapping` | 动态处理2-4本地控制器 |
| 2. 场景 | `godot-scene-management` | 干净地加载/卸载迷你游戏 |
| 3. 数据 | `godot-resource-data-patterns` | 通过资源文件定义迷你游戏 |
| 4. UI | `godot-ui-containers` | 计分板、指令屏幕 |
| 5. 逻辑 | `godot-turn-system` | 管理“棋盘游戏”阶段 |

## 架构概览

### 1. 迷你游戏定义
使用资源定义什么是迷你游戏。

```gdscript
# minigame_data.gd
class_name MinigameData extends Resource

@export var title: String
@export var scene_path: String
@export var instructions: String
@export var is_1v3: bool = false
@export var thumbnail: Texture2D
```

### 2. 派对管理器
单例，在迷你游戏之间持久化。

```gdscript
# party_manager.gd
extends Node

var players: Array[PlayerData] = [] # 跟踪分数、输入设备ID、颜色
var current_round: int = 1
var max_rounds: int = 10

func start_minigame(minigame: MinigameData) -> void:
    # 1. 显示指令场景
    await show_instructions(minigame)
    # 2. 过渡到实际游戏
    get_tree().change_scene_to_file(minigame.scene_path)
    # 3. 传递玩家数据到新场景
    # （迷你游戏场景必须在_ready中查找PartyManager）
```

### 3. 迷你游戏基类
每个迷你游戏继承自此以确保兼容性。

```gdscript
# minigame_base.gd
class_name Minigame extends Node

signal game_ended(results: Dictionary)

func _ready() -> void:
    setup_players(PartyManager.players)
    start_countdown()

func end_game() -> void:
    # 计算赢家
    game_ended.emit(results)
    PartyManager.handle_minigame_end(results)
```

## 关键机制实现

### 本地多人游戏输入
处理动态设备分配。

```gdscript
# player_controller.gd
@export var player_id: int = 0 # 0, 1, 2, 3

func _physics_process(delta: float) -> void:
    var device = PartyManager.players[player_id].device_id
    # 使用特定设备ID输入
    var direction = Input.get_vector("p%s_left" % player_id, ...) 
    # 更好方法：在运行时明确重映射InputMap动作
```

### 不对称游戏玩法（1v3）
平衡“一个”与“多个”。
*   **一个**：强大，高HP，独特能力（例如，库巴套装）。
*   **多个**：单独弱，必须合作生存/获胜。

## Godot特定技巧

*   **SubViewport**：强大用于4玩家分屏。每个玩家获得一个摄像头，所有渲染相同世界（或不同世界！）。
*   **InputEventJoypadButton**：使用`Input.get_connected_joypads()`在大厅屏幕自动检测控制器。
*   **重映射**：Godot的`InputMap`系统可以在运行时使用`InputMap.action_add_event()`修改。动态创建“p1_jump”、“p2_jump”是常见模式。

## 常见陷阱

1.  **冗长教程**：玩家只想游玩。**修复**：3秒循环GIF + 1句话指令覆盖在游戏开始前。
2.  **停机时间**：在10秒迷你游戏之间的加载时间。**修复**：保持迷你游戏资源轻量。如果可能，使用“棋盘”场景在后台保持加载，或使用创建`Thread`加载。
3.  **混淆控制**：迷你游戏A使用“A”跳跃，迷你游戏B使用“B”。**修复**：标准化。“A”总是接受/行动。“B”总是返回/取消。


## 参考
- 主技能: [godot-master](../godot-master/SKILL.md)
