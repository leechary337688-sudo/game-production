---
name: godot-master
description: "Godot 4.x专业游戏与应用开发的整合专家库。通过架构工作流程、反模式目录、性能预算和服务器API模式，协调86个专门蓝图。使用场景：(1) 启动新Godot项目，(2) 设计游戏或应用架构，(3) 构建实体/组件系统，(4) 调试性能或物理问题，(5) 选择2D/3D方法，(6) 实现多人游戏，(7) 优化绘制调用或脚本时间，(8) 跨平台移植。所有Godot开发任务的主要入口点。"
---

# Godot大师：首席架构师知识中心

每个部分都通过关注**知识差异**来赚取代币——即Claude已知知识与从实际产品中获得的资深Godot工程师知识之间的差距。

---

## 🧠 第一部分：专家思维框架

### "谁拥有什么？" —— 架构理智检查
在编写任何系统之前，为每个状态片段回答这三个问题：
- **谁拥有数据？**（`StatsComponent`拥有健康值，而不是`CombatSystem`）
- **谁被允许更改它？**（只有所有者通过像`apply_damage()`这样的公共方法）
- **谁需要知道它已更改？**（任何监听`health_changed`信号的人）

如果你不能为每个状态变量回答所有三个问题，你的架构就有耦合问题。这不是OOP封装——这是Godot特定的，因为**信号系统是执行机制**，而不是访问修饰符。

### Godot "分层蛋糕"
将每个功能组织成四层。信号向上传播，绝不向下：
```
┌──────────────────────────────┐
│  表示层（UI / VFX）         │  ← 监听信号，绝不拥有数据
├──────────────────────────────┤
│  逻辑层（状态机）           │  ← 协调转换，查询数据
├──────────────────────────────┤
│  数据层（资源 / .tres）     │  ← 单一真相源，可序列化
├──────────────────────────────┤
│  基础设施层（自动加载）      │  ← 信号总线，保存管理器，音频总线
└──────────────────────────────┘
```
**关键规则**：表示层绝不能直接修改数据层。基础设施层仅通过信号通信。如果一个`Label`节点调用`player.health -= 1`，架构就坏了。

### 信号总线分层架构
- **全局总线（自动加载）**：仅用于生命周期事件（`match_started`，`player_died`，`settings_changed`）。调试蔓延是成本——限制事件到<15个。
- **作用域功能总线**：每个功能文件夹有自己的总线（例如，`CombatBus`仅用于战斗节点）。这是可扩展的折衷方案。
- **直接信号**：单个场景内的父-子通信。绝不跨场景边界。

---

## 🧭 第二部分：架构决策框架

### 主决策矩阵

| 场景 | 策略 | **强制**技能链 | 权衡 |
| :--- | :--- | :--- | :--- |
| **快速原型** | 事件驱动单例 | **阅读**：[基础](references/godot-project-foundations.md) → [自动加载](references/godot-autoload-architecture.md)。**不要加载**类型或平台参考。 | 快速启动，面条代码风险 |
| **复杂RPG** | 组件驱动 | **阅读**：[组合](references/godot-composition.md) → [状态](references/godot-state-machine-advanced.md) → [RPG统计](references/godot-rpg-stats.md)。**不要加载**多人游戏或平台参考。 | 重设置，无限扩展 |
| **大规模开放世界** | 资源流 | **阅读**：[开放世界](references/godot-genre-open-world.md) → [保存/加载](references/godot-save-load-systems.md)。同时加载[性能](references/godot-performance-optimization.md)。 | 复杂I/O，超过10K单位的浮点精度抖动 |
| **服务器认证多人** | 确定性 | **阅读**：[服务器架构](references/godot-server-architecture.md) → [多人游戏](references/godot-multiplayer-networking.md)。**不要加载**单人游戏类型参考。 | 高延迟，反作弊安全 |
| **移动/网页移植** | 自适应响应 | **阅读**：[UI容器](references/godot-ui-containers.md) → [适应桌面→移动](references/godot-adapt-desktop-to-mobile.md) → [平台移动](references/godot-platform-mobile.md)。 | UI复杂性，广泛覆盖 |
| **应用 / 工具** | 应用组合 | **阅读**：[应用组合](references/godot-composition-apps.md) → [主题](references/godot-ui-theming.md)。**不要加载**游戏特定参考。 | 不同于游戏的范式 |
| **浪漫 / 约会模拟** | 情感经济 | **阅读**：[浪漫](references/romance.md) → [对话](references/godot-dialogue-system.md) → [UI富文本](references/godot-ui-rich-text.md)。 | 高UI/叙事密度 |
| **秘密 / 彩蛋** | 故意混淆 | **阅读**：[秘密](references/mechanic-secrets.md) → [持久性](references/godot-save-load-systems.md)。 | 社区参与，调试风险 |
| **收集任务** | 搜寻逻辑 | **阅读**：[收集](references/game-loop-collection.md) → [Marker3D放置](references/godot-3d-world-building.md)。 | 玩家留存，探索驱动力 |
| **季节性事件** | 运行时注入 | **阅读**：[复活节主题](references/theme-easter.md) → [材质交换](references/godot-3d-materials.md)。 | 快速品牌化，无资源污染 |
| **魂系死亡率** | 风险奖励复活 | **阅读**：[复活/尸体跑](references/mechanic-revival.md) → [物理3D](references/godot-physics-3d.md)。 | 高紧张感，玩家挫败风险 |

