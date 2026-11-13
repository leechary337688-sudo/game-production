---
name: godot-server-architecture
description: "使用RID实现低级服务器访问（RenderingServer、PhysicsServer2D/3D、NavigationServer）以实现最高性能的专家蓝图。绕过场景树开销，用于程序生成、粒子系统和体素引擎。在节点太慢或管理数千个对象时使用。关键词：RenderingServer、PhysicsServer、NavigationServer、RID、canvas_item、body_create、低级、性能。"
---

# 服务器架构

基于RID的服务器API、直接渲染/物理访问和对象池定义最高性能模式。

## 可用脚本

### [headless_manager.gd](scripts/headless_manager.gd)
用于专用服务器生命周期管理、参数解析和无头模式优化的管理器。

### [rid_performance_server.gd](scripts/rid_performance_server.gd)
具有RID生命周期管理和批处理操作的专业服务器包装器。

## 服务器架构中绝对不要做的事情

- **绝对不要忘记释放RIDs** — `RenderingServer.canvas_item_create()` 后不释放？内存泄漏（垃圾回收不跟踪RIDs）。完成后必须调用 `canvas_item_free(rid)`。
- **绝对不要将服务器API与节点用于同一对象** — 为同一实体创建RID体和CharacterBody2D？冲突并导致双重模拟成本。选择一种方法。
- **绝对不要使用服务器进行原型设计** — 调试服务器代码很痛苦（没有检查器、print_tree或可视化工具）。先使用节点，然后优化到服务器。
- **绝对不要跳过RID验证** — 调用 `body_set_state(invalid_rid, ...)` = 崩溃。使用 `RID.is_valid(rid)` 或在数组/字典中跟踪RIDs。
- **绝对不要在没有首先分析的情况下使用服务器** — 过早优化。在Godot 4中，节点可以很好地处理10k+对象。首先分析，然后用服务器替换瓶颈。
- **绝对不要忘记设置形状变换** — `PhysicsServer2D.body_add_shape(body, shape)` 没有变换？形状偏移在(0,0)。通过 `body_set_shape_transform()` 设置变换。
- **绝对不要使用RenderingServer处理UI** — 通过canvas_item_create()创建UI元素？没有自动层、输入或主题。使用Control节点处理UI。

---

无需节点的直接渲染访问。

```gdscript
# 创建画布项（2D精灵等效）
var canvas_item := RenderingServer.canvas_item_create()
RenderingServer.canvas_item_set_parent(canvas_item, get_canvas_item())

# 绘制纹理
var texture_rid := load("res://icon.png").get_rid()
RenderingServer.canvas_item_add_texture_rect(
    canvas_item,
    Rect2(0, 0, 64, 64),
    texture_rid
)
```

## PhysicsServer2D

无需节点创建物理体。

```gdscript
# 创建体
var body_rid := PhysicsServer2D.body_create()
PhysicsServer2D.body_set_mode(body_rid, PhysicsServer2D.BODY_MODE_RIGID)

# 创建形状
var shape_rid := PhysicsServer2D.circle_shape_create()
PhysicsServer2D.shape_set_data(shape_rid, 16.0)  # 半径

# 将形状分配给体
PhysicsServer2D.body_add_shape(body_rid, shape_rid)
```

## 何时使用服务器

**使用服务器用于：**
- 程序生成（数千个对象）
- 粒子系统
- 体素引擎
- 自定义渲染

**使用节点用于：**
- 常规游戏对象
- UI
- 原型设计

## 参考
- [Godot文档：使用服务器](https://docs.godotengine.org/en/stable/tutorials/performance/using_servers.html)


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
