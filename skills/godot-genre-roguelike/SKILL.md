---
名称: godot-genre-roguelike
描述: "Roguelike的专家蓝图，包括程序生成（Walker方法，BSP房间），带有元进度的永久死亡（解锁持久性），运行状态与元状态分离，种子RNG（可共享运行），战利品/遗物系统（基于钩子的修改器），以及难度缩放（基于楼层的进度）。用于地牢爬行者，动作roguelike，或roguelite。触发关键词：roguelike，程序生成，永久死亡，元进度，种子RNG，遗物系统，运行状态。"
---

# 类型：Roguelike

Roguelike的专家蓝图，平衡挑战、进度和可重玩性。

## 切勿做

- **切勿让运行纯靠RNG** — 技能应能减轻坏运气。提供保证的物品商店，重掷机制，或起始装备选择。
- **切勿过度强大的元升级** — 如果元进度太强，游戏变成“磨砺取胜”而非“学习取胜”。保持适度（最大+10%伤害）。
- **切勿缺乏内容多样性** — 程序生成重新排列内容。需要至少50+房间，20+敌人，100+物品以保持新鲜感。
- **切勿使用无种子RNG** — 总是用种子初始化RandomNumberGenerator。启用可共享/可复现的运行。
- **切勿允许存档作弊** — 仅在楼层转换时保存状态。加载时删除存档（严格roguelike的标准）。
---

## 可用脚本

> **强制**：在实现相应模式前阅读适当脚本。

### [meta_progression_manager.gd](scripts/meta_progression_manager.gd)
跨运行持久性用于货币和升级。JSON保存/加载带有升级购买/等级跟踪。为生产版本加密。

---

## 核心循环
1.  **准备**：选择角色，装备元升级。
2.  **运行**：完成程序生成的关卡，获取临时增益。
3.  **挑战**：在日益困难的遭遇/首领中生存。
4.  **死亡/胜利**：运行结束，计算资源。
5.  **元进度**：花费资源在永久解锁/升级上。
6.  **重复**：以新能力开始新运行。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 架构 | `state-machines`, `autoloads` | 管理运行状态与元状态 |
| 2. 世界生成 | `godot-procedural-generation`, `tilemap`, `noise` | 每次运行创建独特关卡 |
| 3. 战斗 | `godot-combat-system`, `enemy-ai` | 快节奏、高风险的遭遇 |
| 4. 进度 | `loot-tables`, `godot-inventory-system` | 管理运行特定物品/遗物 |
| 5. 持久性 | `save-system`, `resources` | 在运行间保存元进度 |

## 架构概述

Roguelike需要严格分离**运行状态**（临时）和**元状态**（持久）。

### 1. 运行管理器（AutoLoad）
处理单次运行的生命周期。死亡时完全重置。

```gdscript
# run_manager.gd
extends Node

signal run_started
signal run_ended(victory: bool)
signal floor_changed(new_floor: int)

var current_seed: int
var current_floor: int = 1
var player_stats: Dictionary = {}
var inventory: Array[Resource] = []
var rng: RandomNumberGenerator

func start_run(seed_val: int = -1) -> void:
    rng = RandomNumberGenerator.new()
    if seed_val == -1:
        rng.randomize()
        current_seed = rng.seed
    else:
        current_seed = seed_val
        rng.seed = current_seed
        
    current_floor = 1
    _reset_run_state()
    run_started.emit()

func _reset_run_state() -> void:
    player_stats = { "hp": 100, "gold": 0 }
    inventory.clear()

func next_floor() -> void:
    current_floor += 1
    floor_changed.emit(current_floor)
    
func end_run(victory: bool) -> void:
    run_ended.emit(victory)
    # 在这里触发元进度保存
```

### 2. 元进度（资源）
存储永久解锁。

