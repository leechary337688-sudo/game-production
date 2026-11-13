---
name: godot-signal-architecture
description: "使用\"信号向上，调用向下\"模式的信号驱动架构专家蓝图，实现松耦合。涵盖类型化信号、信号链、一次性连接和AutoLoad事件总线。适用于实现事件系统或解耦节点。关键词：信号、发射、连接、CONNECT_ONE_SHOT、CONNECT_REFERENCE_COUNTED、事件总线、AutoLoad、解耦。"
---

# 信号架构

信号向上/调用向下模式、类型化信号和事件总线定义了松耦合、可维护的架构。

## 可用脚本

### [global_event_bus.gd](scripts/global_event_bus.gd)
专家级AutoLoad事件总线，具有类型化信号和连接管理。

### [signal_debugger.gd](scripts/signal_debugger.gd)
运行时信号连接分析器。显示场景层次结构中的所有连接。

### [signal_spy.gd](scripts/signal_spy.gd)
测试实用工具，用于观察信号发射，带有计数跟踪和历史记录。

> **强制要求 - 对于事件总线**：在实现跨场景通信之前，阅读global_event_bus.gd。


## 信号架构中绝不做的事

- **绝不创建循环信号依赖** — A向B发信号，B向A回发信号？无限循环 + 堆栈溢出。使用中介（父节点或AutoLoad）来打破循环。
- **绝不跳过信号类型化** — `signal moved` 没有类型？没有自动补全或类型安全。使用 `signal moved(direction: Vector2)` 以获得编辑器支持。
- **绝不忘断开信号** — 节点释放但信号仍连接？“尝试调用空实例”错误。在 `_exit_tree()` 中断开连接或使用 `CONNECT_REFERENCE_COUNTED`。
- **绝不在_ready()中为动态节点连接信号** — 敌人在关卡加载后生成？信号未连接。在实例化时连接或使用组 + `await` 模式。
- **绝不使用信号进行父→子通信** — 父节点向子节点发信号破坏封装。直接向下调用：`child.method()`。保留信号用于子→父通信。
- **绝不发射带副作用的信号** — `died.emit()` 在内部调用 `queue_free()`？监听器在节点释放前无法响应。先发射信号，然后清理。
- **绝不使用基于字符串的信号名称** — `connect(\"heath_chnaged\", ...)` 拼写错误 = 静默失败。使用直接引用：`player.health_changed.connect(...)`。

---

**使用信号用于：**
- UI按钮按下 → 游戏逻辑
- 玩家死亡 → 游戏结束屏幕
- 物品收集 → 库存更新
- 敌人击杀 → 分数更新
- 通过AutoLoad进行跨场景通信

**使用直接调用用于：**
- 父节点控制子节点行为
- 访问子节点属性
- 简单的本地交互

## 实现模式

### 模式1：定义类型化信号

```gdscript
extends CharacterBody2D

# ✅ 好 - 类型化信号（Godot 4.x）
signal health_changed(new_health: int, max_health: int)
signal died()
signal item_collected(item_name: String, item_type: int)

# ❌ 坏 - 非类型化信号
signal health_changed
signal died
```

### 模式2：在状态变化时发射信号

```gdscript
# player.gd
extends CharacterBody2D

signal health_changed(current: int, maximum: int)
signal died()

var health: int = 100:
    set(value):
        health = clamp(value, 0, max_health)
        health_changed.emit(health, max_health)
        if health <= 0:
            died.emit()

var max_health: int = 100

func take_damage(amount: int) -> void:
    health -= amount  # 触发setter，发射信号
```

### 模式3：在父节点中连接信号

```gdscript
# game.gd（父节点）
extends Node2D

@onready var player: CharacterBody2D = $Player
@onready var ui: Control = $UI

func _ready() -> void:
    # 连接子节点信号
    player.health_changed.connect(_on_player_health_changed)
    player.died.connect(_on_player_died)

func _on_player_health_changed(current: int, maximum: int) -> void:
    # 向下调用到UI
    ui.update_health_bar(current, maximum)

func _on_player_died() -> void:
    # 编排游戏结束
    ui.show_game_over()
    get_tree().paused = true
```

### 模式4：通过AutoLoad的全局信号

用于跨场景通信：

