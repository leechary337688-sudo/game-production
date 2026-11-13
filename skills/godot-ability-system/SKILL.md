---
name: godot-ability-system
description: "用于RPG/动作能力系统的专家模式，包括冷却策略、连击系统、技能链、具有先决条件的技能树、升级路径和资源管理。适用于实现可解锁能力、角色进展或复杂技能系统。触发关键词：PlayerAbility、AbilityManager、cooldown、SkillTree、SkillNode、prerequisites、can_use、execute、ComboSystem、ability_chain、global_cooldown、charge_system、upgrade_path。"
---

# 能力系统

构建灵活、可扩展能力系统的专家指导。

## 绝不这样做

- **绝不在_process()中跟踪冷却** — 使用计时器或在_physics_process()中手动跟踪delta。_process()具有可变的delta，在慢速帧中会导致冷却不同步。
- **绝不忘记全局冷却（GCD）** — 没有GCD，玩家会滥用瞬发能力。在所有能力施放之间添加一个小的通用冷却（0.5-1.5秒）。
- **绝不将能力效果硬编码在管理器代码中** — 使用策略模式。每个能力都是一个具有execute()方法的资源，而不是一个巨大的switch语句。
- **绝不允许在动画锁定期间使用能力** — 在允许新施放前检查`is_casting`或`animation_playing`。中断动画会破坏状态机。
- **绝不保存冷却状态而不进行时间标准化** — 保存“cooldown_end_time”（OS.get_unix_time() + 剩余时间），而不是“remaining_time”。防止利用（更改系统时钟、重新加载游戏）。

---

## 可用脚本

> **强制**：在实现相应模式前阅读适当脚本。

### [ability_manager.gd](scripts/ability_manager.gd)
能力编排，包括冷却注册、can_use检查和视觉冷却进度。与角色逻辑解耦，适用于玩家、敌人或炮塔。

### [ability_resource.gd](scripts/ability_resource.gd)
可脚本化的能力资源基类，具有元数据、统计数据和效果数组。虚拟execute()方法用于继承（ProjectileAbility、BuffAbility）。

---

## 架构模式

### 基于资源的能力

```gdscript
# ability_base.gd - 所有能力的基础类
class_name Ability
extends Resource

@export var ability_id: String
@export var display_name: String
@export var icon: Texture2D
@export var description: String

@export_group("成本")
@export var mana_cost: int = 0
@export var stamina_cost: int = 0
@export var health_cost: int = 0  # 生命汲取能力

@export_group("时间")
@export var cooldown: float = 5.0
@export var cast_time: float = 0.0  # 0 = 瞬发
@export var channel_time: float = 0.0  # 引导能力

@export_group("解锁")
@export var unlock_level: int = 1
@export var prerequisites: Array[String] = []  # 其他能力ID

## 覆盖这些方法
func can_cast(caster: Node) -> bool:
    return true  # 额外检查（范围、目标等）

func execute(caster: Node, target: Node = null) -> void:
    pass  # 能力效果

func on_cast_start(caster: Node) -> void:
    pass  # 动画、效果

func on_cast_complete(caster: Node) -> void:
    execute(caster)

func on_cancel(caster: Node) -> void:
    pass  # 退还资源
```

### 具体能力示例

```gdscript
# fireball.gd
class_name FireballAbility
extends Ability

@export var damage: int = 50
@export var projectile_scene: PackedScene
@export var range: float = 500.0

func can_cast(caster: Node) -> bool:
    var target = caster.get_target()
    if not target:
        return false
    
    var distance := caster.global_position.distance_to(target.global_position)
    return distance <= range

func execute(caster: Node, target: Node = null) -> void:
    var projectile := projectile_scene.instantiate()
    caster.get_parent().add_child(projectile)
    projectile.global_position = caster.global_position
    projectile.target = target
    projectile.damage = damage
```

---

## 能力管理器（集中式）

### 核心管理器