### "何时不使用节点"决策
最具影响力的专家独有决策之一。Godot文档明确说"避免对所有事情使用节点"：

| 类型 | 何时使用 | 成本 | 专家用例 |
| :--- | :--- | :--- | :--- |
| **`Object`** | 自定义数据结构，手动内存管理 | 最轻。必须手动调用`.free()`。 | 自定义空间哈希映射，ECS类数据存储 |
| **`RefCounted`** | 瞬态数据包，自动删除的逻辑对象 | 当没有剩余引用时自动删除。 | `DamageRequest`，`PathQuery`，`AbilityEffect` — 不需要场景树的逻辑包 |
| **`Resource`** | 可序列化数据，支持检查器 | 比RefCounted稍重。处理`.tres` I/O。 | `ItemData`，`EnemyStats`，`DialogueLine` — 任何设计者应在检查器中编辑的数据 |
| **`Node`** | 需要`_process`/`_physics_process`，需要存在于场景树中 | 最重——每个节点的SceneTree开销。 | 仅用于需要每帧更新或空间变换的实体 |

**专家模式**：对所有逻辑包和数据容器使用`RefCounted`子类。为必须存在于空间树中的事物保留`Node`。这为复杂系统减半场景树开销。

---

## 🔧 第三部分：核心工作流程

### 工作流程1：专业脚手架
*从空项目到生产就绪容器。*

**强制——阅读整个文件**：[基础](references/godot-project-foundations.md)
1. 按**功能**组织（`/features/player/`，`/features/combat/`），而不是按类类型。一个`player/`文件夹包含玩家的场景、脚本、资源和测试。
2. **阅读**：[信号架构](references/godot-signal-architecture.md) — 创建`GlobalSignalBus`自动加载，事件<15个。
3. **阅读**：[GDScript精通](references/godot-gdscript-mastery.md) — 在项目设置 → GDScript → 调试中启用`untyped_declaration`警告。
4. 应用**[项目模板](references/godot-project-templates.md)** 用于基础`.gitignore`、导出预设和输入映射。
5. 使用**[MCP场景构建器](references/godot-mcp-scene-builder.md)** 如果可用，以程序化生成场景层次结构。
**不要加载** 战斗、多人游戏、类型或平台参考在脚手架期间。

### 工作流程2：实体编排
*构建模块化、可测试的角色。*

**强制链——阅读所有**：[组合](references/godot-composition.md) → [状态机](references/godot-state-machine-advanced.md) → [CharacterBody2D](references/godot-characterbody-2d.md) 或 [物理3D](references/godot-physics-3d.md) → [动画树](references/godot-animation-tree-mastery.md)
**不要加载** UI、音频或保存/加载参考用于实体工作。

- 状态机查询`InputComponent`，绝不直接处理输入。这允许AI/玩家交换零重构。
- 状态机仅处理转换。逻辑属于组件。`MoveState`告诉`MoveComponent`行动，而不是反过来。
- 每个实体必须通过**F6测试**：按“运行当前场景”（F6）必须工作而不崩溃。如果崩溃，你的实体有场景外部依赖。

### 工作流程3：数据驱动系统
*通过资源连接战斗、库存、统计。*

**强制链——阅读所有**：[资源模式](references/godot-resource-data-patterns.md) → [RPG统计](references/godot-rpg-stats.md) → [战斗](references/godot-combat-system.md) → [库存](references/godot-inventory-system.md)

