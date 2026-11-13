---
名称: godot-characterbody-2d
描述: "CharacterBody2D的专家模式，包括平台移动（如coyote时间、跳跃缓冲、可变跳跃高度）、顶部移动（8方向、坦克控制）、碰撞处理、单向平台和状态机。适用于玩家角色、NPC或敌人。触发关键词：CharacterBody2D、move_and_slide、is_on_floor、coyote_time、jump_buffer、velocity、get_slide_collision、one_way_platforms、state_machine。"
---

# CharacterBody2D 实现

使用Godot物理系统进行玩家控制的2D移动的专家指导。

## 绝对不要做

- **永远不要在调用 `move_and_slide()` 时乘以 delta** — `move_and_slide()` 已考虑delta时间。乘会导致缓慢、帧依赖的移动。
- **永远不要在跳跃前忘记检查 `is_on_floor()`** — 允许空中跳跃而无双跳机制。
- **永远不要使用 `velocity.x = direction * SPEED` 而不加摩擦** — 在else分支中，角色会无限滑动而无摩擦。使用 `move_toward(velocity.x, 0, FRICTION * delta)`。
- **永远不要在坠落时将 `velocity.y` 设为精确值** — 覆盖重力累积。使用 `velocity.y += gravity * delta` 而不是 `velocity.y = gravity`。
- **永远不要使用 floor_snap_length > 16px** — 大的snap值导致"粘附"到斜坡和墙壁。
---

## 可用脚本

> **强制**: 在实现相应模式前阅读适当脚本。

### [expert_physics_2d.gd](scripts/expert_physics_2d.gd)
完整的平台移动，包括coyote时间、跳跃缓冲、平滑加速/摩擦和亚像素稳定。使用move_toward进行精确控制。

### [dash_controller.gd](scripts/dash_controller.gd)
帧完美冲刺，包括无敌帧、冷却和动量保持。

### [wall_jump_controller.gd](scripts/wall_jump_controller.gd)
墙壁滑动、粘附和方向性墙壁跳跃，带自动校正。

> **优先做**: 在添加冲刺/墙壁跳跃前，先阅读expert_physics_2d.gd作为平台基础。

---

## 何时使用 CharacterBody2D

**使用 CharacterBody2D 用于:**
- 玩家角色（平台、顶部、侧滚）
- 带有自定义移动逻辑的NPC
- 带有非物理基础移动的敌人

**使用 RigidBody2D 用于:**
- 物理驱动对象（滚石、车辆）
- 受力和冲量影响的对象

## 平台移动模式

### 基础平台控制器

```gdscript
extends CharacterBody2D

const SPEED := 300.0
const JUMP_VELOCITY := -400.0

# 从项目设置获取重力
var gravity: int = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta: float) -> void:
    # 应用重力
    if not is_on_floor():
        velocity.y += gravity * delta
    
    # 处理跳跃
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    # 获取输入方向
    var direction := Input.get_axis("move_left", "move_right")
    
    # 应用移动
    if direction:
        velocity.x = direction * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)
    
    move_and_slide()
```

### 高级平台移动（带Coyote时间与跳跃缓冲）

```gdscript
extends CharacterBody2D

const SPEED := 300.0
const JUMP_VELOCITY := -400.0
const ACCELERATION := 1500.0
const FRICTION := 1200.0
const AIR_RESISTANCE := 200.0

# Coyote时间: 离开平台后的宽限期
const COYOTE_TIME := 0.1
var coyote_timer := 0.0

# 跳跃缓冲: 在落地前稍早记住跳跃输入
const JUMP_BUFFER_TIME := 0.1
var jump_buffer_timer := 0.0

var gravity: int = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta: float) -> void:
    # 重力
    if not is_on_floor():
        velocity.y += gravity * delta
        coyote_timer -= delta
    else:
        coyote_timer = COYOTE_TIME
    
    # 跳跃缓冲
    if Input.is_action_just_pressed("jump"):
        jump_buffer_timer = JUMP_BUFFER_TIME
    else:
        jump_buffer_timer -= delta
    
    # 跳跃（带coyote时间和缓冲）
    if jump_buffer_timer > 0 and coyote_timer > 0:
        velocity.y = JUMP_VELOCITY
        jump_buffer_timer = 0
        coyote_timer = 0
    
    # 可变跳跃高度
    if Input.is_action_just_released("jump") and velocity.y < 0:
        velocity.y *= 0.5
    
    # 带加速/摩擦的移动
    var direction := Input.get_axis("move_left", "move_right")
    
    if direction:
        velocity.x = move_toward(velocity.x, direction * SPEED, ACCELERATION * delta)
    else:
        var friction_value := FRICTION if is_on_floor() else AIR_RESISTANCE
        velocity.x = move_toward(velocity.x, 0, friction_value * delta)
    
    move_and_slide()
```

## 顶部移动模式

### 8方向顶部移动

```gdscript
extends CharacterBody2D

const SPEED := 200.0
const ACCELERATION := 1500.0
const FRICTION := 1000.0

func _physics_process(delta: float) -> void:
    # 获取输入方向（为对角线移动归一化）
    var input_vector := Input.get_vector(
        "move_left", "move_right",
        "move_up", "move_down"
    )
    
    if input_vector != Vector2.ZERO:
        # 加速至目标速度
        velocity = velocity.move_toward(
            input_vector * SPEED,
            ACCELERATION * delta
        )
    else:
        # 应用摩擦
        velocity = velocity.move_toward(
            Vector2.ZERO,
            FRICTION * delta
        )
    
    move_and_slide()
```

