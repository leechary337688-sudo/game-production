---
name: godot-3d-world-building
description: "使用GridMap与MeshLibrary、CSG构造实体几何、WorldEnvironment设置、ProceduralSkyMaterial和体积雾的3D级别设计专家模式。适用于构建3D级别、模块化瓷砖集、BSP风格几何或环境效果。触发关键词：GridMap、MeshLibrary、set_cell_item、get_cell_item、map_to_local、local_to_map、CSGCombiner3D、CSGBox3D、CSGSphere3D、CSGPolygon3D、WorldEnvironment、Environment、Sky、ProceduralSkyMaterial、PanoramaSkyMaterial、fog_enabled、volumetric_fog_enabled。"
---

# 3D 世界构建

使用GridMap、CSG和环境设置的级别设计专家指导。

## 永远不要做

- **永远不要忘记烘焙GridMap导航** — GridMap不会自动生成导航网格。使用EditorPlugin或手动NavigationRegion3D。
- **永远不要在最终游戏几何中使用CSG** — CSG用于原型设计。转换为静态网格以提高性能（在编辑器中使用“Bake CSG Mesh”）。
- **放置瓷砖后永远不要缩放GridMap单元格大小** — 更改`cell_size`不会更新现有瓷砖，导致错位。在开始时设置一次。
- **永远不要在没有碰撞形状的情况下使用MeshLibrary** — 没有碰撞的项目会生成仅视觉的几何体，玩家会掉落。
- **在没有DirectionalLight3D的情况下永远不要启用体积雾** — 体积雾需要至少一个光源进行散射。没有光源 = 没有可见雾。

---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [collision_gen.gd](scripts/collision_gen.gd)
从网格自动生成碰撞形状。当导入没有碰撞的模型或用于程序几何时使用。

### [gridmap_runtime_builder.gd](scripts/gridmap_runtime_builder.gd)
运行时的GridMap瓷砖放置，支持批操作和自动导航烘焙。

### [csg_bake_tool.gd](scripts/csg_bake_tool.gd)
编辑器脚本，将CSG几何体烘焙到静态网格，包括适当的材质和碰撞。当最终化级别原型时使用。

### [lod_manager.gd](scripts/lod_manager.gd)
基于相机距离的级别细节切换。管理大户外场景的网格交换和可见性。

### [occlusion_setup.gd](scripts/occlusion_setup.gd)
OccluderInstance3D配置，用于手动遮挡剔除。用于有许多房间的室内级别。

---

## GridMap 基础

### 设置工作流

```gdscript
# 1. 创建MeshLibrary资源（编辑器）
# 场景 → 新建继承场景 → 创建网格对齐的网格
# 场景 → 转换为 → MeshLibrary...

# 2. 分配给GridMap
extends GridMap

func _ready() -> void:
    mesh_library = load("res://tilesets/dungeon_library.tres")
    cell_size = Vector3(2, 2, 2)  # 必须与库的单元格大小匹配
```

### 单元格操作

```gdscript
# gridmap_builder.gd
extends GridMap

# 放置单元格
func place_tile(grid_pos: Vector3i, tile_index: int) -> void:
    set_cell_item(grid_pos, tile_index)

# 获取单元格
func get_tile(grid_pos: Vector3i) -> int:
    return get_cell_item(grid_pos)  # 返回索引或INVALID_CELL_ITEM (-1)

# 移除单元格
func remove_tile(grid_pos: Vector3i) -> void:
    set_cell_item(grid_pos, INVALID_CELL_ITEM)

# 旋转单元格 (0-23, 参见GridMap.ROTATION_*常量)
func place_rotated(grid_pos: Vector3i, tile_index: int, orientation: int) -> void:
    set_cell_item(grid_pos, tile_index, orientation)
```

### 坐标转换

```gdscript
# 世界位置 ↔ 网格坐标
func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        var camera := get_viewport().get_camera_3d()
        var from := camera.project_ray_origin(event.position)
        var to := from + camera.project_ray_normal(event.position) * 1000
        
        var space := get_world_3d().direct_space_state
        var query := PhysicsRayQueryParameters3D.create(from, to)
        var result := space.intersect_ray(query)
        
        if result:
            var world_pos: Vector3 = result.position
            var grid_pos := local_to_map(to_local(world_pos))
            place_tile(grid_pos, 0)  # 在点击位置放置瓷砖

# 网格 → 世界
func get_cell_center(grid_pos: Vector3i) -> Vector3:
    return to_global(map_to_local(grid_pos))
```

