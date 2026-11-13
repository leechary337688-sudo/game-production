---
name: godot-3d-lighting
description: "Godot 3D灯光专家模式，包括DirectionalLight3D阴影级联、OmniLight3D衰减、SpotLight3D投影仪、VoxelGI与SDFGI比较，以及LightmapGI烘焙。用于实现逼真3D灯光、阴影优化、全局照明或光照探头。触发关键词：DirectionalLight3D、OmniLight3D、SpotLight3D、shadow_enabled、directional_shadow_mode、directional_shadow_split、omni_range、omni_attenuation、spot_range、spot_angle、VoxelGI、SDFGI、LightmapGI、ReflectionProbe、Environment、WorldEnvironment。"
---

# 3D灯光

关于逼真3D灯光、阴影和全局照明的专家指南。

## 绝不操作

- **绝不使用未设置适当范围的VoxelGI** — 未绑定的VoxelGI严重降低性能。始终将`size`设置为紧密贴合场景。
- **绝不在每个灯光上启用阴影** — 每个投射阴影的灯光都很昂贵。谨慎使用阴影：最多1-2个DirectionalLights，约3-5个OmniLights。
- **绝不忘记directional_shadow_mode** — 默认为ORTHOGONAL。对于大型户外场景，使用PARALLEL_4_SPLITS以获得远距离更好的阴影质量。
- **绝不将LightmapGI用于完全动态的场景** — Lightmaps是烘焙的。移动几何体不会接收更新的灯光。改用VoxelGI或SDFGI。
- **绝不将omni_range设置得太大** — 灯光衰减是二次的。范围500会影响785,000平方单位。尽可能保持范围小到视觉可接受。

---

## 可用脚本

> **强制要求**：在实现相应模式前阅读适当的脚本。

### [day_night_cycle.gd](scripts/day_night_cycle.gd)
基于时间的动态太阳位置和颜色。处理DirectionalLight3D旋转、色温和强度曲线。用于户外昼夜系统。

### [light_probe_manager.gd](scripts/light_probe_manager.gd)
全局照明设置的VoxelGI和SDFGI管理。

### [lighting_manager.gd](scripts/lighting_manager.gd)
动态灯光池和LOD。基于相机距离管理灯光剔除和阴影切换。用于多灯光的性能优化。

### [volumetric_fx.gd](scripts/volumetric_fx.gd)
体积雾和神光配置。运行时雾密度/颜色调整和光线束设置。用于大气效果。

---

## DirectionalLight3D（太阳/月亮）

### 阴影级联

```gdscript
# 用于相机从近到远移动的户外场景
extends DirectionalLight3D

func _ready() -> void:
    shadow_enabled = true
    directional_shadow_mode = SHADOW_PARALLEL_4_SPLITS
    
    # 分割距离（以米为单位，从相机算起）
    directional_shadow_split_1 = 10.0   # 第一级联：0-10米
    directional_shadow_split_2 = 50.0   # 第二级联：10-50米
    directional_shadow_split_3 = 200.0  # 第三级联：50-200米
    # 第四级联：200米 - 最大阴影距离
    
    directional_shadow_max_distance = 500.0
    
    # 质量与性能
    directional_shadow_blend_splits = true  # 平滑过渡
```

### 昼夜循环

```gdscript
# sun_controller.gd
extends DirectionalLight3D

@export var time_of_day := 12.0  # 0-24小时
@export var rotation_speed := 0.1  # 每秒小时数

func _process(delta: float) -> void:
    time_of_day += rotation_speed * delta
    if time_of_day >= 24.0:
        time_of_day -= 24.0
    
    # 旋转太阳（0° = 中午，180° = 午夜）
    var angle := (time_of_day - 12.0) * 15.0  # 每小时15°
    rotation_degrees.x = -angle
    
    # 调整强度
    if time_of_day < 6.0 or time_of_day > 18.0:
        light_energy = 0.0  # 夜晚
    elif time_of_day < 7.0:
        light_energy = remap(time_of_day, 6.0, 7.0, 0.0, 1.0)  # 日出
    elif time_of_day > 17.0:
        light_energy = remap(time_of_day, 17.0, 18.0, 1.0, 0.0)  # 日落
    else:
        light_energy = 1.0  # 白天
    
    # 颜色变化
    if time_of_day < 8.0 or time_of_day > 16.0:
        light_color = Color(1.0, 0.7, 0.4)  # 橙色（黎明/黄昏）
    else:
        light_color = Color(1.0, 1.0, 0.9)  # 中性白色
```

---

## OmniLight3D（点光源）

### 衰减调整

```gdscript
# torch.gd
extends OmniLight3D

func _ready() -> void:
    omni_range = 10.0  # 最大范围
    omni_attenuation = 2.0  # 衰减曲线（1.0 = 线性，2.0 = 二次/逼真）
    
    # 对于“魔法”灯光，减少衰减
    omni_attenuation = 0.5  # 更平的衰减，达到更远
```

### 闪烁效果

```gdscript
#  campfire.gd
extends OmniLight3D

@export var base_energy := 1.0
@export var flicker_strength := 0.3
@export var flicker_speed := 5.0

func _process(delta: float) -> void:
    var flicker := sin(Time.get_ticks_msec() * 0.001 * flicker_speed) * flicker_strength
    light_energy = base_energy + flicker
```

---

