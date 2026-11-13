---
名称: godot-turn-system
描述: "回合制战斗的专家蓝图，包含回合顺序、行动点、阶段管理和时间轴系统，适用于策略/RPG游戏。覆盖速度基础的主动性、中断和同时回合。在实现回合制战斗或战术系统时使用。关键词回合制、主动性、行动点、阶段、回合、回合顺序、战斗。"
---

# 回合系统

回合顺序计算、行动点、阶段管理和时间轴系统定义回合制战斗。

## 可用脚本

### [active_time_battle.gd](scripts/active_time_battle.gd)
活动时间战斗（ATB）系统的框架，支持异步动作。

### [timeline_turn_manager.gd](scripts/timeline_turn_manager.gd)
专家时间轴基础的回合管理器，包含中断和同时动作。

## 在回合系统中绝不要做

- **绝不要每个动作后重新计算回合顺序** — 每次移动后排序50个战斗者？O(n log n) × 动作 = 延迟。每回合计算一次，仅在状态变化时更新。
- **绝不要在没有确定性的情况下使用速度平局** — 两个单位相同速度，随机顺序？不可复现的回放。使用次要状态（ID、位置等）打破平局。
- **绝不要忘记验证动作成本** — 允许动作而不检查点数？负AP = 漏洞。总是在扣除前使用 `if can_perform_action(cost)`。
- **绝不要硬编码阶段过渡** — `if phase == 0: phase = 1` 对于10个阶段？不可维护。使用枚举 + 匹配或阶段处理程序数组。
- **绝不要跳过联网游戏的回合超时** — 永远等待玩家输入？虐待漏洞。总是实现回合定时器并附带默认动作。
- **绝不要在清理前发出 turn_ended 信号** — 信号监听器开始下一回合，但前一回合未清理？状态损坏。先清理，然后发出信号。

---

```gdscript
# turn_manager.gd (自动加载)
extends Node

signal turn_started(战斗者: Node)
signal turn_ended(战斗者: Node)
signal round_ended

var combatants: Array[Node] = []
var turn_order: Array[Node] = []
var current_turn_index: int = 0

func start_combat(参与者: Array[Node]) -> void:
    combatants = participants
    calculate_turn_order()
    start_next_turn()

func calculate_turn_order() -> void:
    turn_order = combatants.duplicate()
    turn_order.sort_custom(func(a, b): return a.speed > b.speed)

func start_next_turn() -> void:
    if current_turn_index >= turn_order.size():
        current_turn_index = 0
        round_ended.emit()
        calculate_turn_order()  # 每回合重新计算
    
    var current := turn_order[current_turn_index]
    turn_started.emit(current)

func end_turn() -> void:
    var current := turn_order[current_turn_index]
    turn_ended.emit(current)
    current_turn_index += 1
    start_next_turn()
```

## 行动点系统

```gdscript
# combatant.gd
extends Node

@export var max_action_points: int = 3
var current_action_points: int = 3

func start_turn() -> void:
    current_action_points = max_action_points

func can_perform_action(cost: int) -> bool:
    return current_action_points >= cost

func perform_action(cost: int) -> bool:
    if not can_perform_action(cost):
        return false
    
    current_action_points -= cost
    return true
```

## 回合阶段

```gdscript
enum Phase { DRAW, MAIN, END }

var current_phase: Phase = Phase.DRAW

func advance_phase() -> void:
    match current_phase:
        Phase.DRAW:
            current_phase = Phase.MAIN
        Phase.MAIN:
            current_phase = Phase.END
        Phase.END:
            TurnManager.end_turn()
            current_phase = Phase.DRAW
```

## 最佳实践

1. **速度基础** - 主动性决定顺序
2. **行动点** - 限制每回合的行动
3. **超时** - 为在线游戏添加回合定时器

## 参考
- 相关: `godot-combat-system`, `godot-rpg-stats`

### 相关
- 主要技能: [godot-master](../godot-master/SKILL.md)
