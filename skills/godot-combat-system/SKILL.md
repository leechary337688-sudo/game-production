---
name: godot-combat-system
description: "包括命中框/伤害框架构、伤害计算（DamageData类）、生命值组件、战斗状态机、连击系统、技能冷却和伤害弹窗的专家模式。适用于动作游戏、RPG或格斗游戏。触发关键词：Hitbox、Hurtbox、DamageData、HealthComponent、combat_state、combo_system、ability_cooldown、invincibility_frames、damage_popup。"
---

# 战斗系统

构建灵活、基于组件的战斗系统的专家指导。

## 永远不要做

- **永远不要使用直接的伤害引用（`target.health -= 10`）** — 绕过护甲、抗性、事件。使用DamageData + HealthComponent模式。
- **永远不要忘记无敌帧** — 没有无敌帧，多段攻击每帧都会造成伤害。击中后添加0.5-1秒无敌时间。
- **永远不要让命中框永久激活** — 使用动画轨迹启用/禁用命中框。永久命中框会导致意外伤害。
- **永远不要使用组进行命中框过滤** — 使用碰撞层。组不尊重物理层并导致友军伤害。
- **永远不要在没有DamageData的情况下发出damage_received信号** — 原始int/float伤害丢失上下文（来源、类型、击退）。始终使用DamageData类。
---

## 可用脚本

> **强制**：在实现相应模式前阅读适当的脚本。

### [hitbox_hurtbox.gd](scripts/hitbox_hurtbox.gd)
基于组件的命中框，带命中停顿和击退。使用Engine.time_scale和ignore_time_scale计时器以实现正确的命中停顿冻结帧。

---

## 伤害系统

```gdscript
# damage_data.gd
class_name DamageData
extends RefCounted

var amount: float
var source: Node
var damage_type: String = "physical"
var knockback: Vector2 = Vector2.ZERO
var is_critical: bool = false

func _init(dmg: float, src: Node = null) -> void:
    amount = dmg
    source = src
```

## 伤害框/命中框模式

```gdscript
# hurtbox.gd
extends Area2D
class_name Hurtbox

signal damage_received(data: DamageData)

@export var health_component: Node

func _ready() -> void:
    area_entered.connect(_on_area_entered)

func _on_area_entered(area: Area2D) -> void:
    if area is Hitbox:
        var damage := area.get_damage()
        damage_received.emit(damage)
        
        if health_component:
            health_component.take_damage(damage)
```

```gdscript
# hitbox.gd
extends Area2D
class_name Hitbox

@export var damage: float = 10.0
@export var damage_type: String = "physical"
@export var knockback_force: float = 100.0
@export var owner_node: Node

func get_damage() -> DamageData:
    var data := DamageData.new(damage, owner_node)
    data.damage_type = damage_type
    
    # 计算击退方向
    if owner_node:
        var direction := (global_position - owner_node.global_position).normalized()
        data.knockback = direction * knockback_force
    
    return data
```

## 生命值组件

```gdscript
# health_component.gd
extends Node
class_name HealthComponent

signal health_changed(old_health: float, new_health: float)
signal died
signal healed(amount: float)

@export var max_health: float = 100.0
@export var current_health: float = 100.0
@export var invincible: bool = false

func take_damage(data: DamageData) -> void:
    if invincible:
        return
    
    var old_health := current_health
    current_health -= data.amount
    current_health = clampf(current_health, 0, max_health)
    
    health_changed.emit(old_health, current_health)
    
    if current_health <= 0:
        died.emit()

func heal(amount: float) -> void:
    var old_health := current_health
    current_health += amount
    current_health = minf(current_health, max_health)
    
    healed.emit(amount)
    health_changed.emit(old_health, current_health)

func is_dead() -> bool:
    return current_health <= 0
```

## 战斗状态机

```gdscript
# combat_state.gd
extends Node
class_name CombatState

enum State { IDLE, ATTACKING, BLOCKING, DODGING, STUNNED }

var current_state: State = State.IDLE
var can_act: bool = true

func enter_attack_state() -> bool:
    if not can_act:
        return false
    
    current_state = State.ATTACKING
    can_act = false
    return true

func enter_block_state() -> void:
    current_state = State.BLOCKING

func enter_dodge_state() -> bool:
    if not can_act:
        return false
    
    current_state = State.DODGING
    can_act = false
    return true

func exit_state() -> void:
    current_state = State.IDLE
    can_act = true
```

## 连击系统

```gdscript
# combo_system.gd
extends Node
class_name ComboSystem

signal combo_executed(combo_name: String)

@export var combo_window: float = 0.5
var combo_buffer: Array[String] = []
var last_input_time: float = 0.0

func register_input(action: String) -> void:
    var current_time := Time.get_ticks_msec() / 1000.0
    
    if current_time - last_input_time > combo_window:
        combo_buffer.clear()
    
    combo_buffer.append(action)
    last_input_time = current_time
    
    check_combos()

func check_combos() -> void:
    # 轻击 → 轻击 → 重击 = 特殊攻击
    if combo_buffer.size() >= 3:
        var last_three := combo_buffer.slice(-3)
        if last_three == ["light", "light", "heavy"]:
            execute_combo("special_attack")
            combo_buffer.clear()

func execute_combo(combo_name: String) -> void:
    combo_executed.emit(combo_name)
```

## 技能系统

```gdscript
# ability.gd
class_name Ability
extends Resource

@export var ability_name: String
@export var cooldown: float = 1.0
@export var damage: float = 25.0
@export var range: float = 100.0
@export var animation: String

var is_on_cooldown: bool = false

func can_use() -> bool:
    return not is_on_cooldown

func use(caster: Node) -> void:
    if not can_use():
        return
    
    is_on_cooldown = true
    
    # 执行技能逻辑
    _execute(caster)
    
    # 开始冷却
    await caster.get_tree().create_timer(cooldown).timeout
    is_on_cooldown = false

func _execute(caster: Node) -> void:
    # 在派生技能中覆盖
    pass
```

## 伤害弹窗

```gdscript
# damage_popup.gd
extends Label

func show_damage(amount: float, is_crit: bool = false) -> void:
    text = str(int(amount))
    
    if is_crit:
        modulate = Color.RED
        scale = Vector2(1.5, 1.5)
    
    var tween := create_tween()
    tween.set_parallel(true)
    tween.tween_property(self, "position:y", position.y - 50, 1.0)
    tween.tween_property(self, "modulate:a", 0.0, 1.0)
    tween.finished.connect(queue_free)
```

## 暴击

```gdscript
func calculate_damage(base_damage: float, crit_chance: float = 0.1) -> DamageData:
    var data := DamageData.new(base_damage)
    
    if randf() < crit_chance:
        data.is_critical = true
        data.amount *= 2.0
    
    return data
```

## 最佳实践

1. **分离关注点** - 生命值 ≠ 战斗 ≠ 移动
2. **使用信号** - 解耦系统
3. **使用Area2D用于命中框** - 内置碰撞检测
4. **无敌帧** - 防止垃圾伤害

## 参考
- 相关：`godot-2d-physics`、`godot-animation-player`、`godot-characterbody-2d`


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