- 创建一个`ItemData.gd`扩展`Resource`。实例化为100个`.tres`文件而不是100个脚本。
- HUD绝不直接引用玩家。它监听信号总线上的`player_health_changed`。
- 在所有`@export Resource`变量上启用“局部到场景”，或在`_ready()`中调用`resource.duplicate()`。不这样做是第8部分的Bug #1。

### 工作流程4：持久性管道
**强制**：[自动加载架构](references/godot-autoload-architecture.md) → [保存/加载](references/godot-save-load-systems.md) → [场景管理](references/godot-scene-management.md)

- 使用字典映射序列化。旧保存文件在添加新字段时绝不能损坏——使用`.get("key", default_value)`。
- 对于程序化世界：保存**种子**加上修改的**增量列表**，而不是整个地图。一个100MB的世界变成50KB的保存。

### 工作流程5：性能优化
**强制**：[调试/性能分析](references/godot-debugging-profiling.md) → [性能优化](references/godot-performance-optimization.md)

**诊断优先方法**（绝不盲目优化）：
1. **高脚本时间** → 使用内置性能分析器分析。检查是否在数百个节点上调用`_process`。移动到单管理器模式或服务器API（见第6部分）。
2. **高绘制调用** → 对重复几何使用`MultiMeshInstance`。用ORM纹理批处理材质。
3. **物理卡顿** → 简化碰撞到原始形状。加载[2D物理](references/godot-2d-physics.md)或[3D物理](references/godot-physics-3d.md)。检查是否使用`_process`代替`_physics_process`进行移动。
4. **VRAM过用** → 将纹理切换到VRAM压缩（桌面用BPTC/S3TC，移动用ETC2）。绝不发布原始PNG。
5. **间歇帧尖峰** → 通常是GC传递、同步`load()`或NavigationServer重新计算。使用`ResourceLoader.load_threaded_request()`。

### 工作流程6：跨平台适应
**强制**：[输入处理](references/godot-input-handling.md) → [适应桌面→移动](references/godot-adapt-desktop-to-mobile.md) → [平台移动](references/godot-platform-mobile.md)
**也阅读**：[平台桌面](references/godot-platform-desktop.md)、[平台网页](references/godot-platform-web.md)、[平台控制台](references/godot-platform-console.md)、[平台VR](references/godot-platform-vr.md) 根据需要。

- 使用一个`InputManager`自动加载，将所有输入类型转换为标准化操作。绝不直接读取`Input.is_key_pressed()`——它阻止控制器和触摸支持。
- 移动触摸目标：最小44px物理大小。使用`MarginContainer`和Safe Area逻辑用于缺口/切割设备。
- 网页导出：Godot的`AudioServer`在首次播放前需要用户交互（浏览器策略）。用“点击开始”屏幕处理。

### 工作流程7：程序化生成
**强制**：[程序化生成](references/godot-procedural-generation.md) → [Tilemap精通](references/godot-tilemap-mastery.md) 或 [3D世界构建](references/godot-3d-world-building.md) → [导航](references/godot-navigation-pathfinding.md)

- 始终使用具有固定`seed`的`FastNoiseLite`资源进行确定性生成。
- 绝不主线程上烘焙NavMesh。使用`NavigationServer3D.parse_source_geometry_data()` + `NavigationServer3D.bake_from_source_geometry_data_async()`。
- 对于无限世界：区块加载必须在后台线程使用`WorkerThreadPool`。在树外构建场景区块，然后在主线程上`add_child.call_deferred()`。

### 工作流程8：多人游戏架构
**强制——阅读所有**：[多人游戏网络](references/godot-multiplayer-networking.md) → [服务器架构](references/godot-server-architecture.md) → [适应单→多](references/godot-adapt-single-to-multiplayer.md)
**不要加载** 单人游戏类型蓝图。

- 客户端发送输入，服务器计算结果。客户端绝不决定伤害、位置增量或库存变化。
- 使用客户端预测与服务器协调：本地预测，从服务器快照纠正。隐藏高达~150ms的延迟。
- `MultiplayerSpawner`在Godot 4中处理复制。每个场景配置它，而不是全局。

### 工作流程9：高级UI/UX
**强制**：[UI主题](references/godot-ui-theming.md) → [UI容器](references/godot-ui-containers.md) → [补间](references/godot-tweening.md) → [富文本](references/godot-ui-rich-text.md)

