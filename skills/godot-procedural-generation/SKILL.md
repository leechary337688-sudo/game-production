---
name: godot-procedural-generation
description: "使用FastNoiseLite、随机行走、BSP树、波函数坍缩和种子随机化的程序化内容生成（地牢、地形、战利品、关卡）专家蓝图。适用于创建roguelike游戏、沙盒游戏或动态内容。关键词：程序化、生成、FastNoiseLite、Perlin噪声、BSP、醉汉行走、波函数坍缩、种子化。"
---

# 程序化生成

种子算法、噪声函数和约束传播定义了可重玩的内容生成。

## 可用脚本

### [wfc_level_generator.gd](scripts/wfc_level_generator.gd)
具有瓦片邻接规则的专家级波函数坍缩实现。

## 程序化生成中切勿做的事情

- **切勿忘记种子RNG** — 没有种子的`randi()` = 每次相同的地牢。使用`seed(hash(Time.get_ticks_msec()))`或暴露种子以用于速通。
- **切勿在`_ready()`中使用`randf()`进行多人游戏** — 每个客户端在不同时间调用`_ready()` = 不同步的RNG = 不同的地牢。使用服务器的共享种子。
- **切勿跳过验证** — 醉汉行走地牢没有出口？可玩性失败。始终验证（例如，使用A*从起点到终点）或重新生成。
- **切勿每帧调用`noise.get_noise_2d()`** — 每帧调用噪声10,000次 = 延迟。在`_ready()`中预生成高度图，缓存在数组中。
- **切勿使用没有最小房间大小的BSP** — 无限分割 = 1x1房间 = 崩溃。设置`min_size`（例如，6x6）以防止过度细分。
- **切勿忽略WFC矛盾** — 波函数坍缩在没有有效瓦片时失败。必须检测矛盾，回溯或重新启动生成。
- **切勿阻塞主线程进行大型生成** — 在`_ready()`中生成1000x1000地形 = 冻结。使用工作线程或使用`await`跨帧分割。

---

```gdscript
func generate_dungeon(width: int, height: int, fill_percent: float = 0.4) -> Array:
    var grid := []
    for y in height:
        var row := []
        for x in width:
            row.append(1)  # 1 = 墙
        grid.append(row)
    
    # 从中心开始
    var x := width / 2
    var y := height / 2
    var floor_tiles := 0
    var target_floor := int(width * height * fill_percent)
    
    while floor_tiles < target_floor:
        if grid[y][x] == 1:
            grid[y][x] = 0  # 创建地板
            floor_tiles += 1
        
        # 随机行走
        var dir := randi() % 4
        match dir:
            0: x = clampi(x + 1, 0, width - 1)
            1: x = clampi(x - 1, 0, width - 1)
            2: y = clampi(y + 1, 0, height - 1)
            3: y = clampi(y - 1, 0, height - 1)
    
    return grid
```

## Perlin噪声地形

```gdscript
var noise := FastNoiseLite.new()

func generate_terrain(width: int, height: int) -> Array:
    noise.seed = randi()
    noise.frequency = 0.05
    
    var terrain := []
    for y in height:
        var row := []
        for x in width:
            var value := noise.get_noise_2d(x, y)
            
            # 映射噪声到瓦片类型
            var tile: int
            if value < -0.2:
                tile = 0  # 水
            elif value < 0.2:
                tile = 1  # 草
            else:
                tile = 2  # 山
            
            row.append(tile)
        terrain.append(row)
    
    return terrain
```

## BSP房间

```gdscript
class_name BSPRoom

var x: int
var y: int
var width: int
var height: int
var left: BSPRoom = null
var right: BSPRoom = null

func split(min_size: int = 6) -> bool:
    if left or right:
        return false  # 已经分割
    
    # 选择分割方向
    var split_horizontal := randf() > 0.5
    
    if width > height and float(width) / float(height) >= 1.25:
        split_horizontal = false
    elif height > width and float(height) / float(width) >= 1.25:
        split_horizontal = true
    
    var max := (height if split_horizontal else width) - min_size
    if max <= min_size:
        return false  # 太小
    
    var split_pos := randi_range(min_size, max)
    
    if split_horizontal:
        left = BSPRoom.new()
        left.x = x
        left.y = y
        left.width = width
        left.height = split_pos
        
        right = BSPRoom.new()
        right.x = x
        right.y = y + split_pos
        right.width = width
        right.height = height - split_pos
    else:
        left = BSPRoom.new()
        left.x = x
        left.y = y
        left.width = split_pos
        left.height = height
        
        right = BSPRoom.new()
        right.x = x + split_pos
        right.y = y
        right.width = width - split_pos
        right.height = height
    
    return true

func generate_bsp_dungeon(width: int, height: int, iterations: int = 4) -> Array[BSPRoom]:
    var root := BSPRoom.new()
    root.x = 0
    root.y = 0
    root.width = width
    root.height = height
    
    var rooms: Array[BSPRoom] = [root]
    
    for i in iterations:
        var new_rooms: Array[BSPRoom] = []
        for room in rooms:
            if room.split():
                new_rooms.append(room.left)
                new_rooms.append(room.right)
            else:
                new_rooms.append(room)
        rooms = new_rooms
    
    return rooms
```

## 随机战利品

```gdscript
func generate_loot(loot_level: int) -> Array[Item]:
    var items: Array[Item] = []
    var roll_count := randi_range(1, 3)
    
    for i in roll_count:
        var rarity := roll_rarity()
        var item := get_random_item(rarity, loot_level)
        items.append(item)
    
    return items

func roll_rarity() -> String:
    var roll := randf()
    if roll < 0.6:
        return "common"
    elif roll < 0.85:
        return "uncommon"
    elif roll < 0.95:
        return "rare"
    else:
        return "legendary"
```

## 波函数坍缩

```gdscript
# 简化的WFC用于瓦片模式
# 加载兼容的瓦片邻接规则
var tile_rules := {
    "grass": ["grass", "path", "water_edge"],
    "water": ["water", "water_edge"],
    "path": ["grass", "path"]
}

func wfc_generate(width: int, height: int) -> Array:
    var grid := []
    for y in height:
        var row := []
        for x in width:
            row.append(null)  # 未坍缩
        grid.append(row)
    
    # 坍缩单元格直到完成
    while has_uncollapsed(grid):
        var pos := find_lowest_entropy(grid)
        collapse_cell(grid, pos)
        propagate_constraints(grid, pos)
    
    return grid
```

## 最佳实践

1. **种子化** - 使用种子以实现可重复性
2. **验证** - 确保可玩关卡
3. **性能** - 如果需要，异步生成

## 参考
- 相关：`godot-tilemap-mastery`、`godot-resource-data-patterns`

### 相关
- 大师技能：[godot-master](../godot-master/SKILL.md)
