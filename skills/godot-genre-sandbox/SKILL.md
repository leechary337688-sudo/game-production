---
名称: godot-genre-sandbox
描述: "沙盒游戏专家蓝图（适用于Minecraft、Terraria、Garry's Mod），包含基于物理的交互、细胞自动机、涌现式游戏玩法和创意工具。用于构建具有体素、元素系统、玩家创建结构或程序化世界的开放世界创造游戏。关键词：体素、沙盒、细胞自动机、MultiMesh、区块管理、涌现行为、创意模式。"
---

# 类别：沙盒
物理模拟、涌现式玩法和玩家创造力定义了这一类别。

## 可用脚本

### [voxel_chunk_manager.gd](脚本/voxel_chunk_manager.gd)
使用`MultiMeshInstance3D`进行数千体素的专家级区块化渲染。包括贪婪网格化和性能说明。

## 核心循环
1.  **探索**：玩家发现世界规则和材料
2.  **实验**：玩家测试交互（火燃烧木头）
3.  **建造**：玩家构建结构或机器
4.  **模拟**：游戏运行物理/逻辑系统
5.  **分享**：玩家保存/分享创作
6.  **涌现**：从简单规则中产生的非预期复杂行为

## 沙盒游戏中绝不做的事项

- **绝不每帧模拟整个世界** — 仅更新有最近变化的“脏”区块。休眠区块浪费90%以上的CPU。使用空间哈希跟踪活动区域。
- **绝不为体素使用单独的`RigidBody`节点** — 1000+物理体 = 瞬间崩溃。对流体/沙子使用细胞自动机，对固体块使用静态碰撞，仅对玩家放置的对象使用动态体。
- **绝不保存每个块的绝对变换** — 一个256×256世界 = 65,536个块。使用基于区块的RLE（运行长度编码）：`{type:AIR, count:50000}`压缩大量空空间。
- **绝不每帧更新`MultiMesh`实例变换** — 这会强制GPU缓冲更新。批量更改，在更改时重建区块，而不是每帧。
- **绝不硬编码元素交互**（`if wood + fire: burn()`） — 使用基于属性的系统：`if temperature > ignition_point and flammable > 0`。这使玩家能够发现涌现组合。
- **绝不使用`Node`表示每个网格单元** — 节点有200+字节开销。百万块世界仅节点元数据就需要200MB+。使用类型化`Dictionary`或通过`position.x + position.y * width`索引的`PackedInt32Array`。
- **绝不对所有体素进行射线投射以放置工具** — 使用网格量化：`floor(mouse_pos / block_size)`直接计算目标单元。射线投射随体素数量呈O(n)。

## 架构模式

### 1. 元素系统（基于属性的涌现）
建模材料属性，而不是行为。交互从重叠属性中涌现。

```gdscript
# element_data.gd
class_name ElementData extends Resource

enum Type { SOLID, LIQUID, GAS, POWDER }
@export var id: String = "air"
@export var type: Type = Type.GAS
@export var density: float = 0.0      # 用于液体流动方向
@export var flammable: float = 0.0    # 0-1：点燃概率
@export var ignition_temp: float = 400.0
@export var conductivity: float = 0.0  # 用于电力/热量
@export var hardness: float = 1.0     # 挖掘时间乘数

# 边缘情况：如果两个元素密度相同但类型不同怎么办？
# 解决方案：使用次级排序（类型枚举优先级：SOLID > LIQUID > POWDER > GAS）
func should_swap_with(other: ElementData) -> bool:
    if density == other.density:
        return type > other.type  # 枚举比较：SOLID(0) > GAS(3)
    return density > other.density
```

### 2. 细胞自动机网格（落沙模拟）
更新顺序重要。自上而下防止“传送”粒子。

```gdscript
# world_grid.gd
var grid: Dictionary = {}  # Vector2i -> ElementData
var dirty_cells: Array[Vector2i] = []

func _physics_process(_delta: float) -> void:
    # 关键：自上而下排序以防止双重移动
    dirty_cells.sort_custom(func(a, b): return a.y < b.y)
    
    for pos in dirty_cells:
        simulate_cell(pos)
    dirty_cells.clear()

func simulate_cell(pos: Vector2i) -> void:
    var cell = grid.get(pos)
    if not cell: return
    
    match cell.type:
        ElementData.Type.LIQUID, ElementData.Type.POWDER:
            # 尝试向下，然后左下，然后右下
            var targets = [pos + Vector2i.DOWN, 
                           pos + Vector2i(- 1, 1), 
                           pos + Vector2i(1, 1)]
            for target in targets:
                var neighbor = grid.get(target)
                if neighbor and cell.should_swap_with(neighbor):
                    swap_cells(pos, target)
                    mark_dirty(target)
                    return
        
        ElementData.Type.GAS:
            # 气体上升（液体的逆过程）
            var targets = [pos + Vector2i.UP,
                           pos + Vector2i(-1, -1),
                           pos + Vector2i(1, -1)]
            # 相同的交换逻辑...

# 边缘情况：如果多个粒子想要移动到同一单元怎么办？
# 解决方案：仅标记目标脏，不双重交换。下一帧解决冲突。
```

