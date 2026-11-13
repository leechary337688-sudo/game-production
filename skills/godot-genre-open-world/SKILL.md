---
name: godot-genre-open-world
description: "开放世界游戏的专家蓝图，包括基于块的流式加载（动态加载/卸载区域）、浮点原点（防止超过5000单位的精度抖动）、HLOD（用于远处网格的层次细节）、持久状态（跟踪未加载块中的实体变化）、POI发现系统（指南针、标记）和线程加载（防止卡顿）。适用于RPG、沙盒或探索游戏。触发关键词：open_world, chunk_streaming, floating_origin, HLOD, persistent_state, POI_discovery, threaded_loading。"
---

# 类型：开放世界

专家蓝图，平衡规模、性能和玩家参与度。

## 绝对不要做

- **绝对不要优先考虑规模而非密度** — 巨大的空地图很无聊。较小、更密集的地图胜过广阔的沙漠。密度 > 规模。
- **绝对不要保存所有内容** — 500MB的保存文件会破坏性能。只保存*变化*（增量压缩）。未修改的对象使用默认值。
- **绝对不要在10公里距离进行物理处理** — 对于距离大于2单位的块，禁用物理处理。对远处逻辑使用简单模拟（计时器）。
- **绝对不要忽略浮点精度** — 在5000+单位时，物体会抖动。实现浮点原点：当玩家超过阈值时移动世界。
- **绝对不要同步块加载** — 在_process()中加载块会导致卡顿。使用Thread.new()进行后台加载。
---

## 可用脚本

> **强制**：在实现相应模式前阅读适当的脚本。

### [floating_origin_shifter.gd](scripts/floating_origin_shifter.gd)
当玩家超过从(0,0,0)的阈值距离时移动世界原点。防止大距离下的浮点精度抖动。

---

## 核心循环
1.  **遍历**：玩家跨越 vast distances（步行、车辆、坐骑）。
2.  **发现**：玩家动态找到兴趣点（POIs）。
3.  **任务**：玩家接受需要旅行的任务。
4.  **进展**：世界状态基于玩家行动改变。
5.  **沉浸**：动态天气、昼夜循环影响游戏玩法。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 地形 | `godot-3d-world-building`, `shaders` | 大规模地形，三平面映射 |
| 2. 优化 | `level-of-detail`, `multithreading` | HLOD，后台加载，遮挡 |
| 3. 数据 | `godot-save-load-systems` | 保存数千个对象的状态 |
| 4. 导航 | `godot-navigation-pathfinding` | 在大型动态地图上进行AI路径规划 |
| 5. 核心 | `floating-origin` | 防止在10,000+单位时的精度抖动 |

## 架构概述

### 1. 流式加载器（块管理器）
加载和卸载玩家周围的世界。

```gdscript
# world_streamer.gd
extends Node3D

@export var chunk_size: float = 100.0
@export var render_distance: int = 4
var active_chunks: Dictionary = {}

func _process(delta: float) -> void:
    var player_chunk = Vector2i(player.position.x / chunk_size, player.position.z / chunk_size)
    update_chunks(player_chunk)

func update_chunks(center: Vector2i) -> void:
    # 1. 确定需要的块
    var needed = []
    for x in range(-render_distance, render_distance + 1):
        for y in range(-render_distance, render_distance + 1):
            needed.append(center + Vector2i(x, y))
    
    # 2. 卸载旧的
    for chunk in active_chunks.keys():
        if chunk not in needed:
            unload_chunk(chunk)
    
    # 3. 加载新的（线程化）
    for chunk in needed:
        if chunk not in active_chunks:
            load_chunk_async(chunk)
```

### 2. 浮点原点
解决当远离(0,0,0)时的浮点精度错误（抖动）。

```gdscript
# floating_origin.gd
extends Node

const THRESHOLD: float = 5000.0

func _process(delta: float) -> void:
    if player.global_position.length() > THRESHOLD:
        shift_world(-player.global_position)

func shift_world(offset: Vector3) -> void:
    # 将整个世界向玩家位置相反方向移动
    # 所以玩家产生移动的幻觉，但逻辑保持在0,0附近
    for node in get_tree().get_nodes_in_group("world_root"):
        node.global_position += offset
```

### 3. 任务状态数据库
当块45未加载时跟踪“我是否在块45杀死了强盗？”

```gdscript
# global_state.gd
var chunk_data: Dictionary = {} # Vector2i -> Dictionary

func set_entity_dead(chunk_id: Vector2i, entity_id: String) -> void:
    if not chunk_data.has(chunk_id):
        chunk_data[chunk_id] = {}
    chunk_data[chunk_id][entity_id] = { "dead": true }
```

## 关键机制实现

### HLOD（层次细节级别）
当从1公里外观看时，将100栋房子合并成1个简单网格。
*   **近处**：高多边形房子 + 道具。
*   **远处**：低多边形广告牌 / impostor 网格。
*   **非常远**：地形纹理的一部分。

### 兴趣点（发现）
指南针栏逻辑。

```gdscript
func update_compass() -> void:
    for poi in active_pois:
        var direction = player.global_transform.basis.z
        var to_poi = (poi.global_position - player.global_position).normalized()
        var angle = direction.angle_to(to_poi)
        # 将角度映射到UI位置
```

## Godot特定提示

*   **VisibilityRange**：在MeshInstance3D上使用特定的 `visibility_range_begin` 和 `end` 来处理LODs，无需专用LOD节点。
*   **Thread**：使用 `Thread.new()` 加载块以防止帧卡顿。
*   **OcclusionCulling**：为大城市烘焙遮挡。对于开放田野，简单的距离裁剪通常足够。

## 常见陷阱

1.  **“空”世界**：巨大的地图，无事可做。**修复**：密度 > 规模。较小、更密集的地图优于广阔的沙漠。
2.  **保存文件臃肿**：保存文件是500MB。**修复**：只保存*变化*（增量压缩）。如果石头没有移动，不要保存它。
3.  **距离物理**：物理在远处崩溃。**修复**：对于距离大于2单位的块，禁用物理处理。对远处逻辑使用简单“模拟”。


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
