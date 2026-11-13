---
名称: godot-3d-materials
描述: "Godot 3D PBR材质的专家模式，使用StandardMaterial3D包括漫反射、金属/粗糙度工作流、法线贴图、ORM纹理打包、透明度模式和着色器转换。用于创建逼真的3D表面、PBR工作流或材质优化。触发关键词: StandardMaterial3D, BaseMaterial3D, albedo_texture, metallic, metallic_texture, roughness, roughness_texture, normal_texture, normal_enabled, orm_texture, transparency, alpha_scissor, alpha_hash, cull_mode, ShaderMaterial, shader参数。"
---

# 3D材质

Godot中PBR材质和StandardMaterial3D的专家指导。

## 绝不这样做

- **绝不使用单独的金属/粗糙度/AO纹理** — 使用ORM打包（一个RGB纹理包含遮蔽/粗糙度/金属通道）以节省纹理槽和内存。
- **绝不忘记启用normal_enabled** — 除非设置`normal_enabled = true`，否则法线贴图不起作用。静默失败很常见。
- **绝不使用TRANSPARENCY_ALPHA用于剪切材质** — 使用TRANSPARENCY_ALPHA_SCISSOR或TRANSPARENCY_ALPHA_HASH代替。完整的alpha混合昂贵并导致排序问题。
- **绝不设置metallic = 0.5** — 材质要么是金属（1.0），要么是非金属（0.0）。中间值物理上不正确，除了锈迹/污垢过渡。
- **绝不使用没有HDR的发射** — 发射值大于1.0仅在项目设置中启用HDR渲染时有效。

---

## 可用脚本

> **必须**：在实现相应模式前阅读适当脚本。

### [material_fx.gd](scripts/material_fx.gd)
运行时材质属性动画，用于损伤效果、溶解和纹理交换。用于动态材质状态变化。

### [pbr_material_builder.gd](scripts/pbr_material_builder.gd)
使用ORM纹理和三平面映射的运行时PBR材质创建。

### [organic_material.gd](scripts/organic_material.gd)
次表面散射和边缘光照设置，用于有机表面（皮肤、叶子）。用于逼真角色或植被材质。

### [triplanar_world.gdshader](scripts/triplanar_world.gdshader)
三平面投影着色器，用于无UV映射的地形。基于表面法线混合纹理。用于悬崖、洞穴或程序化地形。

---

## StandardMaterial3D基础

### PBR纹理设置

```gdscript
# 创建基于物理的材质
var mat := StandardMaterial3D.new()

# 漫反射（基础颜色）
mat.albedo_texture = load("res://textures/wood_albedo.png")
mat.albedo_color = Color.WHITE  # 色调乘数

# 法线贴图（表面细节）
mat.normal_enabled = true  # 关键：必须先启用
mat.normal_texture = load("res://textures/wood_normal.png")
mat.normal_scale = 1.0  # 凹凸强度

# ORM纹理（R=遮蔽，G=粗糙度，B=金属）
mat.orm_texture = load("res://textures/wood_orm.png")

# 替代方案：单独纹理（效率较低）
# mat.roughness_texture = load("res://textures/wood_roughness.png")
# mat.metallic_texture = load("res://textures/wood_metallic.png")
# mat.ao_texture = load("res://textures/wood_ao.png")

# 应用到网格
$MeshInstance3D.material_override = mat
```

---

## 金属 vs 粗糙度

### 金属工作流

```gdscript
# 纯金属（钢、金、铜）
mat.metallic = 1.0
mat.roughness = 0.2  # 抛光金属
mat.albedo_color = Color(0.8, 0.8, 0.8)  # 金属色调

# 粗糙金属（铁、铝）
mat.metallic = 1.0
mat.roughness = 0.7
```

### 非金属工作流

```gdscript
# 非金属（木、塑料、石）
mat.metallic = 0.0
mat.roughness = 0.6  # 木材典型值
mat.albedo_color = Color(0.6, 0.4, 0.2)  # 棕色木材

# 光泽塑料
mat.metallic = 0.0
mat.roughness = 0.1  # 非常光滑
```

### 过渡材质（锈迹/污垢）

```gdscript
# 使用纹理混合金属/非金属
mat.metallic_texture = load("res://rust_mask.png")
# 白色区域（1.0）= 金属
# 黑色区域（0.0）= 锈迹（非金属）
```

---

## 透明度模式

### 决策矩阵

| 模式 | 使用场景 | 性能 | 排序问题 |
|------|----------|-------------|---------------|
| ALPHA_SCISSOR | 树叶、链围栏 | 快 | 无 |
| ALPHA_HASH | 抖动淡出、LOD过渡 | 快 | 有噪点 |
| ALPHA | 玻璃、水、粒子 | 慢 | 有（渲染顺序） |

### Alpha剪切（剪裁）

```gdscript
# 用于树叶、草、围栏
mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
mat.alpha_scissor_threshold = 0.5  # 透明度小于0.5的像素被丢弃
mat.albedo_texture = load("res://leaf.png")  # 必须有alpha通道

# 启用背面剔除以提高性能
mat.cull_mode = BaseMaterial3D.CULL_BACK
```

### Alpha哈希（抖动）

```gdscript
# 用于平滑淡出，无排序问题
mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_HASH
mat.alpha_hash_scale = 1.0  # 抖动图案缩放

# 动画淡出
var tween := create_tween()
tween.tween_property(mat, "albedo_color:a", 0.0, 1.0)
```

### Alpha混合（全透明）

```gdscript
# 用于玻璃、水（昂贵）
mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
mat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX

# 禁用深度写入以正确混合
mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
mat.cull_mode = BaseMaterial3D.CULL_DISABLED  # 显示两面
```

