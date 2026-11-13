---
名称：godot-debugging-profiling
描述："专家调试工作流，包括打印调试（push_warning、push_error、assert）、断点（条件断点）、Godot调试器（堆栈跟踪、变量、远程调试）、性能分析器（时间分析器、内存监视器）、错误处理模式和性能优化。用于bug修复、性能调优或开发诊断。触发关键词：breakpoint、print_debug、push_error、assert、profiler、remote_debug、memory_leak、orphan_nodes、Performance.get_monitor。"
---

# 调试与性能分析

使用Godot调试工具高效查找和修复bug的专家指导。

## 永不这样做

- **永不使用没有描述性上下文的`print()`** — `print(value)`是无用的。使用带标签的`print("玩家健康值：", health)`。
- **永不在发布版本中留下调试打印** — 用`if OS.is_debug_build()`包装或使用自定义DEBUG常量。打印会减慢发布版本。
- **永不忽略`push_warning()`消息** — 警告表示潜在bug（空引用、弃用的API）。在它们变成错误之前修复。
- **永不在发布版本中使用`assert()`进行运行时验证** — 断言在发布版本中被禁用。使用`if not condition: push_error()`进行运行时检查。
- **永不在调试模式下进行性能分析** — 调试构建慢5-10倍。始终使用发布导出或`--release`标志进行分析。
---

## 可用脚本

> **强制要求**：在实现相应模式之前，阅读适当的脚本。

### [performance_plotter.gd](scripts/performance_plotter.gd)
自定义性能监视器，用于游戏玩法指标（投射物/敌人数量）。包括带堆栈跟踪和内存统计的自动错误状态捕获。

### [debug_overlay.gd](scripts/debug_overlay.gd)
游戏内调试UI，实时显示FPS、内存、孤儿节点和自定义指标。

> **不要加载** debug_overlay.gd在发布版本中 - 用`if OS.is_debug_build()`包装使用。


---

## 打印调试

```gdscript
# 基本打印
print("值：", some_value)

# 格式化打印
print("玩家在 %s 位置，健康值 %d" % [position, health])

# 带调用者信息的打印
print_debug("调试信息在此")

# 警告（非致命）
push_warning("这可能是个问题")

# 错误（非致命）
push_error("出错了！")

# 断言（调试中致命）
assert(health > 0, "健康值不能为负！")
```

## 断点

**设置断点：**
- 点击脚本编辑器行号槽
- 或使用`breakpoint`关键字：

```gdscript
func suspicious_function() -> void:
    breakpoint  # 执行在此停止
    var result := calculate_something()
```

## 调试器面板

**调试 → 调试器** (Ctrl+Shift+D)

标签：
- **堆栈跟踪**：暂停时的调用堆栈
- **变量**：检查局部/成员变量
- **断点**：管理所有断点
- **错误**：运行时错误和警告

## 远程调试

**调试运行中的游戏：**
1. 运行项目 (F5)
2. 调试 → 远程调试 → 选择运行实例
3. 检查实时游戏状态

## 常见调试模式

### 空引用

```gdscript
# ❌ 崩溃：空引用
$NonExistentNode.do_thing()

# ✅ 安全：先检查
var node := get_node_or_null("MaybeExists")
if node:
    node.do_thing()
```

### 跟踪状态变化

```gdscript
var _health: int = 100

var health: int:
    get:
        return _health
    set(value):
        print("健康值改变：%d → %d" % [_health, value])
        print_stack()  # 显示谁改变了它
        _health = value
```

### 可视化射线投射

```gdscript
func _draw() -> void:
    if Engine.is_editor_hint():
        draw_line(Vector2.ZERO, ray_direction * ray_length, Color.RED, 2.0)
```

### 3D中的调试绘制

```gdscript
# 使用DebugDraw插件或创建调试网格
func debug_draw_sphere(pos: Vector3, radius: float) -> void:
    var mesh := SphereMesh.new()
    mesh.radius = radius
    var instance := MeshInstance3D.new()
    instance.mesh = mesh
    instance.global_position = pos
    add_child(instance)
```

## 错误处理

```gdscript
# 处理文件错误
func load_save() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        push_warning("未找到保存文件")
        return {}
    
    var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if file == null:
        push_error("打开保存失败：%s" % FileAccess.get_open_error())
        return {}
    
    var json := JSON.new()
    var error := json.parse(file.get_as_text())
    if error != OK:
        push_error("JSON解析错误：%s" % json.get_error_message())
        return {}
    
    return json.data
```

## 性能分析器

**调试 → 性能分析器** (F3)

### 时间分析器
- 显示函数执行时间
- 识别慢函数
- 目标：每帧< 16.67ms (60 FPS)

### 监视器
- FPS、物理、内存
- 对象计数
- 绘制调用

## 常见性能问题

### 问题：低FPS

```gdscript
# 在_process中检查
func _process(delta: float) -> void:
    print(Engine.get_frames_per_second())  # 监视FPS
```

### 问题：内存泄漏

```gdscript
# 用打印检查
func _exit_tree() -> void:
    print("节点释放：", name)

# 使用组跟踪
add_to_group("tracked")
print("活动对象：", get_tree().get_nodes_in_group("tracked").size())
```

### 问题：孤儿节点

```gdscript
# 检查孤儿
func check_orphans() -> void:
    print("孤儿节点：", Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT))
```

## 调试控制台

```gdscript
# 运行时调试控制台
var console_visible := false

func _input(event: InputEvent) -> void:
    if event is InputEventKey and event.keycode == KEY_QUOTELEFT:
        console_visible = not console_visible
        $DebugConsole.visible = console_visible
```

## 最佳实践

### 1. 使用调试标志

```gdscript
const DEBUG := true

func debug_log(message: String) -> void:
    if DEBUG:
        print("[DEBUG] ", message)
```

### 2. 条件断点

```gdscript
# 仅在特定条件下中断
if player.health <= 0:
    breakpoint
```

### 3. 场景树检查器

```
调试 → 远程调试 → 检查场景树
查看实时节点层次结构
```

## 参考
- [Godot文档：调试器](https://docs.godotengine.org/en/stable/tutorials/scripting/debug/debugger_panel.html)


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
