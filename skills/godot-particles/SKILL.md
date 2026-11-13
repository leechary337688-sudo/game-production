---
name: godot-particles
description: "GPU粒子系统的专家蓝图（爆炸、魔法效果、天气、轨迹）使用GPUParticles2D/3D、ParticleProcessMaterial、渐变、子发射器和自定义着色器。在创建VFX、环境效果或视觉反馈时使用。关键词GPUParticles2D、ParticleProcessMaterial、emission_shape、color_ramp、sub_emitter、one_shot。"
---

# 粒子系统

GPU加速渲染、基于材质的配置和子发射器定义了高性能的VFX。

## 可用脚本

### [vfx_shader_manager.gd](scripts/vfx_shader_manager.gd)
高级粒子VFX的专家自定义着色器集成。

### [particle_burst_emitter.gd](scripts/particle_burst_emitter.gd)
一次性粒子爆发与自动清理 - VFX系统的基础。

## 粒子系统中绝对不要做的事

- **绝对不要对性能关键的效果使用CPUParticles2D** — 100+个godot-particles使用CPU = 延迟峰值。除非目标平台是移动设备且没有GPU支持，否则使用GPUParticles2D。
- **绝对不要忘记为一击godot-particles设置`emitting = false`** — 默认`emitting = true`的爆炸场景 = godot-particles在instantiate()时立即发射，在定位之前。设置为false，定位，然后发射。
- **绝对不要在没有在目标平台上测试的情况下使用高`amount`** — 1000个godot-particles在桌面上正常，在移动设备上卡顿。早期测试，基于`OS.get_name()`缩放`amount`。
- **绝对不要忘记`queue_free()`一击godot-particles** — 爆炸持续1秒但节点永远留在树中 = 内存泄漏。`await create_timer(lifetime).timeout`然后`queue_free()`。
- **绝对不要对爆炸使用`emission_shape = POINT`** — 所有godot-particles在同一位置生成 = 看起来扁平。使用`EMISSION_SHAPE_SPHERE`带半径以获得3D扩散。
- **绝对不要忘记颜色渐变中的alpha** — 粒子在结束时突然消失 = 生硬。在1.0处添加渐变点，使用`Color(r, g, b, 0.0)`以实现平滑淡出。

### 基本设置

```gdscript
# 添加GPUParticles2D节点
# 设置数量: 32
# 设置生命周期: 1.0
# 设置一击: true（用于爆炸）
```

### 粒子材质

```gdscript
# 创建ParticleProcessMaterial
var material := ParticleProcessMaterial.new()

# 发射形状
material.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
material.emission_sphere_radius = 10.0

# 重力
material.gravity = Vector3(0, 98, 0)

# 速度
material.initial_velocity_min = 50.0
material.initial_velocity_max = 100.0

# 颜色
material.color = Color.ORANGE_RED

# 应用到godot-particles
$GPUParticles2D.process_material = material
```

## 常见效果

### 爆炸

```gdscript
extends GPUParticles2D

func _ready() -> void:
    one_shot = true
    amount = 64
    lifetime = 0.8
    explosiveness = 0.9
    
    var mat := ParticleProcessMaterial.new()
    mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
    mat.emission_sphere_radius = 5.0
    mat.initial_velocity_min = 100.0
    mat.initial_velocity_max = 200.0
    mat.gravity = Vector3(0, 200, 0)
    mat.scale_min = 0.5
    mat.scale_max = 1.5
    
    process_material = mat
    emitting = true
```

### 烟雾轨迹

```gdscript
extends GPUParticles2D

func _ready() -> void:
    amount = 16
    lifetime = 2.0
    
    var mat := ParticleProcessMaterial.new()
    mat.direction = Vector3(0, -1, 0)
    mat.initial_velocity_min = 20.0
    mat.initial_velocity_max = 40.0
    mat.scale_min = 0.5
    mat.scale_max = 1.0
    mat.color = Color(0.5, 0.5, 0.5, 0.5)
    
    process_material = mat
```

### 火花/星星

```gdscript
var mat := ParticleProcessMaterial.new()
mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
mat.emission_box_extents = Vector3(100, 100, 0)
mat.gravity = Vector3.ZERO
mat.angular_velocity_min = -180
mat.angular_velocity_max = 180
mat.scale_min = 0.1
mat.scale_max = 0.5

# 使用星星纹理
$GPUParticles2D.texture = load("res://textures/star.png")
$GPUParticles2D.process_material = mat
```

## 按需生成粒子

```gdscript
# player.gd
const EXPLOSION_EFFECT := preload("res://effects/explosion.tscn")

func die() -> void:
    var explosion := EXPLOSION_EFFECT.instantiate()
    get_parent().add_child(explosion)
    explosion.global_position = global_position
    explosion.emitting = true
    queue_free()
```

## 3D粒子

```gdscript
extends GPUParticles3D

func _ready() -> void:
    amount = 100
    lifetime = 3.0
    
    var mat := ParticleProcessMaterial.new()
    mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
    mat.emission_box_extents = Vector3(10, 0.1, 10)
    mat.direction = Vector3.UP
    mat.initial_velocity_min = 2.0
    mat.initial_velocity_max = 5.0
    mat.gravity = Vector3(0, -9.8, 0)
    
    process_material = mat
```

## 颜色渐变

```gdscript
var mat := ParticleProcessMaterial.new()

# 创建渐变
var gradient := Gradient.new()
gradient.add_point(0.0, Color.YELLOW)
gradient.add_point(0.5, Color.ORANGE)
gradient.add_point(1.0, Color(0.5, 0.0, 0.0, 0.0))  # 淡出到透明红色

var gradient_texture := GradientTexture1D.new()
gradient_texture.gradient = gradient

mat.color_ramp = gradient_texture
```

## 子发射器

```gdscript
# 生成godot-particles的粒子（烟花）
$ParentParticles.sub_emitter = $ChildParticles.get_path()
$ParentParticles.sub_emitter_mode = GPUParticles2D.SUB_EMITTER_AT_END
```

## 最佳实践

### 1. 使用纹理作为形状

```gdscript
# 添加纹理到godot-particles
$GPUParticles2D.texture = load("res://textures/particle.png")
```

### 2. 生命周期管理

```gdscript
# 自动删除一击godot-particles
if one_shot:
    await get_tree().create_timer(lifetime).timeout
    queue_free()
```

### 3. 性能

```gdscript
# 为移动设备减少数量
if OS.get_name() == "Android":
    amount = amount / 2
```

## 参考
- [Godot 文档: 粒子系统](https://docs.godotengine.org/en/stable/tutorials/2d/particle_systems_2d.html)


### 相关
- 主要技能: [godot-master](../godot-master/SKILL.md)
