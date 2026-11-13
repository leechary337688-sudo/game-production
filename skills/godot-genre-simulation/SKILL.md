---
名称: godot-genre-simulation
描述: "模拟和大亨游戏（如SimCity、RollerCoaster Tycoon、Factorio、Two Point Hospital）的专家蓝图，涵盖经济管理、时间进展、互联系统、NPC模拟和反馈循环。适用于构建管理模拟游戏、大亨游戏、城市建造者或资源优化游戏。关键词：大亨、经济系统、资源管理、时间尺度、反馈循环、进度解锁、模拟时钟。"
---

# 类型: 模拟 / 大亨

优化、系统掌握和令人满意的反馈循环定义了管理游戏。

## 可用脚本

### [sim_tick_manager.gd](scripts/sim_tick_manager.gd)
专家级的基于时钟的模拟，具有可变速度控制和批处理功能。

## 核心循环

`投资 → 建造/管理 → 生成收入 → 优化 → 扩展`

## 在模拟游戏中永远不要做的事情

- **永远不要在`_process()`中单独处理每个模拟实体** — 在固定时钟中批量更新（例如，每秒一次）。模拟1000个业务单独处理 = 每秒60k次调用。批量处理 = 每秒1k次调用。
- **永远不要使用浮点数表示货币** — `float`会累积舍入错误。$1.10 * 3 = $3.2999999。使用`int`分：`1100 * 3 = 3300`分 = $33.00精确。
- **永远不要让早期游戏变得枯燥等待** — 前置决策点。前5分钟必须吸引玩家。不要让他们等待10分钟才能首次解锁。
- **永远不要使用线性成本缩放** — 建筑成本为`10 * 等级`在100级时会崩溃（1000成本）。使用指数：`BASE * pow(1.5, 等级)`创造有意义的权衡。
- **永远不要向玩家隐藏关键数字** — 显示收入/支出明细、生产率、效率百分比。优化游戏需要透明度。
- **永远不要允许无限资源堆叠而没有后果** — 存储上限创造有趣的决策。无限资源移除策略。
- **永远不要每帧更新UI标签** — 更新50个UI标签 @60fps = 每秒3000次更新。使用信号：仅在值更改时更新。

---

## 经济设计

任何大亨游戏的核心是其经济。关键原则：**多个相互关联的资源，强制权衡**。

### 多资源系统

```gdscript
class_name TycoonEconomy
extends Node

signal resource_changed(resource_type: String, amount: float)
signal went_bankrupt

var resources: Dictionary = {
    "money": 10000.0,
    "reputation": 50.0,  # 0-100
    "workers": 0,
    "materials": 100.0,
    "energy": 100.0
}

var resource_caps: Dictionary = {
    "reputation": 100.0,
    "workers": 50,
    "energy": 1000.0
}

func modify_resource(type: String, amount: float) -> bool:
    if amount < 0 and resources[type] + amount < 0:
        if type == "money":
            went_bankrupt.emit()
        return false  # 不能为负
    
    resources[type] = clamp(
        resources[type] + amount,
        0,
        resource_caps.get(type, INF)
    )
    resource_changed.emit(type, resources[type])
    return true
```

### 收入/支出跟踪

```gdscript
class_name FinancialTracker
extends Node

var income_sources: Dictionary = {}  # source_name: amount_per_tick
var expense_sources: Dictionary = {}

signal financial_update(profit: float, income: float, expenses: float)

func calculate_tick() -> float:
    var total_income := 0.0
    var total_expenses := 0.0
    
    for source in income_sources.values():
        total_income += source
    
    for source in expense_sources.values():
        total_expenses += source
    
    var profit := total_income - total_expenses
    financial_update.emit(profit, total_income, total_expenses)
    return profit
```

---

## 时间系统

模拟游戏需要可控的时间：

```gdscript
class_name SimulationTime
extends Node

signal time_tick(delta_game_hours: float)
signal day_changed(day: int)
signal speed_changed(new_speed: int)

enum Speed { PAUSED, NORMAL, FAST, ULTRA }

@export var seconds_per_game_hour := 30.0  # 真实秒数

var current_speed := Speed.NORMAL
var speed_multipliers := {
    Speed.PAUSED: 0.0,
    Speed.NORMAL: 1.0,
    Speed.FAST: 3.0,
    Speed.ULTRA: 10.0
}

var current_hour := 8.0  # 从早上8点开始
var current_day := 1

func _process(delta: float) -> void:
    if current_speed == Speed.PAUSED:
        return
    
    var game_delta := (delta / seconds_per_game_hour) * speed_multipliers[current_speed]
    current_hour += game_delta
    
    if current_hour >= 24.0:
        current_hour -= 24.0
        current_day += 1
        day_changed.emit(current_day)
    
    time_tick.emit(game_delta)

func set_speed(speed: Speed) -> void:
    current_speed = speed
    speed_changed.emit(speed)
```

---

## 实体管理

### 工人/NPC

```gdscript
class_name Worker
extends Node

enum State { IDLE, WORKING, RESTING, COMMUTING }

@export var wage_per_hour: float = 10.0
@export var skill_level: float = 1.0  # 生产力乘数
@export var morale: float = 80.0  # 0-100

var current_state := State.IDLE
var assigned_workstation: Workstation

func update(game_hours: float) -> void:
    match current_state:
        State.WORKING:
            if assigned_workstation:
                var productivity := skill_level * (morale / 100.0)
                assigned_workstation.work(game_hours * productivity)
                morale -= game_hours * 0.5  # 工作使工人疲劳
        State.RESTING:
            morale = min(100.0, morale + game_hours * 2.0)

func calculate_hourly_cost() -> float:
    return wage_per_hour
```

