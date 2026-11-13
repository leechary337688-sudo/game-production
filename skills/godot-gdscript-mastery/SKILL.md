---
name: Godot GDScript精通
description: "专家级GDScript最佳实践，包括静态类型（var x: int, func returns void）、信号架构（signal up call down）、唯一节点访问（%NodeName, @onready）、脚本结构（extends, class_name, signals, exports, methods）和性能模式（dict.get with defaults, avoid get_node in loops）。用于代码审查、重构或建立项目标准。触发关键词：static_typing, signal_architecture, unique_nodes, @onready, class_name, signal_up_call_down, gdscript_style_guide。"
---

# GDScript精通

专家指导如何编写性能优化、可维护的GDScript，遵循官方Godot标准。

## 永远不要做的事

- **永远不要在性能关键代码中使用动态类型** — `var x = 5` 比 `var x: int = 5` 慢20-40%。所有变量都应指定类型。
- **永远不要从子节点调用父节点的方法（“向上调用”）** — 使用“信号向上，调用向下”模式。子节点应发射信号，父节点调用子节点方法。
- **永远不要在`_process()`或`_physics_process()`中使用`get_node()`** — 使用缓存如`@onready var sprite = $Sprite`。get_node()在循环中较慢。
- **永远不要在没有默认值的情况下访问字典** — `dict["key"]` 如果键缺失会崩溃。使用`dict.get("key", default)`以确保安全。
- **永远不要省略可重用脚本的`class_name`** — 没有`class_name`，不能使用类型提示（`var item: Item`）。使代码难以维护。
---

## 可用脚本

> **必须的**：在实现相应模式前阅读适当的脚本。

### [advanced_lambdas.gd](scripts/advanced_lambdas.gd)
GDScript中的高阶函数：使用lambda的filter/map、返回Callables的工厂函数、类型数组的Godot组合、以及静态实用方法。

### [type_checker.gd](scripts/type_checker.gd)
扫描代码库以查找缺失的类型提示。在发布前运行以强制静态类型标准。

### [performance_analyzer.gd](scripts/performance_analyzer.gd)
检测性能反模式：循环中的get_node()、字符串拼接、不安全字典访问。

### [signal_architecture_validator.gd](scripts/signal_architecture_validator.gd)
强制“信号向上，调用向下”模式。检测get_parent()调用和未类型化的信号。

> **不要加载** performance_analyzer.gd，除非正在分析热路径或优化帧率。


---

## 核心指导原则

### 1. 强类型化
始终使用静态类型。它提高性能并早期捕获错误。
**规则**：优先使用`var x: int = 5` 而不是 `var x = 5`。
**规则**：始终为函数指定返回类型：`func _ready() -> void:`。

### 2. 信号架构
- **在`_ready()`中连接**：最好在代码中连接信号以保持可见性，而不仅仅在编辑器中。
- **类型化信号**：定义带有类型的信号：`signal item_collected(item: ItemResource)`。
- **模式**：“信号向上，调用向下”。子节点永远不应调用父节点方法；它们应发射信号。

### 3. 节点访问
- **唯一名称**：使用`%UniqueNames`访问对脚本逻辑关键的节点。
- **Onready覆盖**：优先使用`@onready var sprite = %Sprite2D` 而不是在每个函数中调用`get_node()`。

### 4. 代码结构
遵循标准Godot脚本布局：
1. `extends`
2. `class_name`
3. `signals` / `enums` / `constants`
4. `@export` / `@onready` / `properties`
5. `_init()` / `_ready()` / `_process()`
6. 公共方法
7. 私有方法（前缀为`_`）

## 常见“架构师”模式

### 安全的字典查找
如果不100%确定键存在，避免`dict["key"]`。使用`dict.get("key", default)`。

### 场景唯一节点
构建复杂UI时，始终在关键节点（标签、按钮）上切换“访问为场景唯一名称”，并通过`%Name`访问它们。

## 参考
- 官方文档：`tutorials/scripting/gdscript/gdscript_styleguide.rst`
- 官方文档：`tutorials/best_practices/logic_preferences.rst`


### 相关
- 精通技能：[godot-master](../godot-master/SKILL.md)
