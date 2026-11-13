---
名称: godot-adapt-3d-to-2d
描述: "简化3D游戏到2D的专家模式，包括维度减少策略、摄像机扁平化、物理转换、3D到精灵艺术管道和控制简化。适用于将3D移植到2D、为移动端创建2D版本或原型设计。触发关键词：CharacterBody3D到CharacterBody2D、Camera3D到Camera2D、Vector3到Vector2、扁平化Z轴、正交投影、3D到精灵转换、性能优化。"
---

# 适配：3D到2D

简化3D游戏为2D（或2.5D）的专家指导。

## 绝不这样做

- **绝不不加游戏玩法补偿就移除Z轴** — 盲目将3D扁平化为2D会移除空间策略。添加其他深度机制（如图层、跳跃高度变化）。
- **绝不保留3D碰撞形状** — 使用更简单的2D形状（如CapsuleShape2D、RectangleShape2D）。3D形状不会自动转换。
- **绝不使用正交Camera3D作为“2D模式”** — 使用实际的Camera2D以实现正确的2D渲染管道和性能。
- **绝不假设自动性能增益** — 优化不佳的2D（如过多绘制调用、大精灵表）可能比优化好的3D更慢。
- **绝不忘记调整重力** — 3D重力是Vector3(0, -9.8, 0)。2D重力是浮点数（980像素/秒²）。适当缩放。

---

## 可用脚本

> **必须**：在实现相应模式前阅读适当的脚本。

### [ortho_simulation.gd](scripts/ortho_simulation.gd)
在2D俯视游戏中模拟3D Z轴高度。处理垂直速度、重力、精灵偏移和阴影缩放。

### [projection_utils.gd](scripts/projection_utils.gd)
将3D世界位置投影到2D屏幕空间，用于名牌、血条和瞄准。处理背后摄像机检测和基于距离的缩放。

---

## 为何从3D转向2D？

| 原因 | 好处 |
|--------|---------|
| **移动性能** | 在低端设备上快5-10倍 |
| **更简单的艺术管道** | 精灵比3D模型更容易创建 |
| **更快迭代** | 2D关卡设计更快速 |
| **可访问性** | 降低硬件要求 |
| **清晰度** | 减少视觉杂乱，适合解谜/策略游戏 |

---

## 维度减少策略

### 策略1：真实2D（移除Z轴）

```gdscript
# 俯视或侧视图
# 示例：3D等距→2D俯视

# 之前（3D）：
var velocity := Vector3(input.x, 0, input.y) * speed

# 之后（2D）：
var velocity := Vector2(input.x, input.y) * speed

# 使用场景：俯视射击游戏、RTS、回合制策略游戏
```

### 策略2：2.5D（用图层模拟深度）

```gdscript
# 保持视觉深度感知，无Z轴游戏玩法
# 使用ParallaxBackground进行深度图层

# 场景结构：
# ParallaxBackground
#   ├─ ParallaxLayer（远山，滚动慢）
#   ├─ ParallaxLayer（中建筑，滚动中等）
#   └─ ParallaxLayer（近树，滚动快）

# player.gd
extends CharacterBody2D

func _ready() -> void:
    var parallax := get_node("../ParallaxBackground")
    parallax.scroll_base_scale = Vector2(0.5, 0.5)  # 视差强度
```

### 策略3：固定视角（保持等距）

```gdscript
# 保持等距/二度视图，但使用2D物理
# 使用旋转精灵模拟3D角度

const ISO_ANGLE := deg_to_rad(-30)  # 等距倾斜角

func world_to_iso(pos: Vector2) -> Vector2:
    return Vector2(
        pos.x - pos.y,
        (pos.x + pos.y) * 0.5
    )

func iso_to_world(iso_pos: Vector2) -> Vector2:
    return Vector2(
        (iso_pos.x + iso_pos.y * 2) * 0.5,
        (iso_pos.y * 2 - iso_pos.x) * 0.5
    )
```

---

## 节点转换

### 物理体

```gdscript
# CharacterBody3D → CharacterBody2D
extends CharacterBody3D  # 之前

const SPEED = 5.0
const JUMP_VELOCITY = 4.5
const GRAVITY = 9.8

func _physics_process(delta: float) -> void:
    velocity.y -= GRAVITY * delta
    var input := Input.get_vector("left", "right", "forward", "back")
    velocity.x = input.x * SPEED
    velocity.z = input.y * SPEED
    move_and_slide()

# ⬇️ 转换为：

extends CharacterBody2D  # 之后

const SPEED = 300.0
const JUMP_VELOCITY = -400.0
const GRAVITY = 980.0  # 像素每平方秒

func _physics_process(delta: float) -> void:
    velocity.y += GRAVITY * delta
    var input := Input.get_vector("left", "right", "up", "down")
    velocity.x = input.x * SPEED
    # 注意：无Z轴。对于平台游戏，使用input.y进行跳跃
    move_and_slide()
```

### 摄像机转换

```gdscript
# Camera3D → Camera2D
# 之前：第三人称3D摄像机
extends SpringArm3D

@onready var camera: Camera3D = $Camera3D

func _process(delta: float) -> void:
    spring_length = 10.0
    rotate_y(Input.get_axis("cam_left", "cam_right") * delta)

# ⬇️ 转换为：

extends Camera2D  # 之后

@onready var player: CharacterBody2D = $"../Player"

func _process(delta: float) -> void:
    global_position = player.global_position
    zoom = Vector2(2.0, 2.0)  # 根据需要调整
```

---

## 艺术管道：3D模型→精灵

