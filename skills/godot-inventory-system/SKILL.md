---
name: godot-inventory-system
description: "库存系统的专家蓝图（基于《暗黑破坏神》、《生化危机》、《我的世界》），涵盖槽位容器、堆叠逻辑、重量限制、装备系统和拖放UI。用于构建RPG库存、生存物品管理或战利品系统。关键词：库存、槽位、堆叠、装备、制作、物品、资源、拖放。"
---

# 库存系统

槽位管理、堆叠逻辑和基于资源的物品定义了稳健的库存系统。

## 可用脚本

### [grid_inventory_logic.gd](scripts/grid_inventory_logic.gd)
专家级网格库存，具有俄罗斯方块式放置逻辑。

### [inventory_grid.gd](scripts/inventory_grid.gd)
基于网格的库存控制器，带有拖放基础和自动排序。

## 库存系统中永不做的事情

- **永不使用节点作为物品** — `Item extends Node` = 内存泄漏噩梦。100个物品的库存 = 树中的100个节点。使用 `Item extends Resource` 以兼容保存。
- **永不在添加前忘记检查最大堆叠** — 没有堆叠逻辑的 `add_item()` = 物品静默消失。总是在创建新槽位前尝试堆叠。
- **永不直接从UI修改库存** — 点击时 `InventorySlotUI.item = null` = 状态不同步。UI应该发射信号，库存模型更新，然后UI通过信号刷新。
- **永不使用浮点数表示物品数量** — 浮点错误：10.0 - 0.1 * 100 ≠ 0。对可计数物品使用 `int`。仅对重量/体积限制使用浮点数。
- **永不在添加前忘记验证重量/容量** — 玩家添加1000kg物品到100kg库存？必须在添加前检查 `get_total_weight() + item.weight * amount <= max_weight`。
- **永不在循环内发射 `inventory_changed`** — 添加100个物品 = 100次UI刷新 = 延迟峰值。批量操作，循环完成后发射一次。

---

## 核心架构

```gdscript
# item.gd (Resource)
class_name Item
extends Resource

@export var id: String
@export var display_name: String
@export var icon: Texture2D
@export var max_stack: int = 1
@export var weight: float = 0.0
@export_multiline var description: String
```

## 库存管理器

```gdscript
# inventory.gd
class_name Inventory
extends Resource

signal item_added(item: Item, amount: int)
signal item_removed(item: Item, amount: int)
signal inventory_changed

@export var slots: Array[InventorySlot] = []
@export var max_slots: int = 20
@export var max_weight: float = 100.0

func _init() -> void:
    slots.resize(max_slots)
    for i in max_slots:
        slots[i] = InventorySlot.new()

func add_item(item: Item, amount: int = 1) -> bool:
    var remaining := amount
    
    # 首先尝试堆叠
    if item.max_stack > 1:
        for slot in slots:
            if slot.item == item and slot.amount < item.max_stack:
                var space := item.max_stack - slot.amount
                var to_add := mini(space, remaining)
                slot.amount += to_add
                remaining -= to_add
                
                if remaining <= 0:
                    item_added.emit(item, amount)
                    inventory_changed.emit()
                    return true
    
    # 添加到空槽位
    while remaining > 0:
        var empty_slot := find_empty_slot()
        if empty_slot == null:
            return false  # 库存已满
        
        var to_add := mini(item.max_stack, remaining)
        empty_slot.item = item
        empty_slot.amount = to_add
        remaining -= to_add
    
    item_added.emit(item, amount)
    inventory_changed.emit()
    return true

func remove_item(item: Item, amount: int = 1) -> bool:
    var remaining := amount
    
    for slot in slots:
        if slot.item == item:
            var to_remove := mini(slot.amount, remaining)
            slot.amount -= to_remove
            remaining -= to_remove
            
            if slot.amount <= 0:
                slot.clear()
            
            if remaining <= 0:
                item_removed.emit(item, amount)
                inventory_changed.emit()
                return true
    
    return false  # 物品不足

func has_item(item: Item, amount: int = 1) -> bool:
    var count := 0
    for slot in slots:
        if slot.item == item:
            count += slot.amount
    return count >= amount

func find_empty_slot() -> InventorySlot:
    for slot in slots:
        if slot.is_empty():
            return slot
    return null

func get_total_weight() -> float:
    var total := 0.0
    for slot in slots:
        if slot.item:
            total += slot.item.weight * slot.amount
    return total
```

## 库存槽位

```gdscript
# inventory_slot.gd
class_name InventorySlot
extends Resource

signal slot_changed

var item: Item = null
var amount: int = 0

func is_empty() -> bool:
    return item == null

func clear() -> void:
    item = null
    amount = 0
    slot_changed.emit()
```

## 装备系统

```gdscript
# equipment.gd
class_name Equipment
extends Resource

signal equipment_changed(slot: String, item: Item)

@export var weapon: Item = null
@export var armor: Item = null
@export var accessory: Item = null

func equip(slot: String, item: Item) -> Item:
    var old_item: Item = null
    
    match slot:
        "weapon":
            old_item = weapon
            weapon = item
        "armor":
            old_item = armor
            armor = item
        "accessory":
            old_item = accessory
            accessory = item
    
    equipment_changed.emit(slot, item)
    return old_item

func unequip(slot: String) -> Item:
    return equip(slot, null)

func get_total_stats() -> Dictionary:
    var stats := {
        "attack": 0,
        "defense": 0,
        "speed": 0
    }
    
    for item in [weapon, armor, accessory]:
        if item and item.has("stats"):
            for key in item.stats:
                stats[key] += item.stats[key]
    
    return stats
```

## UI集成

```gdscript
# inventory_ui.gd
extends Control

@onready var grid := $GridContainer
var inventory: Inventory

func _ready() -> void:
    inventory.inventory_changed.connect(refresh_ui)
    refresh_ui()

func refresh_ui() -> void:
    # 清除现有
    for child in grid.get_children():
        child.queue_free()
    
    # 创建槽位UI
    for slot in inventory.slots:
        var slot_ui := InventorySlotUI.new()
        slot_ui.setup(slot)
        grid.add_child(slot_ui)
```

## 制作集成

```gdscript
# crafting_recipe.gd
class_name CraftingRecipe
extends Resource

@export var result: Item
@export var result_amount: int = 1
@export var requirements: Array[CraftingRequirement]

func can_craft(inventory: Inventory) -> bool:
    for req in requirements:
        if not inventory.has_item(req.item, req.amount):
            return false
    return true

func craft(inventory: Inventory) -> bool:
    if not can_craft(inventory):
        return false
    
    # 移除材料
    for req in requirements:
        inventory.remove_item(req.item, req.amount)
    
    # 添加结果
    inventory.add_item(result, result_amount)
    return true
```

## 保存/加载

```gdscript
func save_inventory() -> Dictionary:
    return {
        "slots": slots.map(func(s): return s.to_dict())
    }

func load_inventory(data: Dictionary) -> void:
    for i in data.slots.size():
        slots[i].from_dict(data.slots[i])
    inventory_changed.emit()
```

## 最佳实践

1. **使用资源** - 物品作为资源，而不是类实例
2. **信号驱动的UI** - 发射信号，让UI监听
3. **堆叠逻辑** - 总是先检查 `max_stack`
4. **重量限制** - 在添加前验证

## 参考
- 相关：`godot-save-load-systems`, `godot-resource-data-patterns`


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
