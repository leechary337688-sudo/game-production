---
名称: godot-资源-数据-模式
描述: "使用Resource/RefCounted类进行数据导向设计的专家蓝图（物品数据库、角色状态、可重用数据结构）。涵盖类型化数组、序列化、嵌套资源和资源缓存。在实现数据系统或库存/状态/对话数据库时使用。关键词 Resource, RefCounted, ItemData, CharacterStats, 数据库, 序列化, @export, 类型化数组。"
---

# 资源与数据模式

基于资源的设计、类型化数组和序列化定义了可重用、检查器友好的数据结构。

## 可用脚本

### [data_factory_resource.gd](scripts/data_factory_resource.gd)
专家资源工厂，带有类型验证和批量实例化。

### [resource_pool.gd](scripts/resource_pool.gd)
Resource实例的对象池 – 减少热路径中的分配开销。

### [resource_validator.gd](scripts/resource_validator.gd)
验证Resource文件，查找缺少的导出和配置问题。

> **强制 – 针对数据系统**：在实现物品/状态数据库之前，请阅读data_factory_resource.gd。


## 资源设计中绝不要做的事情

- **绝不修改资源实例而不复制** — `player.stats.health -= 10` 在加载的资源上？这会修改磁盘上的 `.tres` 文件。必须先使用 `.duplicate()`。
- **绝不使用非类型化数组** — `@export var items: Array = []` 接受任何类型 = 运行时错误。使用 `Array[ItemData]` 以确保类型安全 + 自动补全。
- **绝不要忘记 @export 用于检查器编辑** — Resource属性没有 `@export`？在检查器中不可见。使用 `@export` 使属性可编辑。
- **绝不要在基础Resource中放入逻辑** — `Resource` 没有生命周期（`_ready`, `_process`）。使用 `extends RefCounted` 用于运行时逻辑，或附加到Node。
- **绝不序列化Node引用** — Resource中的 `@export var player_node: Node`？在保存/加载时会破坏。存储NodePath或UID代替。
- **绝不使用ResourceSaver.save()而不检查错误** — `ResourceSaver.save(res, path)` 可能失败（权限、无效路径）。必须检查返回错误代码。

---

| 类型 | 用例 | 可序列化 | 可保存到磁盘 | 检查器支持 |
|------|----------|-------------|-----------------|-------------------|
| `Resource` | 需要保存/加载的数据 | ✅ | ✅ | ✅ |
| `RefCounted` | 临时运行时数据 | ❌ | ❌ | ❌ |
| `Node` | 场景层次实体 | ✅（场景文件） | ✅ | ✅ |

## 何时使用资源

**使用资源用于：**
- 物品定义（武器、消耗品、装备）
- 角色状态/进度系统
- 技能/能力数据
- 配置文件
- 对话数据库
- 敌人/NPC模板

**使用RefCounted用于：**
- 临时计算
- 仅运行时状态机
- 不需要数据持久化的工具类

## 实现模式

### 模式 1: 自定义资源类

```gdscript
# item_data.gd
extends Resource
class_name ItemData

@export var item_name: String = ""
@export var description: String = ""
@export_enum("武器", "消耗品", "护甲") var item_type: int = 0
@export var icon: Texture2D
@export var value: int = 0
@export var stackable: bool = false
@export var max_stack: int = 1

func use() -> void:
    match item_type:
        0:  # 武器
            print("装备武器: ", item_name)
        1:  # 消耗品
            print("消耗: ", item_name)
        2:  # 护甲
            print("装备护甲: ", item_name)
```

**创建资源实例：**
1. 在检查器中：**右键点击 → 新建资源 → ItemData**
2. 填写属性，**保存**为 `res://items/health_potion.tres`

### 模式 2: 角色状态资源

```gdscript
# character_stats.gd
extends Resource
class_name CharacterStats

@export var max_health: int = 100
@export var max_mana: int = 50
@export var strength: int = 10
@export var defense: int = 5
@export var speed: float = 100.0

var current_health: int = max_health:
    set(value):
        current_health = clampi(value, 0, max_health)

var current_mana: int = max_mana:
    set(value):
        current_mana = clampi(value, 0, max_mana)

func take_damage(amount: int) -> int:
    var actual_damage := maxi(amount - defense, 0)
    current_health -= actual_damage
    return actual_damage

func heal(amount: int) -> void:
    current_health += amount

func duplicate_stats() -> CharacterStats:
    var stats := CharacterStats.new()
    stats.max_health = max_health
    stats.max_mana = max_mana
    stats.strength = strength
    stats.defense = defense
    stats.speed = speed
    stats.current_health = current_health
    stats.current_mana = current_mana
    return stats
```

**用法：**
```gdscript
# player.gd
extends CharacterBody2D

@export var stats: CharacterStats

func _ready() -> void:
    if stats:
        # 创建运行时副本以避免修改原始资源
        stats = stats.duplicate_stats()
```