### 选项1：从3D渲染精灵（自动化）

```gdscript
# 使用Godot从固定角度渲染3D模型
# sprite_renderer.gd（工具脚本）
@tool
extends Node3D

@export var model_path: String = "res://models/character.glb"
@export var output_dir: String = "res://sprites/"
@export var angles: int = 8  # 8方向精灵
@export var render: bool = false:
    set(value):
        if value:
            render_sprites()

func render_sprites() -> void:
    var model := load(model_path).instantiate()
    add_child(model)
    
    var camera := Camera3D.new()
    camera.position = Vector3(0, 2, 5)
    camera.look_at(Vector3.ZERO)
    add_child(camera)
    
    var viewport := SubViewport.new()
    viewport.size = Vector2i(256, 256)
    viewport.transparent_bg = true
    viewport.add_child(camera)
    add_child(viewport)
    
    for i in range(angles):
        model.rotation.y = (TAU / angles) * i
        
        await RenderingServer.frame_post_draw
        var img := viewport.get_texture().get_image()
        img.save_png("%s/sprite_%d.png" % [output_dir, i])
    
    model.queue_free()
    camera.queue_free()
    viewport.queue_free()
```

### 选项2：手动导出（Blender）

```python
# Blender Python脚本（在Blender中运行）
import bpy
import math

angles = 8
output_dir = "/path/to/sprites/"
model = bpy.data.objects["Character"]

for i in range(angles):
    model.rotation_euler.z = (2 * math.pi / angles) * i
    bpy.ops.render.render(write_still=True)
    bpy.data.images['Render Result'].save_render(
        filepath=f"{output_dir}/sprite_{i}.png"
    )
```

### 选项3：使用Sprite3D作为参考

```gdscript
# 在编辑器中保留3D模型，逐帧导出
```

---

## 物理调整

### 重力缩放

```gdscript
# 3D重力（米/秒²）：9.8
# 2D重力（像素/秒²）：缩放到像素单位

# 如果1米 = 100像素：
const GRAVITY_2D = 9.8 * 100  # = 980像素/秒²

# 按比例调整跳跃速度：
# 3D跳跃：4.5米/秒
# 2D跳跃：-450像素/秒
```

### 碰撞简化

```gdscript
# 3D: CapsuleShape3D（16段，昂贵）
var shape_3d := CapsuleShape3D.new()
shape_3d.radius = 0.5
shape_3d.height = 2.0

# 2D: CapsuleShape2D（简单得多）
var shape_2d := CapsuleShape2D.new()
shape_2d.radius = 16  # 像素
shape_2d.height = 64
```

---

## 控制简化

### 3D自由移动→2D受限移动

```gdscript
# 3D：完整的3D移动，带摄像机相对控制
var input_3d := Input.get_vector("left", "right", "forward", "back")
var camera_basis := camera.global_transform.basis
var direction := (camera_basis * Vector3(input_3d.x, 0, input_3d.y)).normalized()

# 2D：简单的4方向（或8方向带对角线）
var input_2d := Input.get_vector("left", "right", "up", "down")
velocity = input_2d.normalized() * SPEED
```

---

## 性能增益

### 预期改进

| 指标 | 3D | 2D | 改进 |
|--------|----|----|-------------|
| 绘制调用 | 100 | 20 | 5倍 |
| GPU负载 | 高 | 低 | 10倍 |
| 电池寿命（移动端） | 1小时 | 5小时 | 5倍 |
| RAM使用 | 500MB | 100MB | 5倍 |

### 优化技术

```gdscript
# 1. 使用TileMapLayer替代单个Sprite2D节点
var tilemap := TileMapLayer.new()
tilemap.tile_set = load("res://tileset.tres")

# 2. 批量精灵渲染
# 使用单个大精灵表替代独立纹理

# 3. 减少粒子数量
var godot-particles := GPUParticles2D.new()
godot-particles.amount = 50  # 从3D的200减少
```

---

## UI适配

```gdscript
# 大多数3D游戏已经使用2D UI（CanvasLayer）
# 无需更改！

# 只需验证新宽高比的UI缩放
get_viewport().size_changed.connect(_on_viewport_resized)

func _on_viewport_resized() -> void:
    var viewport_size := get_viewport().get_visible_rect().size
    # 调整UI锚点/边距
```

---

## 边缘案例

### 深度排序

```gdscript
# 问题：重叠精灵需要排序
# 解决方案：使用Y排序或z_index

extends Sprite2D

func _ready() -> void:
    y_sort_enabled = true  # 按Y位置自动排序
    # 或手动设置z_index：
    z_index = int(global_position.y)
```

### 丢失的空间音频

```gdscript
# 3D空间音频（AudioStreamPlayer3D）→2D平移（AudioStreamPlayer2D）

var audio_2d := AudioStreamPlayer2D.new()
audio_2d.stream = load("res://sounds/footstep.ogg")
audio_2d.max_distance = 1000.0  # 2D范围
audio_2d.attenuation = 2.0
add_child(audio_2d)
```

---

## 决策树：何时简化为2D

| 因素 | 保留3D | 转向2D |
|--------|---------|-------|
| **目标平台** | 桌面、游戏机 | 移动端、网页 |
| **艺术风格** | 写实、沉浸式 | 风格化、复古 |
| **游戏玩法** | 需要3D空间 | 在2D平面上有效 |
| **性能** | 有GPU预算 | 在低端设备上需要60 FPS |
| **团队技能** | 3D艺术家 | 2D艺术家或像素艺术 |


## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