- 绝不在检查器中覆盖颜色。创建一个`.theme`资源作为全局皮肤的单真相源。
- 每个交互元素应有微动画：按钮上的`Tween`缩放脉冲，伤害数字上的`RichTextEffect`，面板转换上的`AnimationPlayer`。
- 使用`Control.FOCUS_MODE_ALL`并测试完整的键盘/游戏手柄导航。不可访问的UI阻止控制台认证。

### 工作流程10：图形与氛围
**强制**：[3D照明](references/godot-3d-lighting.md) → [3D材质](references/godot-3d-materials.md) → [着色器基础](references/godot-shaders-basics.md) → [粒子](references/godot-particles.md)

- 使用`GPUParticles3D`用于环境效果（雨、雾、火）。仅当脚本必须读取/写入单个粒子位置时使用`CPUParticles`。
- 始终手动设置GPU粒子的`visibility_aabb`。自动计算的AABB经常错误，导致发射器离屏时粒子消失。
- 对于风格化外观：使用带有`screen_texture`的`CanvasItem`着色器用于2D后处理。在3D中，使用带有自定义`Environment`资源的`WorldEnvironment`。
- `ReflectionProbe` vs `VoxelGI` vs `SDFGI`：探针便宜/静态，VoxelGI中等/烘焙，SDFGI昂贵/动态。根据你的平台预算选择（见第5部分）。

---

## 🚫 第四部分：专家绝不列表

每个规则包括**非显而易见的原因**——只有发货经验教的东西。

1. **绝不使用`get_tree().root.get_node("...")`** — 绝对路径在ANY祖先重命名或重新父化时中断。使用`%UniqueNames`、`@export NodePath`或基于信号的发现。
2. **绝不使用`load()`在循环或`_process`中** — 同步磁盘读取阻塞整个主线程。对小资产使用脚本顶部的`preload()`，对大资产使用`ResourceLoader.load_threaded_request()`。
3. **绝不`queue_free()`当外部引用存在时** — 持有引用的父节点或数组将获得“已删除对象”错误。在`_exit_tree()`中清理引用，并在释放前设置为`null`。
4. **绝不将游戏逻辑放入`_draw()`** — `_draw()`在渲染线程上调用。突变游戏状态导致与`_physics_process`的竞争条件。
5. **绝不使用`Area2D`用于1000+重叠对象** — 每个重叠检查有O(n²)宽相成本。对弹幕模式使用`ShapeCast2D`、`PhysicsDirectSpaceState2D.intersect_shape()`或服务器API。
6. **绝不变更外部状态从组件** — 如果`HealthComponent`调用`$HUD.update_bar()`，删除HUD会崩溃游戏。组件发出信号；监听器决定如何响应。
7. **绝不使用`await`在`_physics_process`中** — `await`产生执行，意味着物理步骤跳过帧。将异步操作移动到由信号触发的单独方法。
8. **绝不使用`String`键在热路径字典查找中** — 字符串哈希是O(n)。对O(1)指针比较使用`StringName`（`&"key"`），或整数枚举。
9. **绝不存储`Callable`引用到已释放对象** — 静默崩溃或抛出错误。在`_exit_tree()`中断开信号或使用`CONNECT_ONE_SHOT`。
10. **绝不使用`_process`用于1000+实体** — 每个`_process`调用有每个节点的SceneTree开销。使用单个`Manager._process`迭代数据结构数组（数据导向模式），或直接使用服务器API。
11. **绝不使用`Tween`在可能被释放的节点上** — 如果节点在Tween运行时`queue_free()`，它会错误。在`_exit_tree()`中杀死补间，或绑定到SceneTree：`get_tree().create_tween()`。
12. **绝不请求数据FROM `RenderingServer`或`PhysicsServer`在`_process`中** — 这些服务器异步运行。调用getter函数强制同步停滞，杀死性能。API故意设计为在热路径中只写。
13. **绝不使用`call_deferred()`作为初始化顺序错误的创可贴** — 它掩盖了架构问题（依赖树顺序）。用显式初始化信号或`@onready`修复实际依赖。
14. **绝不创建循环信号连接** — 节点A连接到B，B连接到A。这在第一次发出时创建无限循环。使用调解者模式（信号总线）打破循环。
15. **绝不让继承超过3级** — 超过3级，调试`super()`链是噩梦。使用组合（`Node`子节点）来添加行为。

---

## 📊 第五部分：性能预算（具体数字）

