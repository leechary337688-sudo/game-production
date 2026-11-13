---
name: godot-tilemap-mastery
description: "TileMapLayer和TileSet系统的专家蓝图，用于高效的2D关卡设计。覆盖地形自动贴图、物理层、自定义数据、导航集成和运行时操作。适用于构建基于网格的关卡或实现可破坏瓦片。关键词TileMapLayer、TileSet、地形、自动贴图、图集、物理层、自定义数据。"
---

# TileMap 精通

TileMapLayer网格、TileSet图集、地形自动贴图和自定义数据定义了高效的2D关卡系统。

## 可用脚本

### [tilemap_data_manager.gd](scripts/tilemap_data_manager.gd)
专家级TileMap序列化和分块管理器，适用于大型世界。

## 在TileMaps中永远不要做的事

- **永远不要在循环中不使用批处理就调用set_cell()** — 1000个瓦片 × `set_cell()` = 1000个单独函数调用 = 慢。使用`set_cells_terrain_connect()`进行批量操作或缓存更改，一次应用。
- **永远不要忘记source_id参数** — `set_cell(pos, atlas_coords)`没有source_id？错误重载 = 崩溃或静默失败。使用`set_cell(pos, source_id, atlas_coords)`。
- **永远不要混合瓦片坐标与世界坐标** — `set_cell(mouse_position)`没有`local_to_map()`？错误网格位置。始终转换：`local_to_map(global_pos)`。
- **永远不要跳过地形集配置** — 手动为有机形状分配瓦片？100+个瓦片用于草地补丁。使用带有地形集的`set_cells_terrain_connect()`进行自动贴图。
- **永远不要使用TileMap处理动态实体** — 敌人/拾取物作为瓦片？没有信号、物理、脚本。使用Node2D/CharacterBody2D，保留TileMap用于静态/可破坏几何体。
- **永远不要在_physics_process中查询get_cell_tile_data()** — 每帧瓦片数据查找？性能下降。在字典中缓存瓦片数据：`tile_cache[pos] = get_cell_tile_data(pos)`。

---

### 步骤1：创建TileSet资源

1. 创建一个`TileMapLayer`节点
2. 在检查器中：**TileSet → 新建TileSet**
3. 点击TileSet打开底部TileSet编辑器

### 步骤2：添加瓦片图集

1. 在TileSet编辑器中：**+ → 图集**
2. 选择您的瓦片表纹理
3. 配置网格大小（例如，每个瓦片16x16像素）

### 步骤3：添加物理、碰撞、导航

```gdscript
# 每个瓦片可以具有：
# - 物理层：每个瓦片的CollisionShape2D
# - 地形：自动贴图规则
# - 自定义数据：任意属性
```

**为瓦片添加碰撞：**
1. 在TileSet编辑器中选择瓦片
2. 切换到“物理”选项卡
3. 绘制碰撞多边形

## 使用TileMapLayer

### 基本Tilemap设置

```gdscript
extends TileMapLayer

func _ready() -> void:
    # 在网格坐标(x, y)处设置瓦片
    set_cell(Vector2i(0, 0), 0, Vector2i(0, 0))  # source_id, atlas_coords
    
    # 获取坐标处的瓦片
    var atlas_coords := get_cell_atlas_coords(Vector2i(0, 0))
    
    # 清除瓦片
    erase_cell(Vector2i(0, 0))
```

### 运行时瓦片放置

```gdscript
extends TileMapLayer

func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        var global_pos := get_global_mouse_position()
        var tile_pos := local_to_map(global_pos)
        
        # 放置草地瓦片（假设source_id=0, atlas=(0,0)）
        set_cell(tile_pos, 0, Vector2i(0, 0))
```

### 洪水填充模式

```gdscript
func flood_fill(start_pos: Vector2i, tile_source: int, atlas_coords: Vector2i) -> void:
    var cells_to_fill: Array[Vector2i] = [start_pos]
    var original_tile := get_cell_atlas_coords(start_pos)
    
    while cells_to_fill.size() > 0:
        var current := cells_to_fill.pop_back()
        
        if get_cell_atlas_coords(current) != original_tile:
            continue
        
        set_cell(current, tile_source, atlas_coords)
        
        # 添加邻居
        for dir in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
            cells_to_fill.append(current + dir)
```

## 地形自动贴图

### 设置地形集

1. 在TileSet编辑器中：**地形**选项卡
2. 添加地形集（例如，“地面”）
3. 添加地形（例如，“草地”，“泥土”）
4. 通过绘制为瓦片分配地形

### 在代码中使用地形

```gdscript
extends TileMapLayer

func paint_terrain(start: Vector2i, end: Vector2i, terrain_set: int, terrain: int) -> void:
    for x in range(start.x, end.x + 1):
        for y in range(start.y, end.y + 1):
            set_cells_terrain_connect(
                [Vector2i(x, y)],
                terrain_set,
                terrain,
                false  # ignore_empty_terrains
            )
```

