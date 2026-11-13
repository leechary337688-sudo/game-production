---
name: godot-composition
description: "专家级架构标准，用于使用组合模式（实体-组件）构建可扩展的Godot游戏（RPG、平台游戏、射击游戏）。在设计玩家控制器、NPC、敌人、武器或复杂游戏系统时使用。强制游戏实体使用'Has-A'关系。触发关键词：Entity-Component, ECS, Gameplay, Actors, NPCs, Enemies, Weapons, Hitboxes, Game Loop, Level Design。"
---

# Godot组合架构

## 核心理念
这个技能强制**组合优于继承**（"Has-a" vs "Is-a"）。
在Godot中，节点**就是**组件。一个复杂实体（如玩家）只是一个编排器，管理专门的工人节点（组件）。

### 黄金规则
1.  **单一职责**：一个脚本 = 一项工作。
2.  **封装**：组件是“自私的”。它们处理内部逻辑，但不知道*谁*拥有它们。
3.  **编排器**：根脚本（例如，`player.gd`）**不执行逻辑**。它只管理状态并在组件之间传递数据。
4.  **解耦**：组件通过**信号**（向上）和**方法**（向下）通信。

---

## 反模式（切勿这样做）
- **切勿**使用深层次继承链（例如，`Player > Entity > LivingThing > Node`）。这会创建脆弱的“上帝类”。
- **切勿**使用`get_node("Path/To/Thing")`或`$`语法来引用组件。如果场景树更改，这会破坏代码。
- **切勿**让组件直接引用父节点（除非通过类型注入绝对必要）。
- **切勿**在单个脚本中混合输入、物理和游戏逻辑。

---

## 实现标准

### 1. 连接策略：类型化导出
不要依赖树顺序。通过`@export`和静态类型使用显式依赖注入。

**严格Godot组合的“Godot方式”：**
```gdscript
# 编排器（例如，player.gd）
class_name Player extends CharacterBody3D

# 依赖注入：定义背包中的“插槽”
@export var health_component: HealthComponent
@export var movement_component: MovementComponent
@export var input_component: InputComponent

# 在编辑器中使用场景唯一名称（%）进行自动分配
# 或在检查器中拖放。
```

### 2. 组件思维
组件必须定义`class_name`以被识别为类型。

**标准组件模板：**
```gdscript
class_name MyComponent extends Node 
# 使用Node用于逻辑，Node3D/2D如果需要位置

@export var stats: Resource # 组件可以持有自己的数据
signal happened_something(value)

func do_logic(delta: float) -> void:
    # 执行特定任务
    pass
```

---

## 标准组件

### 输入组件（感官）
**职责**：读取硬件状态。存储它。不要对其采取行动。
*状态*：`move_dir`, `jump_pressed`, `attack_just_pressed`。

```gdscript
class_name InputComponent extends Node

var move_dir: Vector2
var jump_pressed: bool

func update() -> void:
    # 由编排器每帧调用
    move_dir = Input.get_vector("left", "right", "up", "down")
    jump_pressed = Input.is_action_just_pressed("jump")
```

### 移动组件（腿）
**职责**：操纵物理体。处理速度/重力。
**约束**：需要引用它移动的物理体。

```gdscript
class_name MovementComponent extends Node

@export var body: CharacterBody3D # 我们移动的东西
@export var speed: float = 8.0
@export var jump_velocity: float = 12.0

func tick(delta: float, direction: Vector2, wants_jump: bool) -> void:
    if not body: return
    
    # 处理重力
    if not body.is_on_floor():
        body.velocity.y -= 9.8 * delta
        
    # 处理移动
    if direction:
        body.velocity.x = direction.x * speed
        body.velocity.z = direction.y * speed # 3D转换
    else:
        body.velocity.x = move_toward(body.velocity.x, 0, speed)
        body.velocity.z = move_toward(body.velocity.z, 0, speed)
        
    # 处理跳跃
    if wants_jump and body.is_on_floor():
        body.velocity.y = jump_velocity
        
    body.move_and_slide()
```

### 生命值组件（生命）
**职责**：管理HP、钳制值、发出信号变化。
**上下文无关**：可以放在玩家、敌人或木箱上。

```gdscript
class_name HealthComponent extends Node

signal died
signal health_changed(current, max)

@export var max_health: float = 100.0
var current_health: float

func _ready():
    current_health = max_health

func damage(amount: float):
    current_health = clamp(current_health - amount, 0, max_health)
    health_changed.emit(current_health, max_health)
    if current_health == 0:
        died.emit()
```

---

## 编排器（整合一切）

编排器（`player.gd`）在`_physics_process`中绑定组件。它充当桥梁。

```gdscript
class_name Player extends CharacterBody3D

@onready var input: InputComponent = %InputComponent
@onready var move: MovementComponent = %MovementComponent
@onready var health: HealthComponent = %HealthComponent

func _ready():
    # 连接信号（耳朵）
    health.died.connect(_on_death)

func _physics_process(delta):
    # 1. 更新感官
    input.update()
    
    # 2. 将数据传递给工人（状态管理）
    # Player脚本决定“输入方向”映射到“移动方向”
    move.tick(delta, input.move_dir, input.jump_pressed)

func _on_death():
    queue_free()
```

## 性能说明
节点是轻量级的。不要害怕每个实体添加10-20个节点。组合的组织优势远远超过`Node`实例的微不足道的内存成本。


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
