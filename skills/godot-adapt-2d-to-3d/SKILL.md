---
名字：godot-adapt-2d-to-3d
描述："专家模式，用于将2D游戏迁移到3D，包括节点类型转换、相机系统（第三人称、第一人称、轨道）、物理层迁移、精灵到模型的艺朮管线，以及控制方案适应。用于将2D项目移植到3D或添加3D元素时。触发关键词：CharacterBody2D to CharacterBody3D, Area2D to Area3D, Camera2D to Camera3D, Vector2 to Vector3, collision_layer migration, sprite to MeshInstance3D, 2D to 3D conversion。"
---

# 适配：2D 到 3D

将2D游戏迁移到第三维度的专家指导。

## 永远不要做

- **永远不要直接将Vector2替换为Vector3(x, y, 0)** — 这会产生一个没有深度游戏体验的"平坦3D"游戏。添加Z轴移动或相机旋转来证明3D的合理性。
- **永远不要保留2D碰撞层** — 2D和3D物理使用独立的层系统。您必须为3D节点重新配置collision_layer/collision_mask。
- **永远不要忘记添加光照** — 没有灯光的3D是漆黑一片（除非使用无光照材质）。至少添加一个DirectionalLight3D。
- **永远不要在3D中使用Camera2D的跟随逻辑** — Camera3D需要弹簧臂或look-at逻辑。直接位置复制会导致剪裁和迷失方向。
- **永远不要假设相同的性能** — 3D的要求高出5-10倍。为更低的绘制调用、移动设备上更小的视口分辨率做预算。

---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [sprite_plane.gd](scripts/sprite_plane.gd)
Sprite3D公告板配置和世界到屏幕投影，用于在3D对象上放置2D UI。处理相机后检测。

### [vector_mapping.gd](scripts/vector_mapping.gd)
静态工具，用于2D→3D向量翻译。Y到Z规则：2D Y（向下）映射到3D Z（向前）。对移动代码至关重要。

---

## 节点转换矩阵

| 2D 节点 | 3D 等效节点 | 说明 |
|---------|---------------|-------|
| CharacterBody2D | CharacterBody3D | 添加Z轴移动，用鼠标旋转 |
| RigidBody2D | RigidBody3D | 重力现在为Vector3(0, -9.8, 0) |
| StaticBody2D | StaticBody3D | 碰撞形状使用Shape3D |
| Area2D | Area3D | 触发器以相同方式工作 |
| Sprite2D | MeshInstance3D + QuadMesh | 或使用Sprite3D（公告板模式） |
| AnimatedSprite2D | AnimatedSprite3D | 公告板模式可用 |
| TileMapLayer | GridMap | 需要MeshLibrary创建 |
| Camera2D | Camera3D | 需要重新定位逻辑 |
| CollisionShape2D | CollisionShape3D | BoxShape2D → BoxShape3D 等 |
| RayCast2D | RayCast3D | target_position 现在为 Vector3 |

---

## 迁移步骤

### 步骤 1：物理层重新配置

```gdscript
# 2D碰撞层与3D是分开的
# 您必须在项目设置 → 层名称 → 3D物理中重新配置

# 之前（2D）：
# 层 1：玩家
# 层 2：敌人
# 层 3：世界

# 之后（3D）- 相同名称，但不同系统
# 在代码中，更新所有碰撞层引用：

# 2D版本：
# collision_layer = 0b0001

# 3D版本（相同逻辑，不同节点）：
var character_3d := CharacterBody3D.new()
character_3d.collision_layer = 0b0001  # 层 1：玩家
character_3d.collision_mask = 0b0110   # 检测敌人 + 世界
```

### 步骤 2：相机转换

```gdscript
# ❌ 错误：直接2D跟随逻辑
extends Camera3D

@onready var player: Node3D = $"../Player"

func _process(delta: float) -> void:
    global_position = player.global_position  # 剪裁，迷失方向！

# ✅ 好：带SpringArm3D的第三人称相机
# 场景结构：
# Player (CharacterBody3D)
#   └─ SpringArm3D
#       └─ Camera3D

# player.gd
extends CharacterBody3D

@onready var spring_arm: SpringArm3D = $SpringArm3D
@onready var camera: Camera3D = $SpringArm3D/Camera3D

func _ready() -> void:
    spring_arm.spring_length = 10.0  # 与玩家的距离
    spring_arm.position = Vector3(0, 2, 0)  # 在玩家上方

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        spring_arm.rotate_y(-event.relative.x * 0.005)  # 水平旋转
        spring_arm.rotate_object_local(Vector3.RIGHT, -event.relative.y * 0.005)  # 垂直
        
        # 限制垂直旋转
        spring_arm.rotation.x = clamp(spring_arm.rotation.x, -PI/3, PI/6)
```

### 步骤 3：移动转换

```gdscript
# 2D平台移动
extends CharacterBody2D

const SPEED = 300.0
const JUMP_VELOCITY = -400.0

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    var direction := Input.get_axis("left", "right")
    velocity.x = direction * SPEED
    
    move_and_slide()

# ✅ 3D等效（第三人称平台）
extends CharacterBody3D

const SPEED = 5.0
const JUMP_VELOCITY = 4.5
const GRAVITY = 9.8

@onready var spring_arm: SpringArm3D = $SpringArm3D

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y -= GRAVITY * delta
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    # 相对于相机方向的移动
    var input_dir := Input.get_vector("left", "right", "forward", "back")
    var camera_basis := spring_arm.global_transform.basis
    var direction := (camera_basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    
    if direction:
        velocity.x = direction.x * SPEED
        velocity.z = direction.z * SPEED
        
        # 旋转玩家以面向移动方向
        rotation.y = lerp_angle(rotation.y, atan2(-direction.x, -direction.z), 0.1)
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)
        velocity.z = move_toward(velocity.z, 0, SPEED)
    
    move_and_slide()
```