## 多层模式

```gdscript
# 场景结构：
# Node2D (Level)
#   ├─ TileMapLayer (Ground)
#   ├─ TileMapLayer (Decoration)
#   └─ TileMapLayer (Collision)

# 每层可以有不同的：
# - 渲染顺序 (z_index)
# - 碰撞层/掩码
# - 调制（颜色色调）
```

## 物理集成

### 启用物理层

1. TileSet编辑器 → **物理层**
2. 添加物理层
3. 为瓦片分配碰撞形状

**从代码检查碰撞：**
```gdscript
func _physics_process(delta: float) -> void:
    # TileMapLayer充当StaticBody2D
    # CharacterBody2D.move_and_slide() 自动检测tilemap碰撞
    pass
```

### 单向碰撞瓦片

```gdscript
# 在TileSet物理层设置中：
# - 启用“单向碰撞”
# - 设置“单向碰撞边距”

# 角色可以从下方跳穿
```

## 自定义瓦片数据

### 定义自定义数据层

1. TileSet编辑器 → **自定义数据层**
2. 添加属性（例如，“damage_per_second: int”）
3. 为特定瓦片设置值

### 读取自定义数据

```gdscript
func get_tile_damage(tile_pos: Vector2i) -> int:
    var tile_data := get_cell_tile_data(tile_pos)
    if tile_data:
        return tile_data.get_custom_data("damage_per_second")
    return 0
```

## 性能优化

### 使用TileMapLayer组

```gdscript
# 静态几何体：单个大TileMapLayer
# 动态瓦片：运行时更改的单独层
```

### 大型世界分块

```gdscript
# 将世界拆分为多个TileMapLayer节点
# 基于玩家位置加载/卸载块

const CHUNK_SIZE := 32

func load_chunk(chunk_coords: Vector2i) -> void:
    var chunk_name := "Chunk_%d_%d" % [chunk_coords.x, chunk_coords.y]
    var chunk := TileMapLayer.new()
    chunk.name = chunk_name
    chunk.tile_set = base_tileset
    add_child(chunk)
    # 加载此块的瓦片...
```

## 导航集成

### 设置导航层

1. TileSet编辑器 → **导航层**
2. 添加导航层
3. 在瓦片上绘制导航多边形

**与NavigationAgent2D使用：**
```gdscript
# 从TileMap自动创建导航
# NavigationAgent2D.get_next_path_position() 立即工作
```

## 最佳实践

### 1. 按目的组织TileSet

```
TileSet 层：
- 地面（地形=草地、泥土、石头）
- 墙壁（碰撞 + 渲染）
- 装饰（无碰撞、覆盖）
```

## 可用脚本

> **强制**：在实现地形系统或运行时放置前阅读。

### [terrain_autotile.gd](scripts/terrain_autotile.gd)
运行时地形自动贴图，带有`set_cells_terrain_connect`批处理和验证。

### [tilemap_chunking.gd](scripts/tilemap_chunking.gd)
基于块的TileMap管理，带有批处理更新 - 大型过程世界必备。

### 2. 使用地形处理有机形状

```gdscript
# ✅ 好 - 平滑地形过渡
set_cells_terrain_connect(tile_positions, 0, 0)

# ❌ 坏 - 手动为有机形状分配瓦片
for pos in positions:
    set_cell(pos, 0, Vector2i(0, 0))
```

### 3. 层Z索引管理

```gdscript
# 背景层
$Background.z_index = -10

# 地面层
$Ground.z_index = 0

# 前景装饰
$Foreground.z_index = 10
```

## 常见模式

### 可破坏瓦片

```gdscript
func destroy_tile(world_pos: Vector2) -> void:
    var tile_pos := local_to_map(world_pos)
    var tile_data := get_cell_tile_data(tile_pos)
    
    if tile_data and tile_data.get_custom_data("destructible"):
        erase_cell(tile_pos)
        # 生成粒子效果、掉落物品等。
```

### 瓦片高亮

```gdscript
@onready var highlight_layer: TileMapLayer = $HighlightLayer

func highlight_tile(tile_pos: Vector2i) -> void:
    highlight_layer.clear()
    highlight_layer.set_cell(tile_pos, 0, Vector2i(0, 0))
```

## 参考
- [Godot 文档：TileMaps](https://docs.godotengine.org/en/stable/tutorials/2d/using_tilemaps.html)
- [Godot 文档：TileSets](https://docs.godotengine.org/en/stable/tutorials/2d/using_tilesets.html)


### 相关
- 掌握技能：[godot-master](../godot-master/SKILL.md)