### 建筑/设施

```gdscript
class_name Facility
extends Node3D

@export var build_cost: Dictionary  # resource_type: amount
@export var operating_cost_per_hour: float = 5.0
@export var capacity: int = 5
@export var output_per_hour: Dictionary  # resource_type: amount

var assigned_workers: Array[Worker] = []
var is_operational := true
var efficiency := 1.0

func calculate_output(game_hours: float) -> Dictionary:
    if not is_operational or assigned_workers.is_empty():
        return {}
    
    var worker_efficiency := 0.0
    for worker in assigned_workers:
        worker_efficiency += worker.skill_level * (worker.morale / 100.0)
    worker_efficiency /= capacity  # 归一化到0-1
    
    var result := {}
    for resource in output_per_hour:
        result[resource] = output_per_hour[resource] * game_hours * worker_efficiency * efficiency
    return result
```

---

## 顾客/需求系统

```gdscript
class_name CustomerSimulation
extends Node

@export var base_customers_per_hour := 10.0
@export var demand_curve: Curve  # 一天中的小时 vs 需求乘数

var customer_queue: Array[Customer] = []

func generate_customers(game_hour: float, delta_hours: float) -> void:
    var demand_mult := demand_curve.sample(game_hour / 24.0)
    var reputation_mult := Economy.resources["reputation"] / 50.0  # 100声誉 = 2倍顾客
    
    var customers_to_spawn := base_customers_per_hour * delta_hours * demand_mult * reputation_mult
    
    for i in int(customers_to_spawn):
        spawn_customer()

func spawn_customer() -> void:
    var customer := Customer.new()
    customer.patience = randf_range(30.0, 120.0)  # 离开前的秒数
    customer.spending_budget = randf_range(10.0, 100.0)
    customer_queue.append(customer)
```

---

## 反馈系统

### 视觉反馈

```gdscript
# 金钱飞向银行、资源流动等
class_name ResourceFlowVisualizer
extends Node

func show_income(amount: float, from: Vector2, to: Vector2) -> void:
    var coin := coin_scene.instantiate()
    coin.position = from
    add_child(coin)
    
    var tween := create_tween()
    tween.tween_property(coin, "position", to, 0.5)
    tween.tween_callback(coin.queue_free)
    
    var label := Label.new()
    label.text = "+$" + str(int(amount))
    label.position = from
    add_child(label)
    
    var label_tween := create_tween()
    label_tween.tween_property(label, "position:y", label.position.y - 30, 0.5)
    label_tween.parallel().tween_property(label, "modulate:a", 0.0, 0.5)
    label_tween.tween_callback(label.queue_free)
```

### 统计仪表板

```gdscript
class_name StatsDashboard
extends Control

@export var graph_history_hours := 24
var income_history: Array[float] = []
var expense_history: Array[float] = []

func record_financial_tick(income: float, expenses: float) -> void:
    income_history.append(income)
    expense_history.append(expenses)
    
    # 保留最后N个条目
    while income_history.size() > graph_history_hours:
        income_history.pop_front()
        expense_history.pop_front()
    
    queue_redraw()

func _draw() -> void:
    # 绘制收入/支出图表
    draw_line_graph(income_history, Color.GREEN)
    draw_line_graph(expense_history, Color.RED)
```

---

## 进度与解锁

```gdscript
class_name UnlockSystem
extends Node

var unlocks: Dictionary = {
    "basic_facility": true,
    "advanced_facility": false,
    "marketing": false,
    "automation": false
}

var unlock_conditions: Dictionary = {
    "advanced_facility": {"money_earned": 50000},
    "marketing": {"reputation": 70},
    "automation": {"workers_hired": 20}
}

var progress: Dictionary = {
    "money_earned": 0.0,
    "workers_hired": 0
}

func check_unlocks() -> Array[String]:
    var newly_unlocked: Array[String] = []
    
    for unlock in unlock_conditions:
        if unlocks[unlock]:
            continue  # 已解锁
        
        var conditions := unlock_conditions[unlock]
        var all_met := true
        
        for condition in conditions:
            if progress.get(condition, 0) < conditions[condition]:
                all_met = false
                break
        
        if all_met:
            unlocks[unlock] = true
            newly_unlocked.append(unlock)
    
    return newly_unlocked
```

---

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 经济太容易破坏 | 广泛平衡、软上限、收益递减 |
| 早期游戏无聊 | 前置有趣的决策、快速早期进度 |
| 信息过载 | 渐进式披露、可折叠UI面板 |
| 没有明确目标 | 里程碑、成就、场景 |
| 繁琐的微管理 | 自动化解锁、批处理操作 |

---

## Godot特定提示

1. **UI**: 广泛使用`Control`节点，`Tree`用于列表，`GraphEdit`用于连接
2. **性能**: 批处理实体，而不是每帧处理
3. **保存/加载**: 将所有游戏状态转换为Dictionary以便JSON序列化
4. **等距视图**: 使用正交投影的`Camera2D`


## 参考
- 主技能: [godot-master](../godot-master/SKILL.md)