---

## MeshLibrary 创建

### 碰撞设置

```gdscript
# tile_scene.tscn（在转换为MeshLibrary之前）
# 根节点：Node3D
#   ├─ MeshInstance3D（视觉）
#   └─ StaticBody3D（碰撞）
#       └─ CollisionShape3D

# 关键：StaticBody3D必须是兄弟/子节点，以便GridMap检测碰撞
```

### 项目元数据

```gdscript
# 访问MeshLibrary项目数据
func get_tile_name(tile_index: int) -> String:
    return mesh_library.get_item_name(tile_index)

# 自定义元数据（存储在MeshLibrary资源中）
# 使用编辑器脚本中的item_set_name()来组织
```

---

## CSG（构造实体几何）

### 布尔操作

```
CSG Combiner3D
  ├─ CSGBox3D（操作：Union）        # 基础房间
  ├─ CSGBox3D（操作：Subtraction）  # 门洞切除
  └─ CSGSphere3D（操作：Intersection）  # 圆角
```

### CSG 刷子类型

```gdscript
# CSGBox3D - 房间基本体
var room := CSGBox3D.new()
room.size = Vector3(10, 5, 10)

# CSGCylinder3D - 柱子
var pillar := CSGCylinder3D.new()
pillar.radius = 0.5
pillar.height = 5.0

# CSGSphere3D - 圆顶
var dome := CSGSphere3D.new()
dome.radius = 3.0
dome.radial_segments = 16
dome.rings = 8

# CSGPolygon3D - 挤压2D形状
var arch := CSGPolygon3D.new()
arch.polygon = PackedVector2Array([
    Vector2(-1, 0), Vector2(-1, 2), Vector2(1, 2), Vector2(1, 0)
])
arch.depth = 0.5
```

### CSG 性能

```gdscript
# ❌ 错误：在运行时使用CSG（慢）
func _ready() -> void:
    var csg := CSGBox3D.new()
    add_child(csg)  # 每帧重新计算网格

# ✅ 正确：烘焙到MeshInstance3D（仅编辑器）
# 选择CSG节点 → 网格 → 烘焙网格实例
# 然后删除CSG节点

# ✅ 同样正确：使用CSG进行级别编辑器，在导出时烘焙
```

---

## WorldEnvironment 设置

### 天空配置

```gdscript
# world_env.gd
extends WorldEnvironment

func _ready() -> void:
    var env := Environment.new()
    environment = env
    
    # 程序化天空
    env.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_mat := ProceduralSkyMaterial.new()
    
    sky_mat.sky_top_color = Color(0.4, 0.6, 1.0)  # 蓝色
    sky_mat.sky_horizon_color = Color(0.8, 0.9, 1.0)  # 浅色
    sky_mat.ground_bottom_color = Color(0.2, 0.2, 0.1)
    sky_mat.sun_angle_max = 30.0
    
    sky.sky_material = sky_mat
    env.sky = sky
```

### HDRI 天空盒

```gdscript
# 用于真实感光照
var env := environment
env.background_mode = Environment.BG_SKY

var sky := Sky.new()
var panorama := PanoramaSkyMaterial.new()
panorama.panorama = load("res://hdri/sunset.hdr")  # 等距长方形HDR图像

sky.sky_material = panorama
env.sky = sky

# 天空对环境光的贡献
env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
env.ambient_light_sky_contribution = 1.0
```

---

## 雾与大气

### 指数雾

```gdscript
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    
    env.fog_enabled = true
    env.fog_mode = Environment.FOG_MODE_EXPONENTIAL
    env.fog_density = 0.01  # 0.0-1.0
    env.fog_light_color = Color(0.9, 0.95, 1.0)  # 偏蓝色
    env.fog_light_energy = 1.0
```

### 深度雾