```gdscript
# ability_manager.gd
class_name AbilityManager
extends Node

signal ability_cast(ability_id: String)
signal ability_ready(ability_id: String)
signal cooldown_started(ability_id: String, duration: float)

var abilities: Dictionary = {}  # ability_id → Ability
var cooldowns: Dictionary = {}  # ability_id → float (剩余时间)
var is_casting: bool = false
var global_cooldown: float = 0.0  # GCD计时器

@export var gcd_duration: float = 1.0  # 全局冷却

func register_ability(ability: Ability) -> void:
    abilities[ability.ability_id] = ability
    cooldowns[ability.ability_id] = 0.0

func can_use_ability(ability_id: String, caster: Node) -> bool:
    var ability := abilities.get(ability_id) as Ability
    if not ability:
        return false
    
    # 检查GCD
    if global_cooldown > 0.0:
        return false
    
    # 检查特定冷却
    if cooldowns.get(ability_id, 0.0) > 0.0:
        return false
    
    # 检查是否已在施放
    if is_casting and ability.cast_time > 0.0:
        return false
    
    # 检查资源
    if not has_resources(caster, ability):
        return false
    
    # 能力特定检查
    return ability.can_cast(caster)

func use_ability(ability_id: String, caster: Node, target: Node = null) -> bool:
    if not can_use_ability(ability_id, caster):
        return false
    
    var ability := abilities[ability_id]
    
    # 消耗资源
    consume_resources(caster, ability)
    
    # 开始施放
    if ability.cast_time > 0.0:
        start_cast(ability, caster, target)
    else:
        # 瞬发施放
        ability.execute(caster, target)
        trigger_cooldown(ability_id, ability.cooldown)
    
    ability_cast.emit(ability_id)
    return true

func start_cast(ability: Ability, caster: Node, target: Node) -> void:
    is_casting = true
    ability.on_cast_start(caster)
    
    # 为施放完成创建计时器
    var timer := get_tree().create_timer(ability.cast_time)
    await timer.timeout
    
    if is_casting:  # 未中断
        ability.on_cast_complete(caster)
        trigger_cooldown(ability.ability_id, ability.cooldown)
    
    is_casting = false

func interrupt_cast() -> void:
    if is_casting:
        is_casting = false
        # 如果需要，触发ability.on_cancel()

func trigger_cooldown(ability_id: String, duration: float) -> void:
    cooldowns[ability_id] = duration
    global_cooldown = gcd_duration
    cooldown_started.emit(ability_id, duration)

func _physics_process(delta: float) -> void:
    # 滴答冷却
    for ability_id in cooldowns.keys():
        if cooldowns[ability_id] > 0.0:
            cooldowns[ability_id] -= delta
            if cooldowns[ability_id] <= 0.0:
                ability_ready.emit(ability_id)
    
    # 滴答GCD
    if global_cooldown > 0.0:
        global_cooldown -= delta

func has_resources(caster: Node, ability: Ability) -> bool:
    return (caster.mana >= ability.mana_cost and
            caster.stamina >= ability.stamina_cost and
            caster.health > ability.health_cost)

func consume_resources(caster: Node, ability: Ability) -> void:
    caster.mana -= ability.mana_cost
    caster.stamina -= ability.stamina_cost
    caster.health -= ability.health_cost
```

---

## 高级模式

### 连击系统

```gdscript
# combo_tracker.gd
extends Node

var combo_chain: Array[String] = []
var combo_window: float = 2.0  # 继续连击的秒数
var last_ability_time: float = 0.0

func register_ability_use(ability_id: String) -> void:
    var current_time := Time.get_ticks_msec() * 0.001
    
    # 如果时间过长，重置
    if current_time - last_ability_time > combo_window:
        combo_chain.clear()
    
    combo_chain.append(ability_id)
    last_ability_time = current_time
    
    # 检查连击完成
    check_combos()

func check_combos() -> void:
    # 示例：“slash” → “slash” → “spin” = “whirlwind”
    if combo_chain.size() >= 3:
        var last_three := combo_chain.slice(-3)
        if last_three == ["slash", "slash", "spin"]:
            trigger_combo_ability("whirlwind")
            combo_chain.clear()

func trigger_combo_ability(combo_id: String) -> void:
    # 执行强大的连击能力
    pass
```

### 充能能力

```gdscript
# charge_ability.gd - 具有多次充能的能力（如《英雄联盟》中的闪现）
class_name ChargeAbility
extends Ability

@export var max_charges: int = 2
@export var charge_recharge_time: float = 20.0

var current_charges: int = max_charges
var recharge_timer: float = 0.0

func can_cast(caster: Node) -> bool:
    return current_charges > 0

func execute(caster: Node, target: Node = null) -> void:
    current_charges -= 1
    
    # 如果未达到最大充能，开始充能
    if current_charges < max_charges and recharge_timer == 0.0:
        recharge_timer = charge_recharge_time

func tick(delta: float) -> void:
    if recharge_timer > 0.0:
        recharge_timer -= delta
        if recharge_timer <= 0.0:
            current_charges += 1
            if current_charges < max_charges:
                recharge_timer = charge_recharge_time  # 继续充能
            else:
                recharge_timer = 0.0
```

---

## 技能树系统

### 技能节点

