---
名称: godot-navigation-pathfinding
描述: "AI路径查找的专家蓝图（用于塔防、RTS、潜行游戏），使用NavigationAgent2D/3D、NavigationServer、避障和动态导航网格生成。在实现敌人AI、NPC移动或障碍物避障时使用。关键词：NavigationAgent2D、NavigationRegion2D、路径查找、NavigationServer、避障、烘焙、NavigationObstacle。"
---

# 导航与路径查找

由NavigationServer驱动的路径查找，包含避障和动态障碍物，定义稳健的AI移动。

## 可用脚本

### [dynamic_nav_manager.gd](scripts/dynamic_nav_manager.gd)
专家级运行时导航网格更新，用于移动平台。

## 导航与路径查找中切勿做的事

- **切勿在等待物理帧之前设置`target_position`** — NavigationServer在`_ready()`中未就绪？路径会静默失败。必须使用`call_deferred()`然后`await get_tree().physics_frame`。
- **切勿在运行时使用`NavigationRegion2D.bake_navigation_polygon()`** — 同步烘焙会使游戏冻结100+毫秒。使用`NavigationServer2D`进行动态更新或预烘焙。
- **切勿忘记检查`is_navigation_finished()`** — 到达目标后调用`get_next_path_position()` = 陈旧路径，AI会走向旧位置。
- **切勿启用`avoidance_enabled`而不设置半径** — 默认半径 = 0，代理会穿过其他对象。设置`nav_agent.radius = collision_shape.radius`以正确避障。
- **切勿每帧轮询`target_position`用于追逐AI** — 每秒设置目标60次 = 路径重新计算泛滥。使用计时器（0.2秒间隔）或距离阈值进行更新。
- **切勿假设路径存在** — 目标不可达（被墙阻挡）？`get_next_path_position()`返回无效。检查`is_target_reachable()`或验证路径长度。

---

### 2D导航

```gdscript
# 场景结构：
# Node2D (关卡)
#   ├─ NavigationRegion2D
#   │    └─ Polygon2D (绘制可行走区域)
#   └─ CharacterBody2D (敌人)
#        └─ NavigationAgent2D
```

**设置NavigationRegion2D：**
1. 添加`NavigationRegion2D`节点
2. 创建**新NavigationPolygon**
3. 点击"编辑" → 绘制可行走区域
4. 烘焙导航网格

### 基础AI移动

```gdscript
extends CharacterBody2D

@onready var nav_agent := $NavigationAgent2D
@export var speed := 200.0

var target_position: Vector2

func _ready() -> void:
    # 等待导航就绪
    call_deferred("setup_navigation")

func setup_navigation() -> void:
    await get_tree().physics_frame
    nav_agent.target_position = target_position

func _physics_process(delta: float) -> void:
    if nav_agent.is_navigation_finished():
        return
    
    var next_position := nav_agent.get_next_path_position()
    var direction := (next_position - global_position).normalized()
    
    velocity = direction * speed
    move_and_slide()

func set_target(pos: Vector2) -> void:
    target_position = pos
    nav_agent.target_position = pos
```

## NavigationAgent属性

```gdscript
# 路径重新计算
nav_agent.path_desired_distance = 10.0
nav_agent.target_desired_distance = 10.0

# 避障
nav_agent.radius = 20.0
nav_agent.avoidance_enabled = true

# 性能
nav_agent.path_max_distance = 500.0
```

## 高级模式

### 追逐玩家

```gdscript
extends CharacterBody2D

@onready var nav_agent := $NavigationAgent2D
@export var speed := 150.0
@export var chase_range := 300.0

var player: Node2D

func _physics_process(delta: float) -> void:
    if not player:
        return
    
    var distance := global_position.distance_to(player.global_position)
    
    if distance <= chase_range:
        nav_agent.target_position = player.global_position
        
        if not nav_agent.is_navigation_finished():
            var next_pos := nav_agent.get_next_path_position()
            var direction := (next_pos - global_position).normalized()
            velocity = direction * speed
            move_and_slide()
```

### 巡逻点

```gdscript
extends CharacterBody2D

@onready var nav_agent := $NavigationAgent2D
@export var patrol_points: Array[Vector2] = []
@export var speed := 100.0

var current_point_index := 0

func _ready() -> void:
    if patrol_points.size() > 0:
        nav_agent.target_position = patrol_points[0]

func _physics_process(delta: float) -> void:
    if nav_agent.is_navigation_finished():
        _go_to_next_patrol_point()
        return
    
    var next_pos := nav_agent.get_next_path_position()
    var direction := (next_pos - global_position).normalized()
    velocity = direction * speed
    move_and_slide()

func _go_to_next_patrol_point() -> void:
    current_point_index = (current_point_index + 1) % patrol_points.size()
    nav_agent.target_position = patrol_points[current_point_index]
```

## 3D导航

```gdscript
extends CharacterBody3D

@onready var nav_agent := $NavigationAgent3D
@export var speed := 5.0

func _physics_process(delta: float) -> void:
    if nav_agent.is_navigation_finished():
        return
    
    var next_position := nav_agent.get_next_path_position()
    var direction := (next_position - global_position).normalized()
    
    velocity = direction * speed
    move_and_slide()
```

## 动态障碍物

```gdscript
# 向移动对象添加NavigationObstacle2D
# 场景：
# CharacterBody2D (移动平台)
#   └─ NavigationObstacle2D

# 导航会自动在其周围更新
```

## 信号

```gdscript
func _ready() -> void:
    nav_agent.velocity_computed.connect(_on_velocity_computed)
    nav_agent.navigation_finished.connect(_on_navigation_finished)

func _on_velocity_computed(safe_velocity: Vector2) -> void:
    velocity = safe_velocity
    move_and_slide()

func _on_navigation_finished() -> void:
    print("到达目的地")
```

## 最佳实践

### 1. 延迟导航设置

```gdscript
# ✅ 好 - 等待导航初始化
func _ready() -> void:
    call_deferred("setup_nav")

func setup_nav() -> void:
    await get_tree().physics_frame
    nav_agent.target_position = target
```

### 2. 检查路径是否存在

```gdscript
if not nav_agent.is_target_reachable():
    print("目标不可达！")
```

### 3. 使用避障处理人群

```gdscript
nav_agent.avoidance_enabled = true
nav_agent.radius = 20.0
nav_agent.max_neighbors = 10
```

## 参考
- [Godot文档：导航](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_introduction_2d.html)


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