---

## 艺术管线：精灵 → 3D模型

### 选项 1：公告板精灵（2.5D）

```gdscript
# 使用Sprite3D进行快速转换
extends Sprite3D

func _ready() -> void:
    texture = load("res://sprites/character.png")
    billboard = BaseMaterial3D.BILLBOARD_ENABLED  # 总是面向相机
    pixel_size = 0.01  # 在3D空间中缩放精灵
```

### 选项 2：四边形网格（浮动精灵）

```gdscript
# 创建纹理化的四边形
var mesh_instance := MeshInstance3D.new()
var quad := QuadMesh.new()
quad.size = Vector2(1, 1)
mesh_instance.mesh = quad

var material := StandardMaterial3D.new()
material.albedo_texture = load("res://sprites/character.png")
material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
material.cull_mode = BaseMaterial3D.CULL_DISABLED  # 显示两面
mesh_instance.material_override = material
```

### 选项 3：完整的3D模型（Blender/资产库）

```gdscript
# 导入.glb, .fbx模型
var character := load("res://models/character.glb").instantiate()
add_child(character)

# 访问动画
var anim_player := character.get_node("AnimationPlayer")
anim_player.play("idle")
```

---

## 光照考虑

### 最小光照设置

```gdscript
# 添加到主场景
var sun := DirectionalLight3D.new()
sun.rotation_degrees = Vector3(-45, 30, 0)
sun.light_energy = 1.0
sun.shadow_enabled = true
add_child(sun)

# 环境光
var env := WorldEnvironment.new()
var environment := Environment.new()
environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
environment.ambient_light_color = Color(0.3, 0.3, 0.4)  # 微妙的蓝色
environment.ambient_light_energy = 0.5
env.environment = environment
add_child(env)
```

---

## UI适配

```gdscript
# ✅ 好：保持2D UI覆盖层
# 场景结构：
# Main (Node3D)
#   ├─ WorldEnvironment
#   ├─ DirectionalLight3D
#   ├─ Player (CharacterBody3D)
#   └─ CanvasLayer  # 3D世界上的2D UI
#       └─ Control (HUD)

# UI保持2D（Control节点，Sprite2D用于HUD元素）
```

---

## 性能预算

### 2D 与 3D 性能

| 指标 | 2D 预算 | 3D 预算 | 说明 |
|--------|-----------|-----------|-------|
| 绘制调用 | 100-200 | 50-100 | 使用更少的网格 |
| 顶点 | 无限 | 100K-500K | LOD 重要 |
| 灯光 | N/A | 3-5 有阴影 | 昂贵 |
| 透明对象 | 许多 | <10 | 排序开销 |
| 粒子系统 | 许多 | 2-3 最大 | 仅GPU godot-particles |

### 优化清单

```gdscript
# 1. 对远处对象使用LOD
var mesh_instance := MeshInstance3D.new()
mesh_instance.lod_bias = 1.0  # 更早降低细节

# 2. 遮挡剔除
# 使用OccluderInstance3D用于大墙/建筑物

# 3. 减少阴影距离
var sun := DirectionalLight3D.new()
sun.directional_shadow_max_distance = 50.0  # 不渲染远处阴影

# 4. 对远处对象使用无光照材质
var material := StandardMaterial3D.new()
material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
```

---

## 输入方案更改

### 2D → 3D 输入映射

```gdscript
# 2D：left/right用于水平移动
Input.get_axis("left", "right")

# 3D：添加forward/back，使用get_vector()
var input := Input.get_vector("left", "right", "forward", "back")
# 返回Vector2(horizontal, vertical)用于3D移动

# 在项目设置 → 输入映射中配置：
# forward: W, 上箭头
# back: S, 下箭头
# left: A, 左箭头
# right: D, 右箭头

# 鼠标查看（锁定光标）
func _ready() -> void:
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        rotate_camera(event.relative)
```

---

## 边缘情况

### 物理不工作

```gdscript
# 问题：忘记了为3D设置碰撞层
# 解决方案：重新配置层

var body := CharacterBody3D.new()
body.collision_layer = 0b0001  # 我是什么？
body.collision_mask = 0b0110   # 我检测什么？
```

### 相机剪裁穿过墙壁

```gdscript
# SpringArm3D在受阻时自动拉近相机
spring_arm.spring_length = 10.0
spring_arm.collision_mask = 0b0100  # 层 3：世界
```

### 玩家掉落地板

```gdscript
# 问题：StaticBody3D地板没有CollisionShape3D
# 解决方案：添加碰撞

var floor_collision := CollisionShape3D.new()
var box_shape := BoxShape3D.new()
box_shape.size = Vector3(100, 1, 100)
floor_collision.shape = box_shape
floor.add_child(floor_collision)
```

---

## 决策树：何时转为3D

| 因素 | 保持2D | 转为3D |
|--------|---------|-------|
| **游戏玩法** | 平台、俯视图，不需要深度 | 探索、第一人称、3D空间战斗 |
| **艺术预算** | 像素艺术，资源有限 | 3D模型可用或必要 |
| **性能目标** | 移动、网页、低端设备 | 桌面、游戏机、高端移动设备 |
| **开发时间** | 有限 | 有时间为3D学习曲线 |
| **团队技能** | 只有2D艺术家 | 3D艺术家或资产库 |


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
