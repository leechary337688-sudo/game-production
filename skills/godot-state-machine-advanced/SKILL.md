---
name: godot-state-machine-advanced
description: "高级层级有限状态机（HSM）和pushdown automata的专家蓝图，用于复杂的AI/角色行为。涵盖状态堆栈、子状态、转换验证和状态上下文传递。当基本FSM不足或实现分层AI时使用。关键词：状态机、HSM、层级、pushdown automata、状态堆栈、FSM、AI行为。"
---

# 高级状态机

层级状态、状态堆栈和上下文传递定义了复杂行为管理。

## 可用脚本

### [hsm_logic_state.gd](scripts/hsm_logic_state.gd)
专家HSM基础类，具有状态堆栈管理和验证。

### [pushdown_automaton.gd](scripts/pushdown_automaton.gd)
基于堆栈的状态机，用于中断-恢复行为（暂停菜单、过场动画）。

> **强制要求**：在实现分层AI行为之前阅读hsm_logic_state.gd。

## 在高级状态机中切勿做

- **切勿在调用enter()之前忘记调用exit()** — 没有exit的转换？跳过先前状态清理 = 资源泄漏（计时器、补间）。始终先exit → enter。
- **切勿使用push_state()而不使用pop_state()** — 推送了100个中断状态？堆栈溢出 + 内存泄漏。每个推送都需要匹配的弹出。
- **切勿在转换期间修改状态** — 在exit()中调用transition_to()？重入转换 = 未定义行为。标记转换，在当前完成后执行。
- **切勿跳过状态验证** — transition_to("AttackState")但状态不存在？静默失败或崩溃。在转换前验证状态存在。
- **切勿忘记处理子状态** — 具有子状态的层级状态？父级update()必须调用current_child_state.update()以进行委托。
- **切勿在代码中使用字符串状态名称** — transition_to("Idel") typo = 静默失败。使用常量或枚举：transition_to(States.IDLE)。

---

```gdscript
# hierarchical_state.gd
class_name HierarchicalState
extends Node

signal transitioned(from_state: String, to_state: String)

var current_state: Node
var state_stack: Array[Node] = []

func  _ready() -> void:
    for child in get_children():
        child.state_machine = self
    
    if get_child_count() > 0:
        current_state = get_child(0)
        current_state.enter()

func transition_to(state_name: String) -> void:
    if not has_node(state_name):
        return
    
    var new_state := get_node(state_name)
    
    if current_state:
        current_state.exit()
    
    transitioned.emit(current_state.name if current_state else "", state_name)
    current_state = new_state
    current_state.enter()

func push_state(state_name: String) -> void:
    if current_state:
        state_stack.append(current_state)
        current_state.exit()
    
    transition_to(state_name)

func pop_state() -> void:
    if state_stack.is_empty():
        return
    
    var previous_state := state_stack.pop_back()
    transition_to(previous_state.name)
```

## 状态基类

```gdscript
# state.gd
class_name State
extends Node

var state_machine: HierarchicalState

func enter() -> void:
    pass

func exit() -> void:
    pass

func update(delta: float) -> void:
    pass

func physics_update(delta: float) -> void:
    pass

func handle_input(event: InputEvent) -> void:
    pass
```

## 最佳实践

1. **分离** - 每个文件一个状态
2. **信号** - 通信状态变化
3. **堆栈** - 使用推送/弹出进行中断

## 参考
- 相关：`godot-characterbody-2d`, `godot-animation-player`

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
