---
名称：godot-genre-rts
描述："用于实时战略游戏的专家蓝图，包括单位选择（拖拽框、Shift添加）、命令系统（移动、攻击、采集）、路径寻找（使用NavigationAgent2D的RVO避免）、战争迷雾（SubViewport遮罩着色器）、资源经济（采集/建造循环）和AI对手（行为树、效用AI）。适用于基地建设RTS或战术战斗游戏。触发关键词：RTS、单位选择、命令系统、战争迷雾、路径寻找_RVO、资源经济、命令队列。"
---

# 类型：实时战略（RTS）

RTS游戏的专家蓝图，平衡策略、微操和性能。

## 切勿做

- **切勿路径寻找抖动** — 单位无限互相推挤。启用RVO避免（NavigationAgent2D.avoidance_enabled with radius）。
- **切勿过度微操** — 自动化日常任务（自动攻击附近敌人、自动恢复采集后卸载）。
- **切勿在每个单位上使用_process** — 对于100+单位，使用中央UnitManager迭代器。节省大量函数调用开销。
- **切勿跳过命令排队** — 玩家期望Shift+点击来链式命令。存储Array[Command]并顺序处理。
- **切勿忘记战争迷雾** — 未访问区域应隐藏。使用SubViewport + 着色器遮罩以提高性能。
---

## 可用脚本

> **必须**：在实现相应模式前阅读适当的脚本。

### [rts_selection_manager.gd](scripts/rts_selection_manager.gd)
鼠标框选单位，支持Shift添加。3D单位的相机投影，命令发出支持队列（Shift+右键点击）。

---

## 核心循环
1.  **采集**：单位收集资源（黄金、木材等）。
2.  **建造**：构建基础建筑以解锁科技/单位。
3.  **训练**：生产多样化的军队单位。
4.  **命令**：实时战斗中的微操单位。
5.  **扩张**：确保地图控制和资源。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 控制 | `godot-input-handling`, `camera-rts` | 选择框、相机平移/缩放 |
| 2. 单位 | `navigation-server`, `state-machines` | 路径寻找、避免、状态（空闲/移动/攻击） |
| 3. 系统 | `fog-of-war`, `building-system` | 地图可见性、网格放置 |
| 4. AI | `behavior-trees`, `utility-ai` | 敌方指挥官逻辑 |
| 5. 优化 | `ui-minimap`, `godot-particles` | 战略概览、战斗反馈 |

## 架构概览

### 1. 选择管理器（单例或指挥官节点）
处理鼠标输入以选择单位。

```gdscript
# selection_manager.gd
extends Node2D

var selected_units: Array[Unit] = []
var drag_start: Vector2
var is_dragging: bool = false
@onready var selection_box: Panel = $SelectionBox

func _unhandled_input(event):
    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            start_selection(event.position)
        else:
            end_selection(event.position)
    elif event is InputEventMouseMotion and is_dragging:
        update_selection_box(event.position)

func end_selection(end_pos: Vector2):
    is_dragging = false
    selection_box.visible = false
    var rect = Rect2(drag_start, end_pos - drag_start).abs()
    
    if Input.is_key_pressed(KEY_SHIFT):
        # 添加到选择
        pass
    else:
        deselect_all()
        
    # 查询物理服务器中的单位在矩形内
    var query = PhysicsShapeQueryParameters2D.new()
    var shape = RectangleShape2D.new()
    shape.size = rect.size
    query.shape = shape
    query.transform = Transform2D(0, rect.get_center())
    # ... 执行查询并添加单位到selected_units
    
    for unit in selected_units:
        unit.set_selected(true)

func issue_command(target_position: Vector2):
    for unit in selected_units:
        unit.move_to(target_position)
```

### 2. 单位控制器（状态机）
单位需要稳健的状态管理来处理命令和自动攻击。

```gdscript
# unit.gd
extends CharacterBody2D
class_name Unit

enum State { IDLE, MOVE, ATTACK, HOLD }
var state: State = State.IDLE
var command_queue: Array[Command] = []

@onready var nav_agent: NavigationAgent2D = $NavigationAgent2D

func move_to(target: Vector2):
    nav_agent.target_position = target
    state = State.MOVE

func _physics_process(delta):
    if state == State.MOVE:
        if nav_agent.is_navigation_finished():
            state = State.IDLE
            return
            
        var next_pos = nav_agent.get_next_path_position()
        var direction = global_position.direction_to(next_pos)
        velocity = direction * speed
        move_and_slide()
```

### 3. 战争迷雾
一个系统来隐藏未访问区域。通常使用纹理和着色器实现。

*   **网格方法**：二维数组的“可见性”值。
*   **视口纹理**：一个`SubViewport`在黑色背景上绘制单位白圈。然后将此纹理用作全屏`ColorRect`覆盖层中的遮罩。

```gdshader
shader_type canvas_item;
uniform sampler2D visibility_texture; 
uniform vec4 fog_color : source_color;

void fragment() {
    float visibility = texture(visibility_texture, UV).r;
    COLOR = mix(fog_color, vec4(0,0,0,0), visibility);
}
```

## 关键机制实现

### 命令队列
允许玩家链式命令（Shift-点击）。
*   **实现**：将命令存储在`Array`中。当一个完成时，弹出下一个。
*   **视觉效果**：绘制线条显示排队路径。

### 资源采集
*   **节点**：`ResourceNode`（树/金矿）和`DropoffPoint`（城镇中心）。
*   **逻辑**：
    1.  移动到资源。
    2.  工作（计时器）。
    3.  移动到卸载点。
    4.  存入（全局经济更新）。
    5.  重复。

## 常见陷阱

1.  **路径寻找抖动**：单位无限互相推挤。**修复**：使用Godot的`NavigationAgent2D`内置的RVO（相互速度避免）（属性`avoidance_enabled`、`radius`）。
2.  **过多微操**：自动化日常任务（自动攻击附近敌人、自动采集行为）。
3.  **性能问题**：节点过多。**修复**：如果需要渲染数千单位，使用`MultiMeshInstance2D`，并对大批单位使用`Server`节点运行逻辑而非单独脚本。

## Godot特定提示

*   **避免**：`NavigationAgent2D`有内置的RVO避免。确保调用`set_velocity()`并使用`velocity_computed`信号进行实际移动！
*   **服务器架构**：对于100+单位，不要在每单位上使用`_process`。使用中央`UnitManager`迭代活动单位以节省函数调用开销。
*   **组**：大量使用组（`Units`、`Buildings`、`Resources`）以便于选择过滤器。


## 参考
- 主技能： [godot-master](../godot-master/SKILL.md)