```gdscript
# events.gd（AutoLoad）
extends Node

signal level_completed(level_number: int)
signal player_spawned(player: Node2D)
signal boss_defeated(boss_name: String)

# 任何脚本都可以发射：
Events.level_completed.emit(3)

# 任何脚本都可以监听：
Events.level_completed.connect(_on_level_completed)
```

## 高级模式

### 模式5：信号链

```gdscript
# enemy.gd
signal died(score_value: int)

func _on_health_depleted() -> void:
    died.emit(100)
    queue_free()

# combat_manager.gd
func _ready() -> void:
    for enemy in get_tree().get_nodes_in_group(\"enemies\"):
        enemy.died.connect(_on_enemy_died)

func _on_enemy_died(score_value: int) -> void:
    GameManager.add_score(score_value)
    Events.enemy_killed.emit()
```

### 模式6：一次性连接

用于单次使用的信号连接：

```gdscript
# 使用CONNECT_ONE_SHOT标志连接
timer.timeout.connect(_on_timer_timeout, CONNECT_ONE_SHOT)

func _on_timer_timeout() -> void:
    print(\"这只会触发一次\")
    # 连接自动移除
```

### 模式7：自定义信号参数

```gdscript
# item.gd
signal picked_up(item_data: Dictionary)

func _on_player_enter() -> void:
    picked_up.emit({
        \"name\": item_name,
        \"type\": item_type,
        \"value\": item_value,
        \"icon\": item_icon
    })

# inventory.gd
func _on_item_picked_up(item_data: Dictionary) -> void:
    add_item(
        item_data.name,
        item_data.type,
        item_data.value
    )
```

## 最佳实践

### 1. 描述性信号名称

```gdscript
# ✅ 好
signal button_pressed()
signal enemy_defeated(enemy_type: String)
signal animation_finished(animation_name: String)

# ❌ 坏
signal pressed()
signal done()
signal finished()
```

### 2. 避免循环依赖

```gdscript
# ❌ 坏：A向B发信号，B向A回发信号
# A.gd
signal data_requested
func _ready():
    B.data_ready.connect(_on_data_ready)
    data_requested.emit()

# B.gd
signal data_ready
func _ready():
    A.data_requested.connect(_on_data_requested)

# ✅ 好：使用中介（父节点或AutoLoad）
# Parent.gd
func _ready():
    A.data_requested.connect(_on_A_data_requested)
    B.data_ready.connect(_on_B_data_ready)
```

### 3. 当节点释放时断开信号

```gdscript
func _ready() -> void:
    player.died.connect(_on_player_died)

func _exit_tree() -> void:
    if player and player.died.is_connected(_on_player_died):
        player.died.disconnect(_on_player_died)
```

**或使用自动清理：**
```gdscript
# 当此节点释放时，信号自动断开
player.died.connect(_on_player_died, CONNECT_REFERENCE_COUNTED)
```

### 4. 分组相关信号

```gdscript
# ✅ 好的组织
# 战斗信号
signal health_changed(current: int, max: int)
signal died()
signal respawned()

# 移动信号
signal jumped()
signal landed()
signal direction_changed(direction: Vector2)

# 库存信号
signal item_added(item: Dictionary)
signal item_removed(item: Dictionary)
signal inventory_full()
```

## 测试信号

```gdscript
func test_health_signal() -> void:
    var signal_emitted := false
    var received_health := 0
    
    player.health_changed.connect(
        func(current: int, _max: int):
            signal_emitted = true
            received_health = current
    )
    
    player.health = 50
    assert(signal_emitted, \"信号未发射\")
    assert(received_health == 50, \"健康值不正确\")
```

## 常见陷阱

**问题**：信号未触发
- **检查**：连接时信号拼写是否正确？
- **检查**：发射代码路径是否实际执行？
- **检查**：在`emit()`前使用`print()`验证

**问题**：信号触发多次
- **原因**：多个连接到同一信号
- **解决方案**：检查连接或使用`CONNECT_ONE_SHOT`

**问题**：“尝试在空实例上调用函数”
- **原因**：节点已释放但信号仍连接
- **解决方案**：在`_exit_tree()`中断开或使用`CONNECT_REFERENCE_COUNTED`

## 参考
- [Godot文档：信号](https://docs.godotengine.org/en/stable/getting_started/step_by_step/signals.html)
- [最佳实践：信号向上，调用向下](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)


### 相关
- 主要技能：[godot-master](../godot-master/SKILL.md)
