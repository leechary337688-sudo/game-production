---
name: godot-genre-metroidvania
description: "Metroidvania游戏的专家蓝图，包括能力门控探索（锁/钥匙）、互联世界设计（带捷径的回溯）、持久状态跟踪（收集品、Boss击败）、房间过渡（无缝加载）、地图系统（基于网格的揭示）和能力多样性（战斗+遍历）。适用于探索平台游戏或动作冒险游戏。触发关键词：metroidvania, ability_gating, interconnected_world, backtracking, map_system, persistent_state, room_transition, soft_locks。"
---

# 类型：Metroidvania

Metroidvania游戏的专家蓝图，平衡探索、进度和回溯奖励。

## 绝不要做

- **绝不允许软锁** — 玩家必须始终有能力回溯。仔细设计“阀门”（单向下降）并提供逃生路线。
- **绝不要做空死胡同** — 每条路径都应有奖励（升级、 lore、货币）。空房间浪费玩家时间。
- **绝不要让回溯变得乏味** — 新能力应加速遍历（冲刺、传送）。或解锁连接遥远区域的捷径。
- **绝不要忘记持久状态** — 全局保存收集品拾取状态。如果玩家在房间A收集了物品，离开后必须保持收集。
- **绝不要在没有面包屑的情况下隐藏关键路径** — 使用地标、环境叙事或微妙视觉线索。玩家应建立心理地图。
---

## 可用脚本

> **强制**：在实现相应模式前阅读适当脚本。

### [minimap_fog.gd](scripts/minimap_fog.gd)
基于网格的迷雾战争小地图。通过玩家位置跟踪已揭示的瓷砖，仅绘制已访问的房间。通过TileMap可扩展以适应大地图。

### [progression_gate_manager.gd](scripts/progression_gate_manager.gd)
能力解锁 + 世界持久系统。跟踪解锁的能力和房间状态（门、Boss），启用全局碰撞门更新。

---

## 核心循环
1.  **探索**：玩家探索可用房间，直到被“锁”（障碍）阻挡。
2.  **发现**：玩家找到“钥匙”（能力/物品）或Boss。
3.  **获取**：玩家获得新的遍历或战斗能力。
4.  **回溯**：玩家使用新能力返回之前的锁。
5.  **进度**：新区域开放，循环重复。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 角色 | `godot-characterbody-2d`, `state-machines` | 紧密、响应式的移动（Coyote时间、缓冲区） |
| 2. 世界 | `godot-tilemap-mastery`, `level-design` | 互联地图、生物群落、地标 |
| 3. 系统 | `godot-save-load-systems`, `godot-scene-management` | 持久世界状态、房间过渡 |
| 4. UI | `ui-system`, `godot-inventory-system` | 地图系统、库存、HUD |
| 5. 抛光 | `juiciness` | 效果、氛围、环境叙事 |

## 架构概述

### 1. 游戏状态与持久性
Metroidvania游戏需要跟踪整个世界中每个收集品和Boss的状态。

```gdscript
# game_state.gd (自动加载)
extends Node

var collected_items: Dictionary = {} # "room_id_item_id": true
var unlocked_abilities: Array[String] = []
var map_visited_rooms: Array[String] = []

func register_collectible(id: String) -> void:
    collected_items[id] = true
    save_game()

func has_ability(ability_name: String) -> bool:
    return ability_name in unlocked_abilities
```

### 2. 房间过渡
无缝过渡是关键。使用 `SceneManager` 来处理实例化新房间和定位玩家。

```gdscript
# door.gd
extends Area2D

@export_file("*.tscn") var target_scene_path: String
@export var target_door_id: String

func _on_body_entered(body: Node2D) -> void:
    if body.is_in_group("player"):
        SceneManager.change_room(target_scene_path, target_door_id)
```

### 3. 能力系统（状态机集成）
能力应集成到玩家的状态机中。

```gdscript
# player_state_machine.gd
func _physics_process(delta):
    if Input.is_action_just_pressed("jump") and is_on_floor():
        transition_to("Jump")
    elif Input.is_action_just_pressed("jump") and not is_on_floor() and GameState.has_ability("double_jump"):
        transition_to("DoubleJump")
    elif Input.is_action_just_pressed("dash") and GameState.has_ability("dash"):
        transition_to("Dash")
```

## 关键机制实现

### 地图系统
基于网格或节点的地图对于导航至关重要。
*   **网格地图**：基于玩家位置自动填充单元格。
*   **房间状态**：跟踪“已访问”状态以揭示地图块。

```gdscript
# map_system.gd
func update_map(player_pos: Vector2) -> void:
    var grid_pos = local_to_map(player_pos)
    if not grid_map_data.has(grid_pos):
        grid_map_data[grid_pos] = VISITED
        ui_map.reveal_cell(grid_pos)
```

### 能力门控（“锁”）
检查特定能力的障碍物。

```gdscript
# breakable_wall.gd
extends StaticBody2D

@export var required_ability: String = "super_missile"

func take_damage(amount: int, ability_type: String) -> void:
    if ability_type == required_ability:
        destroy()
    else:
        play_deflect_sound()
```

## 常见陷阱

1.  **软锁**：确保玩家不能在没有离开能力的情况下卡在区域中。仔细设计“阀门”（单向下降）。
2.  **回溯乏味**：通过改变敌人、打开捷径或使用新能力加速遍历，使回溯变得有趣。
3.  **空奖励**：每个死胡同都应有奖励（健康升级、 lore、货币）。
4.  **迷失玩家**：使用视觉地标和环境叙事来引导玩家，无需显式标记（例如，“雕像房间”）。

## Godot特定提示

*   **Camera2D**：使用 `limit_left`、`limit_top` 等将相机限制在当前房间边界。在房间过渡时更新这些限制。
*   **资源预加载**：如果不使用硬过渡，预加载相邻房间以实现无缝开放世界感觉。
*   **RemoteTransform2D**：使用此功能让相机跟随玩家，但保持与玩家旋转/缩放的分离。
*   **TileMap层**：使用单独的层用于背景（视差）、游戏玩法（碰撞）和前景（视觉深度）。

## 设计原则（来自Dreamnoid）

*   **能力多样性**：能力应同时服务于遍历和战斗（例如，一个可以躲避攻击和跨越间隙的冲刺）。
*   **练习房间**：在安全环境中引入机制，然后在危险环境中测试玩家。
*   **地标**：独特的视觉特征帮助玩家建立心理地图。
*   **物品描述**：使用它们进行“微故事”来构建 lore，而不中断游戏玩法。

## 参考
- 主要技能：[godot-master](../godot-master/SKILL.md)
