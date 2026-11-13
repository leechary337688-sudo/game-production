---
名称: godot-rpg-stats
描述: "使用基于资源的统计、可堆叠的修改器和衍生统计计算的RPG统计系统专家蓝图。在实现角色进度或装备/增益系统时使用。关键词：统计、属性、等级、修改器、CharacterStats、衍生统计、伤害计算、XP。"
---

# RPG统计

基于资源的统计、修改器堆栈和衍生计算定义了灵活的角色进度。

## 可用脚本

### [stat_resource.gd](scripts/stat_resource.gd)
具有缓存、脏标志和修改器堆栈的稳健基于资源的统计系统。

### [modifier_stack_stats.gd](scripts/modifier_stack_stats.gd)
具有加法/乘法修改器堆栈和优先级排序的专家统计系统。

## 在RPG统计中绝不做的

- **绝不使用整数表示百分比** — `var critical_chance: int = 50` 表示50%？整数除法会导致截断错误。使用`float`（0.0-1.0 或 0.0-100.0）。
- **绝不修改统计而不发射信号** — UI显示健康条但`stats.current_health -= 10`不更新？必须在统计变化时发射信号。
- **绝不使用仅加法修改器** — 增益在等级1时增加+10力量（10基础）= 100%增加。相同增益在等级50时（100基础）= 10%增加。使用乘法或混合。
- **绝不跳过修改器ID** — `add_modifier("strength", 5)`没有ID？以后无法移除特定增益。必须使用唯一ID（例如"sword_buff"、"potion_123"）。
- **绝不使用没有上限的指数XP公式** — `xp_to_next = level * 1000`？等级100 = 100k XP，等级1000 = 1M。使用平方根/对数或平坦缩放。
- **绝不要忘记钳制衍生统计** — `max_health = vitality * 10`？来自减益的负活力 = 负健康 = 崩溃。使用`maxi(value, 1)`。

---

```gdscript
# stats.gd
class_name Stats
extends Resource

signal stat_changed(stat_name: String, old_value: float, new_value: float)
signal level_up(new_level: int)

@export var level: int = 1
@export var experience: int = 0
@export var experience_to_next_level: int = 100

# 基础属性
@export var strength: int = 10
@export var dexterity: int = 10
@export var intelligence: int = 10
@export var vitality: int = 10

# 衍生属性（从基础计算）
var max_health: int:
    get: return vitality * 10
var attack_power: int:
    get: return strength * 2
var defense: int:
    get: return strength + (vitality / 2)
var magic_power: int:
    get: return intelligence * 3
var critical_chance: float:
    get: return dexterity * 0.01

# 修改器
var modifiers: Dictionary = {}

func add_experience(amount: int) -> void:
    experience += amount
    
    while experience >= experience_to_next_level:
        level_up_character()

func level_up_character() -> void:
    level += 1
    experience -= experience_to_next_level
    experience_to_next_level = int(experience_to_next_level * 1.5)
    
    # 增加基础属性
    strength += 2
    dexterity += 2
    intelligence += 2
    vitality += 2
    
    level_up.emit(level)

func get_stat(stat_name: String) -> float:
    var base_value: float = get(stat_name)
    var modifier_bonus := get_modifier_total(stat_name)
    return base_value + modifier_bonus

func add_modifier(stat_name: String, modifier_id: String, value: float) -> void:
    if not modifiers.has(stat_name):
        modifiers[stat_name] = {}
    
    modifiers[stat_name][modifier_id] = value

func remove_modifier(stat_name: String, modifier_id: String) -> void:
    if modifiers.has(stat_name):
        modifiers[stat_name].erase(modifier_id)

func get_modifier_total(stat_name: String) -> float:
    if not modifiers.has(stat_name):
        return 0.0
    
    var total := 0.0
    for value in modifiers[stat_name].values():
        total += value
    return total
```

## 装备统计

```gdscript
# equipment_item.gd
extends Item
class_name EquipmentItem

@export var stat_bonuses: Dictionary = {
    "strength": 5,
    "dexterity": 3
}

func on_equip(stats: Stats) -> void:
    for stat_name in stat_bonuses:
        stats.add_modifier(stat_name, "equipment_" + id, stat_bonuses[stat_name])

func on_unequip(stats: Stats) -> void:
    for stat_name in stat_bonuses:
        stats.remove_modifier(stat_name, "equipment_" + id)
```

## 状态效果

```gdscript
# status_effect.gd
class_name StatusEffect
extends Resource

@export var effect_id: String
@export var duration: float
@export var stat_modifiers: Dictionary = {}

func apply(stats: Stats) -> void:
    for stat_name in stat_modifiers:
        stats.add_modifier(stat_name, "status_" + effect_id, stat_modifiers[stat_name])

func remove(stats: Stats) -> void:
    for stat_name in stat_modifiers:
        stats.remove_modifier(stat_name, "status_" + effect_id)
```

## 伤害计算

```gdscript
func calculate_damage(attacker_stats: Stats, defender_stats: Stats) -> float:
    var base_damage := float(attacker_stats.attack_power)
    var defense := float(defender_stats.defense)
    
    # 伤害减少公式
    var damage := base_damage * (100.0 / (100.0 + defense))
    
    # 暴击命中
    if randf() < attacker_stats.critical_chance:
        damage *= 2.0
    
    return maxf(damage, 1.0)  # 最小1点伤害
```

## 技能要求

```gdscript
# skill.gd
class_name Skill
extends Resource

@export var required_level: int = 1
@export var required_stats: Dictionary = {
    "strength": 15,
    "intelligence": 10
}

func can_use(stats: Stats) -> bool:
    if stats.level < required_level:
        return false
    
    for stat_name in required_stats:
        if stats.get_stat(stat_name) < required_stats[stat_name]:
            return false
    
    return true
```

## 最佳实践

1. **衍生统计** - 从基础属性计算
2. **修改器** - 临时/永久加成
3. **公式平衡** - 避免指数级力量膨胀

## 参考
- 相关: `godot-combat-system`, `godot-inventory-system`


### 相关
- 主技能: [godot-master](../godot-master/SKILL.md)