```gdscript
# meta_progression.gd
class_name MetaProgression
extends Resource

@export var total_runs: int = 0
@export var unlocked_weapons: Array[String] = ["sword_basic"]
@export var currency: int = 0
@export var skill_tree_nodes: Dictionary = {} # node_id: level

func save() -> void:
    ResourceSaver.save(self, "user://meta_progression.tres")

static func load_or_create() -> MetaProgression:
    if ResourceLoader.exists("user://meta_progression.tres"):
        return ResourceLoader.load("user://meta_progression.tres")
    return MetaProgression.new()
```

## 关键机制实现

### 程序地牢生成（Walker方法）
一个简单的“醉汉行走”算法，用于有机、洞穴状或连接房间的布局。

```gdscript
# dungeon_generator.gd
extends Node

@export var map_width: int = 50
@export var map_height: int = 50
@export var max_walkers: int = 5
@export var max_steps: int = 500

func generate_dungeon(tilemap: TileMapLayer, rng: RandomNumberGenerator) -> void:
    tilemap.clear()
    var walkers: Array[Vector2i] = [Vector2i(map_width/2, map_height/2)]
    var floor_tiles: Array[Vector2i] = []
    
    for step in max_steps:
        var new_walkers: Array[Vector2i] = []
        for walker in walkers:
            floor_tiles.append(walker)
            # 25% 机会销毁步行者，25% 生成新步行者
            if rng.randf() < 0.25 and walkers.size() > 1:
                continue # 销毁
            if rng.randf() < 0.25 and walkers.size() < max_walkers:
                new_walkers.append(walker) # 生成
            
            # 移动步行者
            var direction = [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT].pick_random()
            new_walkers.append(walker + direction)
        
        walkers = new_walkers
    
    # 设置瓷砖
    for pos in floor_tiles:
        tilemap.set_cell(pos, 0, Vector2i(0,0)) # 假设 source_id 0 是地板
    
    # 后处理：添加墙壁、生成点等。
```

### 物品/遗物系统（基于资源）
遗物修改状态或添加行为。

```gdscript
# relic.gd
class_name Relic
extends Resource

@export var id: String
@export var name: String
@export var icon: Texture2D
@export_multiline var description: String

# 钩子系统用于复杂交互
func on_pickup(player: Node) -> void:
    pass

func on_damage_dealt(player: Node, target: Node, damage: int) -> int:
    return damage # 返回修改后的伤害

func on_kill(player: Node, target: Node) -> void:
    pass
```

```gdscript
# example_relic_vampirism.gd
extends Relic

func on_kill(player: Node, target: Node) -> void:
    player.heal(5)
    print("吸血触发！")
```

## 常见陷阱

1.  **RNG依赖性**：不要让运行完全依赖运气。好的roguelike允许技能减轻坏RNG。
2.  **元进度不平衡**：如果元升级太强，游戏变成“磨砺取胜”而非“学习取胜”。
3.  **缺乏多样性**：程序生成仅依赖于其排列的内容。需要大量内容（房间、敌人、物品）以保持新鲜感。
4.  **存档作弊**：玩家会尝试退出以避免死亡。仅在楼层转换或退出时保存状态，加载时删除存档（可选，但严格roguelike的标准）。

## Godot特定提示

-   **种子运行**：总是用种子初始化 `RandomNumberGenerator`。这允许玩家共享特定运行布局。
-   **ResourceSaver**：使用 `ResourceSaver` 进行元进度，但要小心深度嵌套资源中的循环引用。
-   **场景作为房间**：将“房间”构建为单独场景（`Room1.tscn`, `Room2.tscn`）并在生成布局中实例化，以在程序布局中保持手工质量。
-   **导航**：如果使用2D导航，在生成地牢布局后重新烘焙 `NavigationRegion2D`。

## 高级技术

-   **协同系统**：标记物品（`fire`, `projectile`, `companion`）并检查标签组合以创建突发增益。
-   **导演AI**：一个无形的“导演”系统，跟踪玩家健康/压力并动态调整生成率（如 *Left 4 Dead*）。

## 参考
- 大师技能： [godot-master](../godot-master/SKILL.md)
