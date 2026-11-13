---
名称: godot-genre-idle-clicker
描述: "空闲/点击游戏的专家蓝图，包括大数字处理（尾数+指数系统）、指数增长曲线（成本增长因子1.15倍）、生成器系统（自动生产者）、离线进度计算、声望系统（重置以获得永久乘数）、数字格式化（K/M/B后缀，科学计数法）。适用于增量游戏、空闲游戏或Cookie Clicker衍生游戏。触发关键词：idle_game, big_number, exponential_growth, generator_system, offline_progress, prestige_system, number_formatting。"
---

# 类型：空闲 / 点击

具有指数级进展和声望机制的专家蓝图。

## 永远不要做

- **永远不要使用标准浮点数表示货币** — 浮点数在大约1.8e308时溢出。从第一天起就实现大数字（尾数+指数）系统。
- **永远不要使用计时器节点获取收入** — 计时器会漂移，并在游戏暂停时暂停。使用`_process(delta)`累积器进行精确计时。
- **永远不要让声望感觉像惩罚** — 声望后的运行应该快2-5倍。否则玩家会感觉失去了进度。
- **永远不要每帧更新所有UI标签** — 以60fps更新50多个标签会导致延迟。使用信号仅在值变化时更新，或将更新频率限制在10fps。
- **永远不要忘记离线进度** — 在游戏开始时计算`离线秒数 * 每秒收入`。缺少这会破坏留存率。
---

## 可用脚本

> **强制**：在实现相应模式前，请阅读适当的脚本。

### [scientific_notation_formatter.gd](scripts/scientific_notation_formatter.gd)
处理1e303+的大数字格式化器。使用K/M/B/T后缀直到Vigintillion，回退到科学计数法。针对高标签数量场景的缓存建议。

---

## 核心循环
1.  **点击**：玩家执行手动操作以获取货币。
2.  **购买**：玩家购买“生成器”（自动点击器）。
3.  **等待**：游戏自行运行，数字上升。
4.  **升级**：玩家购买乘数以增加效率。
5.  **声望**：玩家重置进度以获得永久全局乘数。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 数学 | `godot-gdscript-mastery` | 处理比64位浮点数更大的数字 |
| 2. UI | `godot-ui-containers`, `labels` | 干净地显示“1.5e12”或“1.5T” |
| 3. 数据 | `godot-save-load-systems` | 保存进度，离线时间计算 |
| 4. 逻辑 | `signals` | 将UI与经济模拟解耦 |
| 5. 元 | `json-serialization` | 通过数据平衡数百个升级 |

## 架构概述

### 1. 大数字系统
标准`float`在大约1.8e308时变为`INF`。空闲游戏经常超出。
你需要一个自定义的`BigNumber`类（尾数 + 指数）。

```gdscript
# big_number.gd
class_name BigNumber

var mantissa: float = 0.0 # 1.0 到 10.0
var exponent: int = 0     # 10的幂

func _init(m: float, e: int) -> void:
    mantissa = m
    exponent = e
    normalize()

func normalize() -> void:
    if mantissa >= 10.0:
        mantissa /= 10.0
        exponent += 1
    elif mantissa < 1.0 and mantissa != 0.0:
        mantissa *= 10.0
        exponent -= 1
```

### 2. 生成器系统
产生货币的核心实体。

```gdscript
# generator.gd
class_name Generator extends Resource

@export var id: String
@export var base_cost: BigNumber
@export var base_revenue: BigNumber
@export var cost_growth_factor: float = 1.15

var count: int = 0

func get_cost() -> BigNumber:
    # 成本 = 基础 * (增长 ^ 数量)
    return base_cost.multiply(pow(cost_growth_factor, count))
```

### 3. 模拟管理器（离线进度）
计算游戏关闭期间的收益。

```gdscript
# game_manager.gd
func _ready() -> void:
    var last_save_time = save_data.timestamp
    var current_time = Time.get_unix_time_from_system()
    var seconds_offline = current_time - last_save_time
    
    if seconds_offline > 60:
        var revenue = calculate_revenue_per_second().multiply(seconds_offline)
        add_currency(revenue)
        show_welcome_back_popup(revenue)
```

## 关键机制实现

### 声望系统（重置）
重置`生成器`但保留`声望货币`。

```gdscript
func prestige() -> void:
    if current_money.less_than(prestige_threshold):
        return
        
    # 公式：货币的立方根 / 一百万
    # （仅示例，取决于平衡）
    var gained_keys = calculate_prestige_gain()
    
    save_data.prestige_currency += gained_keys
    save_data.global_multiplier = 1.0 + (save_data.prestige_currency * 0.10)
    
    # 重置
    save_data.money = BigNumber.new(0, 0)
    save_data.generators = ResetGenerators()
    save_game()
    reload_scene()
```

### 格式化数字
将`1234567`显示为`1.23M`。

```gdscript
static func format(bn: BigNumber) -> String:
    if bn.exponent < 3:
        return str(int(bn.mantissa * pow(10, bn.exponent)))
    
    var suffixes = ["", "K", "M", "B", "T", "Qa", "Qi"]
    var suffix_idx = bn.exponent / 3
    
    if suffix_idx < suffixes.size():
        return "%.2f%s" % [bn.mantissa * pow(10, bn.exponent % 3), suffixes[suffix_idx]]
    else:
        return "%.2fe%d" % [bn.mantissa, bn.exponent]
```

## Godot特定技巧

*   **计时器**：不要使用`Timer`节点生成收入（漂移）。使用`_process(delta)`并累积时间。
*   **GridContainer**：非常适合“生成器”列表。
*   **资源**：使用`.tres`文件定义每个生成器（农场、矿山、工厂），以便在不修改代码的情况下调整平衡。

## 常见陷阱

1.  **浮点错误**：使用标准`float`表示货币。**修复**：立即实现大数字系统。
2.  **无聊的声望**：重置感觉像惩罚。**修复**：确保声望后的运行明显更快（2x-5x速度）。
3.  **UI延迟**：每帧更新50个文本标签。**修复**：仅在值实际变化时更新标签（基于信号），或将更新频率限制在10fps。

## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