| 指标 | 移动目标 | 桌面目标 | 专家笔记 |
| :--- | :--- | :--- | :--- |
| **绘制调用** | < 100 (2D), < 200 (3D) | < 500 | 对树叶/碎片使用`MultiMeshInstance` |
| **三角形计数** | < 100K可见 | < 1M可见 | 超过500K必须使用LOD系统 |
| **纹理VRAM** | < 512MB | < 2GB | VRAM压缩：ETC2（移动），BPTC（桌面） |
| **脚本时间** | < 4ms每帧 | < 8ms每帧 | 将热循环移动到服务器API |
| **物理体** | < 200活跃 | < 1000活跃 | 对大规模模拟使用`PhysicsServer`直接API |
| **粒子** | < 2000总计 | < 10000总计 | GPU粒子，手动设置`visibility_aabb` |
| **音频总线** | < 8同时 | < 32同时 | 使用[音频系统](references/godot-audio-systems.md)总线路由 |
| **保存文件大小** | < 1MB | < 50MB | 种子 + 增量模式用于程序化世界 |
| **场景加载时间** | < 500ms | < 2s | `ResourceLoader.load_threaded_request()` |

---

## ⚙️ 第六部分：服务器API — 专家性能逃生口

这是大多数Godot开发者从未学习的知识。当场景树成为瓶颈时，使用Godot的低级服务器API完全绕过它。

### 何时下降到服务器API
- **10K+渲染实例**（精灵、网格）：使用`RenderingServer`与RID而不是`Sprite2D`/`MeshInstance3D`节点。
- **弹幕 / 粒子系统**与脚本交互：使用`PhysicsServer2D`体创建而不是`Area2D`节点。
- **大规模物理模拟**：直接使用`PhysicsServer3D`用于布娃娃场、碎片或流体类模拟。

### RID模式（专家）
服务器API通过**RID**（资源ID）通信——服务器端对象的不透明句柄。关键规则：
```gdscript
# 创建服务器端画布项（无节点开销）
var ci_rid := RenderingServer.canvas_item_create()
RenderingServer.canvas_item_set_parent(ci_rid, get_canvas_item())

# 关键：保持资源引用活跃。RID不算作引用。
# 如果Texture资源被GC，RID会静默无效。
var texture: Texture2D = preload("res://sprite.png")
RenderingServer.canvas_item_add_texture_rect(ci_rid, Rect2(-texture.get_size() / 2, texture.get_size()), texture)
```

### 与服务器的线程
- 场景树**不是线程安全的**。但服务器API（RenderingServer，PhysicsServer）在项目设置中启用时是线程安全的。
- 你可以在工作线程上构建场景块（实例化 + add_child），但必须使用`add_child.call_deferred()`将它们附加到活动树。
- GDScript字典/数组：跨线程读取和写入是安全的，但**调整大小**（追加、删除、调整大小）需要`Mutex`。
- **绝不**从多个线程同时加载相同的`Resource`——使用一个加载线程。

---

## 🧩 第七部分：专家代码模式

### 组件注册表
```gdscript
class_name Entity extends CharacterBody2D

var _components: Dictionary = {}

func _ready() -> void:
    for child in get_children():
        if child.has_method("get_component_name"):
            _components[child.get_component_name()] = child

func get_component(component_name: StringName) -> Node:
    return _components.get(component_name)
```

### 死实例安全信号处理器
```gdscript
func _on_damage_dealt(target: Node, amount: int) -> void:
    if not is_instance_valid(target): return
    if target.is_queued_for_deletion(): return
    target.get_component(&"health").apply_damage(amount)
```

### 异步资源加载器
```gdscript
func _load_level_async(path: String) -> void:
    ResourceLoader.load_threaded_request(path)
    while ResourceLoader.load_threaded_get_status(path) == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
        await get_tree().process_frame
    var scene: PackedScene = ResourceLoader.load_threaded_get(path)
    add_child(scene.instantiate())
```

### 状态机转换守卫
```gdscript
func can_transition_to(new_state: StringName) -> bool:
    match name:
        &"Dead": return false  # 终端状态
        &"Stunned": return new_state == &"Idle"  # 只能恢复到Idle
        _: return true
```

### 线程安全区块加载器（服务器API模式）
```gdscript
func _load_chunk_threaded(chunk_pos: Vector2i) -> void:
    # 在活动树外构建场景块（线程安全）
    var chunk := _generate_chunk(chunk_pos)
    # 仅从主线程附加到活动树
    _world_root.add_child.call_deferred(chunk)
```

