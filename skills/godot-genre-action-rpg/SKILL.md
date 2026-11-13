---
名称: godot-genre-action-rpg
描述: "Action RPGs的全面蓝图，包括实时战斗（命中盒/受伤盒，基于状态的伤害），角色进度（RPG状态，升级，技能树），战利品系统（程序化物品生成，词缀，稀有度等级），装备系统（装备槽，状态修饰符），和能力系统（冷却时间，法力消耗，AOE）。基于来自Diablo、Path of Exile、Souls-like开发者的专家ARPG设计。触发关键词：action_rpg, loot_generator, rpg_stats, skill_tree, hitbox_combat, item_affixes, equipment_slots, ability_cooldown, stat_scaling。"
---

# 类型: Action RPG

强调实时战斗、角色构建、战利品和进度的动作RPG专家蓝图。

## 永远不要做

- **永远不要让状态对玩家不可见** — 隐藏状态感觉像随机数。清楚地显示伤害数字、暴击几率%、护甲值。
- **永远不要使用线性伤害缩放** — `damage = level * 10` 使早期/晚期游戏无聊。使用指数：`damage = base * pow(1.15, level)`。
- **永远不要忘记防御的递减回报** — 护甲作为 `damage_reduction = armor / (armor + 100)` 防止无敌堆叠。
- **永远不要让战利品掉落感觉相同** — 用视觉效果（史诗=紫色光芒）、声音提示和有意义的统计差异来区分稀有度。
- **永远不要跳过命中恢复/踉跄** — 没有命中硬直的攻击感觉轻飘飘。添加0.2-0.5秒的踉跄以提供冲击反馈。
---

## 可用脚本

> **强制性的**：在实现相应模式之前阅读适当的脚本。

### [damage_label_manager.gd](scripts/damage_label_manager.gd)
池化的浮动伤害数字，具有垂直堆叠逻辑。预热池，处理暴击缩放，并通过tweens自动淡出。

### [telegraphed_enemy.gd](scripts/telegraphed_enemy.gd)
敌人攻击的AoE telegraph模式。带有视觉提示的蓄力动画给玩家闪避窗口，然后执行伤害区域。

---

## 核心循环

`战斗 → 战利品 → 升级 → 构建力量 → 挑战更硬内容 → 重复`

## 技能链

`godot-project-foundations`, `godot-characterbody-2d`, `godot-combat-system`, `godot-rpg-stats`, `godot-inventory-system`, `godot-ability-system`, `godot-quest-system`, `godot-economy-system`, `godot-save-load-systems`

---

## 战斗系统

### 带状态的实时战斗

```gdscript
class_name CombatController
extends Node

signal damage_dealt(target: Node, amount: int, type: String)
signal enemy_killed(enemy: Node, xp_reward: int)

func calculate_damage(attacker: RPGStats, defender: RPGStats, base_damage: int) -> Dictionary:
    # 物理伤害公式
    var attack_power := attacker.get_stat("strength") * 2 + base_damage
    var defense := defender.get_stat("armor")
    
    # 伤害减免公式（递减回报）
    var reduction := defense / (defense + 100.0)
    var final_damage := int(attack_power * (1.0 - reduction))
    
    # 暴击检查
    var crit_chance := attacker.get_stat("crit_chance") / 100.0
    var is_crit := randf() < crit_chance
    if is_crit:
        final_damage = int(final_damage * attacker.get_stat("crit_damage") / 100.0)
    
    return {
        "damage": max(1, final_damage),
        "is_crit": is_crit,
        "damage_type": "physical"
    }

func apply_damage(target: Node, damage_result: Dictionary) -> void:
    if target.has_method("take_damage"):
        target.take_damage(damage_result["damage"], damage_result["is_crit"])
        damage_dealt.emit(target, damage_result["damage"], damage_result["damage_type"])
```

### 命中盒/受伤盒战斗

```gdscript
class_name Hitbox
extends Area2D

@export var damage: int = 10
@export var knockback_force: float = 200.0
@export var attack_owner: Node

var has_hit: Array[Node] = []  # 防止每次挥动多次命中

func _ready() -> void:
    monitoring = false  # 仅在攻击帧期间启用

func enable() -> void:
    has_hit.clear()
    monitoring = true

func disable() -> void:
    monitoring = false

func _on_area_entered(area: Area2D) -> void:
    if area is Hurtbox:
        var target := area.owner_entity
        if target != attack_owner and target not in has_hit:
            has_hit.append(target)
            var result := CombatController.calculate_damage(
                attack_owner.stats, target.stats, damage
            )
            CombatController.apply_damage(target, result)
            apply_knockback(target)

func apply_knockback(target: Node) -> void:
    var direction := (target.global_position - attack_owner.global_position).normalized()
    if target.has_method("apply_knockback"):
        target.apply_knockback(direction * knockback_force)
```

---

## RPG状态系统

### 基于属性的状态