### 带旋转的顶部移动（坦克控制）

```gdscript
extends CharacterBody2D

const SPEED := 200.0
const ROTATION_SPEED := 3.0

func _physics_process(delta: float) -> void:
    # 旋转
    var rotate_direction := Input.get_axis("rotate_left", "rotate_right")
    rotation += rotate_direction * ROTATION_SPEED * delta
    
    # 前后移动
    var move_direction := Input.get_axis("move_backward", "move_forward")
    velocity = transform.x * move_direction * SPEED
    
    move_and_slide()
```

## 碰撞处理

### 检测地板/墙壁/天花板

```gdscript
func _physics_process(delta: float) -> void:
    move_and_slide()
    
    if is_on_floor():
        print("站立在地面")
    
    if is_on_wall():
        print("接触墙壁")
    
    if is_on_ceiling():
        print("撞击天花板")
```

### 获取碰撞信息

```gdscript
func _physics_process(delta: float) -> void:
    move_and_slide()
    
    # 处理每个碰撞
    for i in get_slide_collision_count():
        var collision := get_slide_collision(i)
        print("与碰撞: ", collision.get_collider().name)
        print("碰撞法线: ", collision.get_normal())
        
        # 示例: 从墙壁弹开
        if collision.get_collider().is_in_group("bouncy"):
            velocity = velocity.bounce(collision.get_normal())
```

### 单向平台

```gdscript
extends CharacterBody2D

func _physics_process(delta: float) -> void:
    # 通过按下允许通过平台下落
    if Input.is_action_pressed("move_down") and is_on_floor():
        position.y += 1  # 轻微向下移动以通过
    
    velocity.y += gravity * delta
    move_and_slide()
```

## 移动状态与状态机

```gdscript
extends CharacterBody2D

enum State { IDLE, RUNNING, JUMPING, FALLING, DASHING }

var current_state := State.IDLE
var dash_velocity := Vector2.ZERO
const DASH_SPEED := 600.0
const DASH_DURATION := 0.2
var dash_timer := 0.0

func _physics_process(delta: float) -> void:
    match current_state:
        State.IDLE:
            _state_idle(delta)
        State.RUNNING:
            _state_running(delta)
        State.JUMPING:
            _state_jumping(delta)
        State.FALLING:
            _state_falling(delta)
        State.DASHING:
            _state_dashing(delta)

func _state_idle(delta: float) -> void:
    velocity.x = move_toward(velocity.x, 0, FRICTION * delta)
    
    if Input.is_action_pressed("move_left") or Input.is_action_pressed("move_right"):
        current_state = State.RUNNING
    elif Input.is_action_just_pressed("jump"):
        current_state = State.JUMPING
    
    move_and_slide()

func _state_dashing(delta: float) -> void:
    dash_timer -= delta
    velocity = dash_velocity
    
    if dash_timer <= 0:
        current_state = State.IDLE
    
    move_and_slide()
```

## 最佳实践

### 1. 使用常量进行调优

```gdscript
# ✅ 好 - 易于调整
const SPEED := 300.0
const JUMP_VELOCITY := -400.0

# ❌ 坏 - 魔术数字
velocity.x = 300
velocity.y = -400
```

### 2. 使用 `@export` 供设计师控制

```gdscript
@export var speed: float = 300.0
@export var jump_velocity: float = -400.0
@export_range(0, 2000) var acceleration: float = 1500.0
```

### 3. 分离移动与动画

```gdscript
func _physics_process(delta: float) -> void:
    _handle_movement(delta)
    _handle_animation()
    move_and_slide()

func _handle_movement(delta: float) -> void:
    # 仅移动逻辑
    pass

func _handle_animation() -> void:
    # 仅动画状态变化
    if velocity.x > 0:
        $AnimatedSprite2D.flip_h = false
    elif velocity.x < 0:
        $AnimatedSprite2D.flip_h = true
```

### 4. 使用地板检测参数

```gdscript
func _ready() -> void:
    # 设置地板参数
    floor_max_angle = deg_to_rad(45)  # 最大斜坡角度
    floor_snap_length = 8.0  # 吸附到地板的距离
    motion_mode = MOTION_MODE_GROUNDED  # 对比 MOTION_MODE_FLOATING
```

## 常见陷阱

**问题**: 角色在斜坡上滑动
```gdscript
# 解决方案: 增加摩擦
const FRICTION := 1200.0
```

**问题**: 角色在移动平台上卡顿
```gdscript
# 解决方案: 启用平台吸附
func _physics_process(delta: float) -> void:
    move_and_slide()
    
    # 吸附到平台速度
    if is_on_floor():
        var floor_velocity := get_platform_velocity()
        velocity += floor_velocity
```

**问题**: 双跳利用
```gdscript
# 解决方案: 跟踪是否使用跳跃
var can_jump := true

func _physics_process(delta: float) -> void:
    if is_on_floor():
        can_jump = true
    
    if Input.is_action_just_pressed("jump") and can_jump:
        velocity.y = JUMP_VELOCITY
        can_jump = false
```

## 参考
- [Godot 文档: CharacterBody2D](https://docs.godotengine.org/en/stable/classes/class_characterbody2d.html)
- [Godot 文档: 使用 CharacterBody2D](https://docs.godotengine.org/en/stable/tutorials/physics/using_character_body_2d.html)


### 相关
- 大师技能: [godot-master](../godot-master/SKILL.md)