---

## 🔥 第八部分：Godot 4.x陷阱（仅限老兵）

1. **`@export`资源默认共享**：多个场景实例都共享相同的`Resource`。在`_ready()`中使用`resource.duplicate()`或启用“局部到场景”复选框。这是新手在Godot 4中报告最多的Bug #1。
2. **信号语法静默失败**：`connect("signal_name", target, "method")`（Godot 3语法）编译但Godot 4中什么也不做。必须使用`signal_name.connect(callable)`。
3. **`Tween`不再是节点**：通过`create_tween()`创建，绑定到创建节点的生命周期。如果那个节点被释放，Tween死亡。对持久补间使用`get_tree().create_tween()`。
4. **`PhysicsBody`层与掩码**：`collision_layer` = “我是什么”。`collision_mask` = “我扫描什么”。将两者设置为相同值导致自碰撞或错过检测。
5. **`StringName` vs `String`在热路径中**：`StringName`（`&"key"`）使用指针比较（O(1)）。`String`使用字符比较（O(n)）。始终在`_process`中对字典键使用`StringName`。
6. **`@onready`时机**：在`_init()`之后但在`_ready()`期间运行。如果你需要构造器时间设置，使用`_init()`。如果你需要树访问，使用`@onready`或`_ready()`。混合它们导致空值。
7. **服务器查询停滞**：在`_process`中调用`RenderingServer`或`PhysicsServer` getter函数强制同步管道刷新。这些服务器异步运行——从它们请求数据停滞整个管道直到服务器赶上。
8. **`move_and_slide()` API更改**：返回`bool`（是否发生碰撞）。速度现在是属性，不是参数。在调用`move_and_slide()`之前`velocity = dir * speed`。

---

## 📂 第九部分：模块目录（86个蓝图）

> [!重要]
> 仅加载当前工作流程所需的模块。使用第2部分的决策矩阵来确定要遵循的链。

### 架构与基础
[基础](references/godot-project-foundations.md) | [组合](references/godot-composition.md) | [应用组合](references/godot-composition-apps.md) | [信号](references/godot-signal-architecture.md) | [自动加载](references/godot-autoload-architecture.md) | [状态](references/godot-state-machine-advanced.md) | [资源](references/godot-resource-data-patterns.md) | [模板](references/godot-project-templates.md) | [MCP设置](references/godot-mcp-setup.md) | [技能发现](references/godot-skill-discovery.md) | [技能判断](references/godot-skill-judge.md)

### GDScript与测试
[GDScript精通](references/godot-gdscript-mastery.md) | [测试模式](references/godot-testing-patterns.md) | [调试/性能分析](references/godot-debugging-profiling.md) | [性能优化](references/godot-performance-optimization.md)

### 2D系统
[2D动画](references/godot-2d-animation.md) | [2D物理](references/godot-2d-physics.md) | [Tilemaps](references/godot-tilemap-mastery.md) | [动画播放器](references/godot-animation-player.md) | [动画树](references/godot-animation-tree-mastery.md) | [CharacterBody2D](references/godot-characterbody-2d.md) | [粒子](references/godot-particles.md) | [补间](references/godot-tweening.md) | [着色器基础](references/godot-shaders-basics.md) | [相机系统](references/godot-camera-systems.md)

### 3D系统
[3D照明](references/godot-3d-lighting.md) | [3D材质](references/godot-3d-materials.md) | [3D世界构建](references/godot-3d-world-building.md) | [物理3D](references/godot-physics-3d.md) | [导航/路径查找](references/godot-navigation-pathfinding.md) | [程序化生成](references/godot-procedural-generation.md)

### 游戏机制
[能力](references/godot-ability-system.md) | [战斗](references/godot-combat-system.md) | [对话](references/godot-dialogue-system.md) | [经济](references/godot-economy-system.md) | [库存](references/godot-inventory-system.md) | [任务](references/godot-quest-system.md) | [RPG统计](references/godot-rpg-stats.md) | [回合系统](references/godot-turn-system.md) | [音频](references/godot-audio-systems.md) | [场景转换](references/godot-scene-management.md) | [保存/加载](references/godot-save-load-systems.md) | [秘密](references/mechanic-secrets.md) | [收集](references/game-loop-collection.md) | [复活](references/mechanic-revival.md)