```gdscript
class_name RPGStats
extends Resource

signal stat_changed(stat_name: String, new_value: float)
signal level_up(new_level: int)

# 基本属性（升级时增加）
@export var strength: int = 10
@export var dexterity: int = 10
@export var intelligence: int = 10
@export var vitality: int = 10

# 派生状态（从属性计算）
var derived_stats: Dictionary = {}

# 来自装备、增益等的修饰符
var flat_modifiers: Dictionary = {}    # +50 生命值
var percent_modifiers: Dictionary = {} # +10% 伤害

var level: int = 1
var experience: int = 0
var skill_points: int = 0

func _init() -> void:
    recalculate_stats()

func recalculate_stats() -> void:
    derived_stats = {
        # 生命值：基于活力
        "max_health": vitality * 10 + 100,
        "health_regen": vitality * 0.5,
        
        # 法力值：基于智力
        "max_mana": intelligence * 8 + 50,
        "mana_regen": intelligence * 0.3,
        
        # 物理：基于力量和敏捷
        "physical_damage": strength * 2,
        "armor": strength + vitality,
        
        # 暴击：基于敏捷
        "crit_chance": 5.0 + dexterity * 0.2,
        "crit_damage": 150.0 + dexterity * 0.5,
        
        # 速度：基于敏捷
        "attack_speed": 1.0 + dexterity * 0.01,
        "move_speed": 100.0 + dexterity * 2
    }
    
    # 应用修饰符
    for stat_name in derived_stats:
        var base := derived_stats[stat_name]
        var flat := flat_modifiers.get(stat_name, 0.0)
        var percent := percent_modifiers.get(stat_name, 0.0)
        derived_stats[stat_name] = (base + flat) * (1.0 + percent / 100.0)

func get_stat(stat_name: String) -> float:
    if stat_name in derived_stats:
        return derived_stats[stat_name]
    return get(stat_name)

func add_experience(amount: int) -> void:
    experience += amount
    while experience >= get_xp_for_next_level():
        experience -= get_xp_for_next_level()
        level += 1
        skill_points += 5
        level_up.emit(level)

func get_xp_for_next_level() -> int:
    # 指数缩放
    return int(100 * pow(1.5, level - 1))
```

---

## 战利品系统

### 物品生成

```gdscript
class_name LootGenerator
extends Node

enum Rarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }

const RARITY_WEIGHTS := {
    Rarity.COMMON: 60,
    Rarity.UNCOMMON: 25,
    Rarity.RARE: 10,
    Rarity.EPIC: 4,
    Rarity.LEGENDARY: 1
}

const RARITY_AFFIX_COUNT := {
    Rarity.COMMON: 0,
    Rarity.UNCOMMON: 1,
    Rarity.RARE: 2,
    Rarity.EPIC: 3,
    Rarity.LEGENDARY: 4
}

@export var affix_pool: Array[ItemAffix]
@export var base_items: Array[ItemBase]

func generate_item(item_level: int, magic_find: float = 0.0) -> Item:
    var rarity := roll_rarity(magic_find)
    var base := base_items.pick_random()
    
    var item := Item.new()
    item.base = base
    item.rarity = rarity
    item.item_level = item_level
    
    # 基于稀有度滚动词缀
    var affix_count := RARITY_AFFIX_COUNT[rarity]
    var available_affixes := affix_pool.duplicate()
    
    for i in affix_count:
        if available_affixes.is_empty():
            break
        var affix := available_affixes.pick_random()
        available_affixes.erase(affix)
        item.affixes.append(generate_affix_roll(affix, item_level))
    
    return item

func roll_rarity(magic_find: float) -> Rarity:
    var weights := RARITY_WEIGHTS.duplicate()
    # 魔法发现增加稀有+掉落
    weights[Rarity.RARE] *= (1.0 + magic_find / 100.0)
    weights[Rarity.EPIC] *= (1.0 + magic_find / 100.0)
    weights[Rarity.LEGENDARY] *= (1.0 + magic_find / 100.0)
    
    var total := 0.0
    for w in weights.values():
        total += w
    
    var roll := randf() * total
    for rarity in weights:
        roll -= weights[rarity]
        if roll <= 0:
            return rarity
    return Rarity.COMMON

func generate_affix_roll(affix: ItemAffix, item_level: int) -> Dictionary:
    # 随着物品等级缩放词缀值
    var min_roll := affix.min_value * (1.0 + item_level * 0.1)
    var max_roll := affix.max_value * (1.0 + item_level * 0.1)
    return {
        "affix": affix,
        "value": randf_range(min_roll, max_roll)
    }
```

### 装备系统