### 模式 3: 数据库模式（资源数组）

```gdscript
# item_database.gd
extends Resource
class_name ItemDatabase

@export var items: Array[ItemData] = []

func get_item_by_name(item_name: String) -> ItemData:
    for item in items:
        if item.item_name == item_name:
            return item
    return null

func get_items_by_type(item_type: int) -> Array[ItemData]:
    var filtered: Array[ItemData] = []
    for item in items:
        if item.item_type == item_type:
            filtered.append(item)
    return filtered
```

**创建数据库：**
1. 创建 `ItemDatabase` 资源
2. 在检查器中展开 `items` 数组
3. 向数组添加 `ItemData` 资源
4. 保存为 `res://data/item_database.tres`

**用法：**
```gdscript
# 全局自动加载
const ITEM_DB := preload("res://data/item_database.tres")

func get_item(name: String) -> ItemData:
    return ITEM_DB.get_item_by_name(name)
```

### 模式 4: 仅运行时数据（RefCounted）

对于不需要持久化的数据：

```gdscript
# damage_calculation.gd
extends RefCounted
class_name DamageCalculation

var base_damage: int
var critical_hit: bool
var damage_type: String

func calculate_final_damage(target_defense: int) -> int:
    var final_damage := base_damage - target_defense
    if critical_hit:
        final_damage *= 2
    return maxi(final_damage, 1)
```

**用法：**
```gdscript
var calc := DamageCalculation.new()
calc.base_damage = 50
calc.critical_hit = randf() > 0.8
calc.damage_type = "物理"
var damage := calc.calculate_final_damage(enemy.defense)
```

## 高级模式

### 模式 5: 嵌套资源

```gdscript
# weapon_data.gd
extends ItemData
class_name WeaponData

@export var damage: int = 10
@export var attack_speed: float = 1.0
@export var special_effects: Array[StatusEffect] = []

# status_effect.gd
extends Resource
class_name StatusEffect

@export var effect_name: String
@export var duration: float
@export var damage_per_second: int
```

### 模式 6: 带有信号的资源脚本

```gdscript
# inventory.gd
extends Resource
class_name Inventory

signal item_added(item: ItemData)
signal item_removed(item: ItemData)

var items: Array[ItemData] = []

func add_item(item: ItemData) -> void:
    items.append(item)
    item_added.emit(item)

func remove_item(item: ItemData) -> void:
    items.erase(item)
    item_removed.emit(item)
```

### 模式 7: 运行时资源加载

```gdscript
# 动态加载资源
var item: ItemData = load("res://items/sword.tres")

# 预加载以提升性能（编译时）
const SWORD := preload("res://items/sword.tres")

# 加载目录中的所有资源
func load_all_items() -> Array[ItemData]:
    var items: Array[ItemData] = []
    var dir := DirAccess.open("res://items/")
    if dir:
        dir.list_dir_begin()
        var file_name := dir.get_next()
        while file_name != "":
            if file_name.ends_with(".tres"):
                var item: ItemData = load("res://items/" + file_name)
                items.append(item)
            file_name = dir.get_next()
    return items
```

## 最佳实践

### 1. 始终在运行时复制资源

```gdscript
# ✅ 好 – 创建实例副本
@export var stats: CharacterStats
func _ready():
    stats = stats.duplicate()  # 或自定义复制方法

# ❌ 坏 – 修改原始资源文件
@export var stats: CharacterStats
func _ready():
    stats.current_health -= 10  # 这会改变 .tres 文件！
```

### 2. 使用 `@export` 用于检查器编辑

```gdscript
# ✅ 使属性在检查器中可编辑
@export var max_health: int = 100
@export var icon: Texture2D
@export_range(0, 100) var drop_chance: int = 50
```

### 3. 按类别组织资源

```
res://data/
    items/
        weapons/
            sword.tres
            bow.tres
        consumables/
            health_potion.tres
    characters/
        player_stats.tres
        enemy_goblin.tres
    databases/
        item_database.tres
```

### 4. 类型化您的数组

```gdscript
# ✅ 好 – 类型化数组
@export var items: Array[ItemData] = []

# ❌ 坏 – 非类型化数组
@export var items: Array = []
```

## 保存/加载资源

```gdscript
# 保存资源到磁盘
func save_inventory(inventory: Inventory, path: String) -> void:
    ResourceSaver.save(inventory, path)

# 从磁盘加载资源
func load_inventory(path: String) -> Inventory:
    if ResourceLoader.exists(path):
        return ResourceLoader.load(path)
    return null
```

## 参考
- [Godot 文档: 资源](https://docs.godotengine.org/en/stable/tutorials/scripting/resources.html)
- [Godot 文档: 数据偏好](https://docs.godotengine.org/en/stable/tutorials/best_practices/data_preferences.html)


### 相关
- 主要技能: [godot-master](../godot-master/SKILL.md)