### UI与UX
[UI容器](references/godot-ui-containers.md) | [富文本](references/godot-ui-rich-text.md) | [主题](references/godot-ui-theming.md) | [输入处理](references/godot-input-handling.md) | [季节性主题](references/theme-easter.md)

### 连接性与平台
[多人游戏](references/godot-multiplayer-networking.md) | [服务器逻辑](references/godot-server-architecture.md) | [导出构建](references/godot-export-builds.md) | [桌面](references/godot-platform-desktop.md) | [移动](references/godot-platform-mobile.md) | [网页](references/godot-platform-web.md) | [控制台](references/godot-platform-console.md) | [VR](references/godot-platform-vr.md)

### 适应指南
[2D→3D](references/godot-adapt-2d-to-3d.md) | [3D→2D](references/godot-adapt-3d-to-2d.md) | [桌面→移动](references/godot-adapt-desktop-to-mobile.md) | [移动→桌面](references/godot-adapt-mobile-to-desktop.md) | [单→多](references/godot-adapt-single-to-multiplayer.md)

### 类型蓝图
[动作RPG](references/godot-genre-action-rpg.md) | [射击游戏](references/godot-genre-shooter.md) | [RTS](references/godot-genre-rts.md) | [MOBA](references/godot-genre-moba.md) | [Rogue类](references/godot-genre-roguelike.md) | [生存](references/godot-genre-survival.md) | [开放世界](references/godot-genre-open-world.md) | [Metroidvania](references/godot-genre-metroidvania.md) | [平台游戏](references/godot-genre-platformer.md) | [格斗](references/godot-genre-fighting.md) | [潜行](references/godot-genre-stealth.md) | [沙盒](references/godot-genre-sandbox.md) | [恐怖](references/godot-genre-horror.md) | [解谜](references/godot-genre-puzzle.md) | [赛车](references/godot-genre-racing.md) | [节奏](references/godot-genre-rhythm.md) | [体育](references/godot-genre-sports.md) | [大逃杀](references/godot-genre-battle-royale.md) | [卡牌游戏](references/godot-genre-card-game.md) | [视觉小说](references/godot-genre-visual-novel.md) | [浪漫](references/romance.md) | [模拟](references/godot-genre-simulation.md) | [塔防](references/godot-genre-tower-defense.md) | [闲置点击](references/godot-genre-idle-clicker.md) | [派对](references/godot-genre-party.md) | [教育](references/godot-genre-educational.md)

### MCP工具
[MCP场景构建器](references/godot-mcp-scene-builder.md)

---

## 🐛 第十部分：专家诊断模式

### “隐形节点”Bug
**症状**：节点存在于树中但不渲染。
**专家诊断链**：`visible`属性 → `z_index` → 父`CanvasLayer`错误层 → `modulate.a == 0` → 在相机`near`剪辑后面（3D） → `SubViewport.render_target_update_mode`未设置 → `CanvasItem`不在任何`CanvasLayer`中（渲染在所有东西后面）。

### “输入被吞噬”Bug
**症状**：点击或按键间歇性忽略。
**专家诊断**：另一个`Control`节点与`mouse_filter = STOP`重叠目标。或，模式`PopupMenu`消耗未处理输入。或，另一个脚本中的`_unhandled_input()`调用`get_viewport().set_input_as_handled()`。

### “物理抖动”Bug
**症状**：角色在表面接触处振动。
**专家诊断**：`Safe Margin`太大。或，使用`_process`进行移动而不是`_physics_process`（插值不匹配）。或，碰撞形状在生成时重叠（永久推彼此分开）。

### “内存泄漏”
**症状**：游戏期间RAM稳定增长。
**专家诊断**：调用`queue_free()`但引用保持在数组/字典中。或，信号以`CONNECT_REFERENCE_COUNTED`连接而没有清理。使用性能分析器“对象”选项卡查找孤儿实例。搜索没有父节点的`Node`实例。

### “帧尖峰”
**症状**：平滑FPS但周期性下降。
**专家诊断**：GDScript GC传递。或，大资源的同步`load()`。或，`NavigationServer`重新烘焙。或，服务器API查询停滞（在`_process`中从`RenderingServer`请求数据）。使用内置性能分析器 → 寻找函数级尖峰。

---

## 参考
- [Godot 4.x官方文档](https://docs.godotengine.org/en/stable/)
- [Godot引擎GitHub讨论](https://github.com/godotengine/godot/discussions)