## SpotLight3D（手电筒/车头灯）

### 设置

```gdscript
# flashlight.gd
extends SpotLight3D

func _ready() -> void:
    spot_range = 20.0
    spot_angle = 45.0  # 锥角（度）
    spot_angle_attenuation = 2.0  # 边缘柔化
    
    shadow_enabled = true
    
    # 投影仪纹理（可选 - cookie/gobo）
    light_projector = load("res://textures/flashlight_mask.png")
```

### 跟随相机

```gdscript
# player_flashlight.gd
extends SpotLight3D

@onready var camera: Camera3D = get_viewport().get_camera_3d()

func _process(delta: float) -> void:
    if camera:
        global_transform = camera.global_transform
```

---

## 全局照明：VoxelGI vs SDFGI

### 决策矩阵

| 特性 | VoxelGI | SDFGI |
|---------|---------|-------|
| 设置 | 每个房间手动设置边界 | 自动，场景范围 |
| 动态对象 | 完全支持 | 部分支持 |
| 性能 | 中等 | 成本较高 |
| 使用场景 | 室内，中小场景 | 大型户外场景 |
| Godot版本 | 4.0+ | 4.0+ |

### VoxelGI设置

```gdscript
# room_gi.gd - 每个房间/区域放置一个VoxelGI
extends VoxelGI

func _ready() -> void:
    # 紧密贴合房间
    size = Vector3(20, 10, 20)
    
    # 质量设置
    subdiv = VoxelGI.SUBDIV_128  # 更高 = 更好质量，更慢
    
    # 烘焙GI数据
    bake()
```

### SDFGI设置

```gdscript
# world_environment.gd
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    
    # 启用SDFGI
    env.sdfgi_enabled = true
    env.sdfgi_use_occlusion = true
    env.sdfgi_read_sky_light = true
    
    # 级联（基于相机自动缩放）
    env.sdfgi_min_cell_size = 0.2  # 细节级别
    env.sdfgi_max_distance = 200.0
```

---

## LightmapGI（烘焙静态照明）

### 何时使用

- 静态建筑（建筑物、地牢）
- 移动/低端目标
- 无动态几何体

### 设置

```gdscript
# 场景结构：
# - LightmapGI节点
# - 具有GeometryInstance3D.gi_mode = STATIC的StaticBody3D网格

# lightmap_baker.gd
extends LightmapGI

func _ready() -> void:
    # 质量设置
    quality = LightmapGI.BAKE_QUALITY_HIGH
    bounces = 3  # 间接光反弹
    
    # 烘焙（仅编辑器，非运行时）
    # 在编辑器中点击“Bake Lightmaps”按钮
```

---

## 环境与天空

### HDR天空盒

```gdscript
# world_env.gd
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    
    env.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_material := PanoramaSkyMaterial.new()
    sky_material.panorama = load("res://hdri/sky.hdr")
    sky.sky_material = sky_material
    env.sky = sky
    
    # 天空对GI的贡献
    env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    env.ambient_light_sky_contribution = 1.0
```

### 体积雾

```gdscript
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    
    env.volumetric_fog_enabled = true
    env.volumetric_fog_density = 0.01
    env.volumetric_fog_albedo = Color(0.9, 0.9, 1.0)  # 偏蓝
    env.volumetric_fog_emission = Color.BLACK
```

---

## ReflectionProbe

用于局部反射（镜子、闪亮地板）：

```gdscript
# reflection_probe.gd
extends ReflectionProbe

func _ready() -> void:
    # 捕捉区域
    size = Vector3(10, 5, 10)
    
    # 质量
    resolution = ReflectionProbe.RESOLUTION_512
    
    # 更新模式
    update_mode = ReflectionProbe.UPDATE_ONCE  # 烘焙一次
    # 或UPDATE_ALWAYS用于动态反射（昂贵）
```

---

## 性能优化

### 灯光预算

```gdscript
# 推荐限制：
# - 带阴影的DirectionalLight3D：1-2个
# - 带阴影的OmniLight3D：3-5个
# - 带阴影的SpotLight3D：2-4个
# - 不带阴影的OmniLight3D：20-30个
# - 不带阴影的SpotLight3D：15-20个

# 在次要灯光上禁用阴影
@onready var candle_lights: Array = [$Candle1, $Candle2, $Candle3]

func _ready() -> void:
    for light in candle_lights:
        light.shadow_enabled = false  # 节省性能
```

### 每灯光阴影距离

```gdscript
# 对远距离灯光禁用阴影
extends OmniLight3D

@export var shadow_max_distance := 50.0

func _process(delta: float) -> void:
    var camera := get_viewport().get_camera_3d()
    if camera:
        var dist := global_position.distance_to(camera.global_position)
        shadow_enabled = (dist < shadow_max_distance)
```

---

## 边缘案例

### 阴影穿透地板

```gdscript
# 问题：薄地板让阴影穿透
# 解决方案：增加阴影偏移

extends DirectionalLight3D

func _ready() -> void:
    shadow_enabled = true
    shadow_bias = 0.1  # 如果阴影渗漏，增加
    shadow_normal_bias = 2.0
```

### 室内场景漏光

```gdscript
# 问题：VoxelGI光通过墙壁渗漏
# 解决方案：每个房间放置VoxelGI节点，不重叠

# 同时：确保墙壁有适当厚度（不是纸薄）
```


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
