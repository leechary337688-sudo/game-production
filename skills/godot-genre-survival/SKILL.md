---
name: godot-genre-survival
description: "生存游戏的专家蓝图（Minecraft, Don't Starve, The Forest, Rust），覆盖了需要系统、资源收集、制作配方、基地建设和进展平衡。用于构建开放世界生存、制作中心或资源管理游戏。关键词：生存、需要系统、制作、库存、饥饿、资源收集、基地建设。"
---

# 流派：生存

资源稀缺、需要管理和通过制作进展定义了生存游戏。

## 可用脚本

### [inventory_slot_resource.gd](scripts/inventory_slot_resource.gd)
使用资源以实现保存兼容性的专家库存槽模式。

## 核心循环
1.  **收集**：采集资源（木材、石头、食物）
2.  **制作**：将资源转换为工具/物品
3.  **建造**：构造庇护所/基地
4.  **生存**：管理需要（饥饿、口渴、环境威胁）
5.  **繁荣**：自动化和技术以超越早期困境

## 在生存游戏中绝对不要做的事

- **绝不要让收集变得繁琐而不缩放** — 50次点击获得1木材 = 杀乐趣。工具层级必须乘以产量：石斧 = 3木材，钢斧 = 10木材。尊重玩家时间。
- **绝不要使用即时死亡作为饥饿** — 0%饥饿 → 即时死亡 = 廉价。使用逐渐HP减少（2 HP/秒）。玩家应该看到死亡来临并急于寻找食物。
- **绝不允许无限库存堆叠** — 999堆叠所有物品移除了资源管理策略。使用重量系统或堆叠限制（每个槽64个）。
- **绝不要让制作配方成为猜测游戏** — 试错制作 = 1990年代设计。显示已发现的配方。发现可以存在，但一旦学会，必须持久。
- **绝不要让需要以恒定速率衰减，无论活动如何** — 饥饿在睡觉/跑步时以相同速度消耗？不真实。冲刺 = 3倍消耗，空闲 = 0.5倍消耗。
- **绝不要在玩家的床/重生点附近生成敌人** — 死亡，重生时遇到3个敌人 = 怒退。强制执行安全区域半径（50米）围绕重生点。

---

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 数据 | `resources`, `custom-resources` | 物品数据（重量、堆叠大小），配方 |
| 2. UI | `grid-containers`, `drag-and-drop` | 库存管理，制作菜单 |
| 3. 世界 | `tilemaps`, `noise-generation` | 程序地形，资源生成 |
| 4. 逻辑 | `state-machines`, `signals` | 玩家状态（需要），交互系统 |
| 5. 保存 | `file-system`, `json-serialization` | 保存世界状态，库存，玩家状态 |

## 架构概述

### 1. 物品数据（基于资源）
库存中的一切都是物品。

```gdscript
# item_data.gd
extends Resource
class_name ItemData

@export var id: String
@export var name: String
@export var icon: Texture2D
@export var max_stack: int = 64
@export var weight: float = 1.0
@export var consumables: Dictionary # { "hunger": 10, "health": 5 }
```

### 2. 库存系统
基于网格的数据结构。

```gdscript
# inventory.gd
extends Node

signal inventory_updated

var slots: Array[ItemSlot] = [] # Array of Resources or Dictionaries
@export var size: int = 20

func add_item(item: ItemData, amount: int) -> int:
    # 1. 检查现有堆叠
    # 2. 添加到空槽
    # 3. 返回剩余数量（无法放置的）
    pass
```

### 3. 交互系统
收获、拾取或打开东西的通用方式。

```gdscript
# interactable.gd
extends Area2D
class_name Interactable

@export var prompt: String = "交互"

func interact(player: Player) -> void:
    _on_interact(player)

func _on_interact(player: Player) -> void:
    pass # 覆盖这个
```

## 关键机制实现

### 需要系统
随着时间减少的简单浮点值。

```gdscript
# needs_manager.gd
var hunger: float = 100.0
var thirst: float = 100.0
var decay_rate: float = 1.0

func _process(delta: float) -> void:
    hunger -= decay_rate * delta
    thirst -= decay_rate * 1.5 * delta
    
    if hunger <= 0:
        take_damage(delta)
```

### 制作逻辑
检查玩家是否有成分 -> 移除成分 -> 添加结果。

```gdscript
func craft(recipe: Recipe) -> bool:
    if not has_ingredients(recipe.ingredients):
        return false
        
    remove_ingredients(recipe.ingredients)
    inventory.add_item(recipe.result_item, recipe.result_amount)
    return true
```

## Godot特定技巧

*   **TileMaps**：使用 `TileMap`（Godot 3）或 `TileMapLayer`（Godot 4）用于世界。
*   **FastNoiseLite**：内置噪声生成器用于程序地形（树木、岩石、生物群落）。
*   **ResourceSaver**：如果设置正确并带有 `export` 变量，直接将 `Inventory` 资源保存到磁盘。
*   **Y-Sort**：对于俯视2D游戏至关重要，以便玩家正确地排序在树后/前。

## 常见陷阱

1.  **繁琐**：收集时间太长。**修复**：使用工具层级缩放资源收集（石斧 = 1木材，钢斧 = 5木材）。
2.  **库存混乱**：太多不堆叠的唯一物品。**修复**：慷慨地处理堆叠大小和存储选项。
3.  **无目标**：玩家生存但感到无聊。**修复**：添加科技树或要努力达到的“老板”。

## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