```gdscript
# skill_node.gd
class_name SkillNode
extends Resource

@export var skill_id: String
@export var display_name: String
@export var description: String
@export var icon: Texture2D

@export_group("要求")
@export var prerequisites: Array[String] = []  # 其他skill_ids
@export var character_level_required: int = 1
@export var points_required: int = 1
@export var mutually_exclusive_with: Array[String] = []  # 不能同时拥有

@export_group("进展")
@export var max_rank: int = 1
@export var current_rank: int = 0

@export_group("效果")
@export var unlocks_ability: String = ""  # 授予的能力ID
@export var stat_bonuses: Dictionary = {}  # “strength”: 5, “crit_chance”: 0.05

func can_unlock(player_skills: Dictionary, player_level: int, available_points: int) -> bool:
    # 已达到最大等级
    if current_rank >= max_rank:
        return false
    
    # 点数不足
    if available_points < points_required:
        return false
    
    # 等级要求
    if player_level < character_level_required:
        return false
    
    # 先决条件
    for prereq_id in prerequisites:
        if not player_skills.has(prereq_id) or player_skills[prereq_id].current_rank == 0:
            return false
    
    # 互斥性
    for exclusive_id in mutually_exclusive_with:
        if player_skills.has(exclusive_id) and player_skills[exclusive_id].current_rank > 0:
            return false
    
    return true

func unlock() -> void:
    current_rank += 1
```

### 技能树管理器

```gdscript
# skill_tree.gd
class_name SkillTree
extends Node

signal skill_unlocked(skill_id: String, rank: int)
signal points_changed(new_total: int)

var skills: Dictionary = {}  # skill_id → SkillNode
var skill_points: int = 0

func add_skill(skill: SkillNode) -> void:
    skills[skill.skill_id] = skill

func can_unlock_skill(skill_id: String, player_level: int) -> bool:
    var skill := skills.get(skill_id) as SkillNode
    if not skill:
        return false
    
    return skill.can_unlock(skills, player_level, skill_points)

func unlock_skill(skill_id: String, player_level: int) -> bool:
    if not can_unlock_skill(skill_id, player_level):
        return false
    
    var skill := skills[skill_id]
    skill.unlock()
    skill_points -= skill.points_required
    
    # 应用效果
    apply_skill_effects(skill)
    
    skill_unlocked.emit(skill_id, skill.current_rank)
    points_changed.emit(skill_points)
    return true

func apply_skill_effects(skill: SkillNode) -> void:
    # 如果指定，授予能力
    if skill.unlocks_ability != "":
        var ability_manager := get_node("/root/AbilityManager")
        # 注册新能力
    
    # 应用统计加成
    var player := get_tree().get_first_node_in_group("player")
    for stat_name in skill.stat_bonuses.keys():
        var bonus = skill.stat_bonuses[stat_name]
        player.set(stat_name, player.get(stat_name) + bonus)

func add_skill_points(amount: int) -> void:
    skill_points += amount
    points_changed.emit(skill_points)

func reset_tree(refund_points: bool = true) -> void:
    var total_spent := 0
    for skill in skills.values():
        total_spent += skill.current_rank * skill.points_required
        skill.current_rank = 0
    
    if refund_points:
        skill_points += total_spent
        points_changed.emit(skill_points)
```

---

## 冷却策略

### 每能力冷却（标准）

```gdscript
# 已在AbilityManager中展示
# 每个能力有独立的冷却
```

### 共享冷却（炉石传说风格）

```gdscript
# 所有“召唤”类型的能力共享冷却
var summon_cooldown: float = 0.0

func use_summon_ability(ability: Ability) -> void:
    ability.execute()
    summon_cooldown = 3.0  # 所有召唤有3秒冷却
```

### 充能系统（已在上方展示）

多次使用，随时间充能。

---

## 边界情况

### 冷却持久化

```gdscript
# save_system.gd
func save_ability_cooldowns() -> Dictionary:
    var data := {}
    var current_time := Time.get_unix_time_from_system()
    
    for ability_id in ability_manager.cooldowns.keys():
        var remaining := ability_manager.cooldowns[ability_id]
        if remaining > 0.0:
            data[ability_id] = current_time + remaining  # 绝对时间
    
    return data

func load_ability_cooldowns(data: Dictionary) -> void:
    var current_time := Time.get_unix_time_from_system()
    
    for ability_id in data.keys():
        var end_time: float = data[ability_id]
        var remaining := max(0.0, end_time - current_time)
        ability_manager.cooldowns[ability_id] = remaining
```

### 动画锁定

```gdscript
# 防止在攻击动画期间滥用能力
func _on_animation_player_animation_started(anim_name: String) -> void:
    if anim_name.begins_with("attack_"):
        ability_manager.is_casting = true

func _on_animation_player_animation_finished(anim_name: String) -> void:
    if anim_name.begins_with("attack_"):
        ability_manager.is_casting = false
```

## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