---

## 高级功能

### 发射（发光材质）

```gdscript
mat.emission_enabled = true
mat.emission = Color(1.0, 0.5, 0.0)  # 橙色发光
mat.emission_energy_multiplier = 2.0  # 亮度（HDR）
mat.emission_texture = load("res://lava_emission.png")

# 动画发射
func _process(delta: float) -> void:
    mat.emission_energy_multiplier = 1.0 + sin(Time.get_ticks_msec() * 0.005) * 0.5
```

### 边缘光照（菲涅尔）

```gdscript
mat.rim_enabled = true
mat.rim = 1.0  # 强度
mat.rim_tint = 0.5  # 漫反射如何影响边缘颜色
```

### 清漆（车漆）

```gdscript
mat.clearcoat_enabled = true
mat.clearcoat = 1.0  # 层强度
mat.clearcoat_roughness = 0.1  # 光泽顶层
```

### 各向异性（拉丝金属）

```gdscript
mat.anisotropy_enabled = true
mat.anisotropy = 1.0  # 方向性高光
mat.anisotropy_flowmap = load("res://brushed_flow.png")
```

---

## 纹理通道打包

### ORM纹理（推荐）

```python
# 外部工具（GIMP、Substance、Python脚本）：
# 将3个灰度纹理合并为1个RGB：
# R通道 = 环境遮蔽（亮 = 无遮蔽）
# G通道 = 粗糙度（亮 = 粗糙）
# B通道 = 金属（亮 = 金属）
```

```gdscript
# 在Godot中：
mat.orm_texture = load("res://textures/material_orm.png")
# 这替代了ao_texture、roughness_texture和metallic_texture！
```

### 自定义打包

```gdscript
# 如果使用自定义通道分配：
mat.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
mat.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
```

---

## 着色器转换

### 何时转换为ShaderMaterial

- 需要自定义效果（溶解、顶点位移）
- 达到StandardMaterial3D限制
- 着色器优化（移除未使用功能）

### 转换工作流

```gdscript
# 1. 创建StandardMaterial3D并设置所有参数
var std_mat := StandardMaterial3D.new()
std_mat.albedo_color = Color.RED
std_mat.metallic = 1.0
std_mat.roughness = 0.2

# 2. 转换为ShaderMaterial
var shader_mat := ShaderMaterial.new()
shader_mat.shader = load("res://custom_shader.gdshader")

# 3. 手动传输参数
shader_mat.set_shader_parameter("albedo", std_mat.albedo_color)
shader_mat.set_shader_parameter("metallic", std_mat.metallic)
shader_mat.set_shader_parameter("roughness", std_mat.roughness)
```

---

## 材质变体（Godot 4.0+）

### 高效材质复用

```gdscript
# 基础材质（共享）
var base_red_metal := StandardMaterial3D.new()
base_red_metal.albedo_color = Color.RED
base_red_metal.metallic = 1.0

# 变体1：粗糙
var rough_variant := base_red_metal.duplicate()
rough_variant.roughness = 0.8

# 变体2：平滑
var smooth_variant := base_red_metal.duplicate()
smooth_variant.roughness = 0.1

# 注意：使用resource_local_to_scene进行实例特定调整
```

---

## 性能优化

### 材质批处理

```gdscript
# ✅ 好：在网格间复用材质
const SHARED_STONE := preload("res://materials/stone.tres")

func _ready() -> void:
    for wall in get_tree().get_nodes_in_group("stone_walls"):
        wall.material_override = SHARED_STONE
    # 所有墙壁在单个绘制调用中批处理

# ❌ 坏：每个网格唯一材质
func _ready() -> void:
    for wall in get_tree().get_nodes_in_group("stone_walls"):
        var mat := StandardMaterial3D.new()  # 新材质！
        mat.albedo_color = Color(0.5, 0.5, 0.5)
        wall.material_override = mat
    # 每个墙壁是单独的绘制调用
```

### 纹理图集

```gdscript
# 将多个材质合并为一个纹理图集
# 然后使用UV偏移选择区域

# material_atlas.gd
extends StandardMaterial3D

func set_atlas_region(tile_x: int, tile_y: int, tiles_per_row: int) -> void:
    var tile_size := 1.0 / tiles_per_row
    uv1_offset = Vector3(tile_x * tile_size, tile_y * tile_size, 0)
    uv1_scale = Vector3(tile_size, tile_size, 1)
```

---

## 边缘案例

### 法线贴图不起作用

```gdscript
# 问题：忘记启用
mat.normal_enabled = true  # 必需

# 问题：错误的纹理导入设置
# 在导入标签：纹理 → 法线贴图 = true
```

### 模型上的纹理接缝

```gdscript
# 问题：Mipmaps导致接缝
# 解决方案：对于紧密打包的UV，禁用Mipmaps
# 导入 → Mipmaps → 生成 = false
```

### 材质看起来平坦

```gdscript
# 问题：缺少法线贴图或粗糙度变化
# 解决方案：添加法线贴图 + 粗糙度纹理

mat.normal_enabled = true
mat.normal_texture = load("res://normal.png")
mat.roughness_texture = load("res://roughness.png")
```

---

## 常见材质预设

```gdscript
# 玻璃
func create_glass() -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.albedo_color = Color(1, 1, 1, 0.2)
    mat.metallic = 0.0
    mat.roughness = 0.0
    mat.refraction_enabled = true
    mat.refraction_scale = 0.05
    return mat

# 黄金
func create_gold() -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(1.0, 0.85, 0.3)
    mat.metallic = 1.0
    mat.roughness = 0.3
    return mat
```


## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