```gdscript
class_name Equipment
extends Node

signal equipment_changed(slot: String, item: Item)

enum Slot { HEAD, CHEST, HANDS, LEGS, FEET, WEAPON, OFFHAND, RING1, RING2, AMULET }

var equipped: Dictionary = {}  # 槽位 -> 物品

func equip(item: Item) -> Item:
    var slot: Slot = item.base.slot
    var previous: Item = equipped.get(slot)
    
    # 卸下旧物品
    if previous:
        remove_item_stats(previous)
    
    # 装备新物品
    equipped[slot] = item
    apply_item_stats(item)
    equipment_changed.emit(Slot.keys()[slot], item)
    
    return previous  # 返回到库存

func apply_item_stats(item: Item) -> void:
    var stats := owner.stats as RPGStats
    
    # 基本状态
    for stat_name in item.base.base_stats:
        stats.flat_modifiers[stat_name] = stats.flat_modifiers.get(stat_name, 0) + item.base.base_stats[stat_name]
    
    # 词缀状态
    for affix_data in item.affixes:
        var affix := affix_data["affix"] as ItemAffix
        var value := affix_data["value"]
        if affix.is_percent:
            stats.percent_modifiers[affix.stat] = stats.percent_modifiers.get(affix.stat, 0) + value
        else:
            stats.flat_modifiers[affix.stat] = stats.flat_modifiers.get(affix.stat, 0) + value
    
    stats.recalculate_stats()
```

---

## 能力系统

### 技能树和解锁

```gdscript
class_name SkillTree
extends Resource

@export var skills: Array[Skill]
@export var connections: Dictionary  # skill_id -> Array[prerequisite_ids]

func can_unlock(skill_id: String, unlocked_skills: Array[String]) -> bool:
    if skill_id in unlocked_skills:
        return false  # 已经解锁
    
    var prereqs: Array = connections.get(skill_id, [])
    for prereq in prereqs:
        if prereq not in unlocked_skills:
            return false
    return true

func unlock_skill(skill_id: String, player: Node) -> bool:
    var skill := get_skill(skill_id)
    if not skill or player.stats.skill_points < skill.cost:
        return false
    
    player.stats.skill_points -= skill.cost
    player.unlocked_skills.append(skill_id)
    player.ability_manager.add_ability(skill.ability)
    return true
```

### 主动能力

```gdscript
class_name ActiveAbility
extends Resource

@export var name: String
@export var cooldown: float = 5.0
@export var mana_cost: int = 20
@export var damage_multiplier: float = 2.0
@export var aoe_radius: float = 0.0
@export var effect_scene: PackedScene

var current_cooldown: float = 0.0

func can_use(caster: Node) -> bool:
    return current_cooldown <= 0 and caster.stats.current_mana >= mana_cost

func use(caster: Node, target_position: Vector2) -> void:
    if not can_use(caster):
        return
    
    caster.stats.current_mana -= mana_cost
    current_cooldown = cooldown
    
    var effect := effect_scene.instantiate()
    effect.global_position = target_position
    effect.damage = int(caster.stats.get_stat("physical_damage") * damage_multiplier)
    effect.caster = caster
    caster.get_tree().current_scene.add_child(effect)

func update_cooldown(delta: float) -> void:
    current_cooldown = max(0, current_cooldown - delta)
```

---

## 敌人设计

### 缩放难度

```gdscript
class_name EnemySpawner
extends Node

@export var base_enemy_scene: PackedScene
@export var area_level: int = 1

func spawn_enemy(position: Vector2) -> Node:
    var enemy := base_enemy_scene.instantiate()
    enemy.global_position = position
    
    # 随着区域等级缩放状态
    var stats := enemy.stats as RPGStats
    var level_mult := 1.0 + (area_level - 1) * 0.15
    
    stats.vitality = int(stats.vitality * level_mult)
    stats.strength = int(stats.strength * level_mult)
    stats.recalculate_stats()
    
    # 缩放奖励
    enemy.xp_reward = int(enemy.xp_reward * level_mult)
    enemy.loot_table.item_level = area_level
    
    add_child(enemy)
    return enemy
```

---

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 状态感觉无意义 | 确保每个点显著影响游戏玩法 |
| 战利品感觉相同 | 稀有度之间的戏剧性视觉和机械差异 |
| 战斗太简单 | 连击系统、位置重要、敌人多样性 |
| 进度墙 | 多个可行路径、追赶机制 |
| 库存管理繁琐 | 自动排序、快速出售、存储标签 |

---

## 架构概述

```
自动加载:
├── 玩家状态 (godot-rpg-stats)
├── 库存管理器 (godot-inventory-system)
├── 任务管理器 (godot-quest-system)
├── 战利品生成器 (godot-economy-system)
└── 游戏管理器 (godot-scene-management)

玩家:
├── CharacterBody2D/3D
├── RPGStats
├── Equipment
├── AbilityManager
├── Hitbox/Hurtbox
└── 输入处理器

敌人:
├── AI 控制器 (状态机)
├── RPGStats (缩放)
├── 健康组件
├── 战利品表
└── Hitbox/Hurtbox
```

---

## Godot特定提示

1. **物品的资源**：使用 `Resource` 对于物品 - 易于序列化以保存/加载
2. **对象池**：池化伤害数字、投射物、物品拾取
3. **动画回调**：使用AnimationPlayer方法轨道来启用/禁用命中盒
4. **状态重新计算**：仅在装备/升级时重新计算，而不是每帧

---

## 参考游戏

- **Diablo / Path of Exile** - 以战利品为重点的ARPG
- **Elden Ring / Dark Souls** - 以战斗为重点的动作RPG
- **Hades** - Roguelike ARPG混合
- **Grim Dawn** - 深度角色构建


## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