```gdscript
# 基于距离的雾
env.fog_enabled = true
env.fog_mode = Environment.FOG_MODE_DEPTH
env.fog_depth_begin = 50.0  # 开始距离
env.fog_depth_end = 200.0   # 结束距离（完全不透明）
env.fog_depth_curve = 1.0   # 衰减曲线
```

### 体积雾

```gdscript
# 需要DirectionalLight3D进行散射
env.volumetric_fog_enabled = true
env.volumetric_fog_density = 0.05
env.volumetric_fog_albedo = Color(0.9, 0.9, 1.0)
env.volumetric_fog_emission = Color.BLACK
env.volumetric_fog_gi_inject = 1.0  # GI对雾的影响程度

# 性能设置
env.volumetric_fog_temporal_reprojection_enabled = true
env.volumetric_fog_detail_spread = 2.0
```

---

## 级别流式加载 / LOD

### GridMap 分块

```gdscript
# level_streamer.gd - 基于玩家位置加载/卸载GridMap块
extends Node3D

@export var chunk_size := 32  # 每块的网格单元格数
@export var load_radius := 2  # 保持加载的块数

var loaded_chunks := {}  # Vector2i → GridMap

func _process(delta: float) -> void:
    var player_pos := get_player_position()
    var player_chunk := Vector2i(
        int(player_pos.x / (chunk_size * cell_size.x)),
        int(player_pos.z / (chunk_size * cell_size.z))
    )
    
    # 加载附近块
    for x in range(-load_radius, load_radius + 1):
        for z in range(-load_radius, load_radius + 1):
            var chunk_coord := player_chunk + Vector2i(x, z)
            if chunk_coord not in loaded_chunks:
                load_chunk(chunk_coord)
    
    # 卸载远处块
    for chunk_coord in loaded_chunks.keys():
        var dist := chunk_coord.distance_to(player_chunk)
        if dist > load_radius:
            unload_chunk(chunk_coord)

func load_chunk(coord: Vector2i) -> void:
    var gridmap := GridMap.new()
    gridmap.mesh_library = preload("res://library.tres")
    add_child(gridmap)
    loaded_chunks[coord] = gridmap
    
    # TODO: 从文件/数据库加载块数据
    # gridmap.set_cell_item(...)

func unload_chunk(coord: Vector2i) -> void:
    var gridmap: GridMap = loaded_chunks[coord]
    gridmap.queue_free()
    loaded_chunks.erase(coord)
```

---

## 程序化生成

### 使用GridMap随机地牢

```gdscript
# dungeon_generator.gd
extends GridMap

enum Tile { FLOOR, WALL, DOOR }

func generate_room(pos: Vector3i, size: Vector3i) -> void:
    # 用地板填充
    for x in range(size.x):
        for z in range(size.z):
            set_cell_item(pos + Vector3i(x, 0, z), Tile.FLOOR)
    
    # 添加墙壁
    for x in range(size.x):
        set_cell_item(pos + Vector3i(x, 0, 0), Tile.WALL)  # 北边
        set_cell_item(pos + Vector3i(x, 0, size.z - 1), Tile.WALL)  # 南边
    
    for z in range(size.z):
        set_cell_item(pos + Vector3i(0, 0, z), Tile.WALL)  # 西边
        set_cell_item(pos + Vector3i(size.x - 1, 0, z), Tile.WALL)  # 东边

func _ready() -> void:
    generate_room(Vector3i(0, 0, 0), Vector3i(10, 1, 10))
```

---

## 边界情况

### GridMap 单元格不碰撞

```gdscript
# 问题：MeshLibrary项目缺少碰撞
# 解决方案：确保源场景中有StaticBody3D + CollisionShape3D

# 在代码中验证：
var item_shapes := mesh_library.get_item_shapes(tile_index)
if item_shapes.is_empty():
    push_error("Tile %d has no collision!" % tile_index)
```

### CSG 网格闪烁

```gdscript
# 问题：重叠CSG操作之间的Z-fighting
# 解决方案：添加小偏移（0.001）以防止精确重叠

var box := CSGBox3D.new()
box.size = Vector3(10, 5, 10)

var cutout := CSGBox3D.new()
cutout.operation = CSGShape3D.OPERATION_SUBTRACTION
cutout.size = Vector3(2, 3, 2.002)  # 略微更大的深度
```

## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