### 3. 工具系统（策略模式）
解耦输入与世界修改。

```gdscript
# tool_base.gd
class_name Tool extends Resource
func use(world_pos: Vector2, world: WorldGrid) -> void: pass

# tool_brush.gd
extends Tool
@export var element: ElementData
@export var radius: int = 1

func use(world_pos: Vector2, world: WorldGrid) -> void:
    var grid_pos = Vector2i(floor(world_pos.x), floor(world_pos.y))
    
    # 圆形笔刷模式
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x*x + y*y <= radius*radius:  # 圆形边界
                var target = grid_pos + Vector2i(x, y)
                world.set_cell(target, element)

# 后备：如果元素放置失败（例如，被不可破坏块占据）？
# 在set_cell()前检查world.can_place(target)，显示视觉反馈。
```

### 4. 基于区块的渲染（3D体素）
仅渲染可见面。使用贪婪网格化合并相邻块。

```gdscript
# 参见脚本/voxel_chunk_manager.gd获取完整实现

# 专家决策树：
# - 小世界（<100k块）：使用SurfaceTool的单一MeshInstance
# - 中世界（100k-1M块）：区块化MultiMesh（见脚本）
# - 大世界（>1M块）：区块化 + 贪婪网格化 + LOD
```

## 沙盒世界保存系统

```gdscript
# chunk_save_data.gd
class_name ChunkSaveData extends Resource

@export var chunk_coord: Vector2i
@export var rle_data: PackedInt32Array  # [type_id, count, type_id, count...]

# 专家技术：运行长度编码
static func encode_chunk(grid: Dictionary, chunk_pos: Vector2i, chunk_size: int) -> ChunkSaveData:
    var data = ChunkSaveData.new()
    data.chunk_coord = chunk_pos
    
    var run_type: int = -1
    var run_count: int = 0
    
    for y in range(chunk_size):
        for x in range(chunk_size):
            var world_pos = chunk_pos * chunk_size + Vector2i(x, y)
            var cell = grid.get(world_pos)
            var type_id = cell.id if cell else 0  # 0 = 空气
            
            if type_id == run_type:
                run_count += 1
            else:
                if run_count > 0:
                    data.rle_data.append(run_type)
                    data.rle_data.append(run_count)
                run_type = type_id
                run_count = 1
    
    # 刷新最终运行
    if run_count > 0:
        data.rle_data.append(run_type)
        data.rle_data.append(run_count)
    
    return data

# 压缩结果：空区块（16×16 = 256个空气块）
# 无RLE：256个整数 = 1024字节
# 有RLE：[0, 256] = 8字节（128倍压缩！）
```

## 玩家创作的物理关节

```gdscript
# joint_tool.gd
func create_hinge(body_a: RigidBody2D, body_b: RigidBody2D, anchor: Vector2) -> void:
    var joint = PinJoint2D.new()
    joint.global_position = anchor
    joint.node_a = body_a.get_path()
    joint.node_b = body_b.get_path()
    joint.softness = 0.5  # 允许轻微弯曲
    add_child(joint)
    
    # 边缘情况：如果关节存在时物体被删除怎么办？
    # 在Godot 4.x中关节会自动断裂，但孤儿节点会泄漏内存。
# 解决方案：
    body_a.tree_exiting.connect(func(): joint.queue_free())
    body_b.tree_exiting.connect(func(): joint.queue_free())

# 后备：玩家将关节连接到静态几何体？
# 在创建关节前检查`body.freeze == false`。
```

## Godot特定专家笔记

- **`MultiMeshInstance3D.multimesh.instance_count`**：必须在缓冲分配前设置。无法动态增长 — 需要重新创建。
- **`RigidBody2D.sleeping`**：物体在无运动2秒后自动休眠。使用`apply_central_impulse(Vector2.ZERO)`强制唤醒而不添加力。
- **`GridMap` vs `MultiMesh`**：GridMap使用MeshLibrary（适合多样性），MultiMesh使用单一网格（适合速度）。结合：GridMap用于结构，MultiMesh用于地形。
- **连续CD**：`continuous_cd`需要凸碰撞形状。对抛射体使用`CapsuleShape2D`，而非`RectangleShape2D`。

## 参考
- 主要技能：[godot-master](../godot-master/SKILL.md)
