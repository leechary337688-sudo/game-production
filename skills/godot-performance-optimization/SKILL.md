---
名称: Godot 性能优化
描述: "专家蓝图，用于性能分析和优化（帧率下降、内存泄漏、绘制调用），使用 Godot Profiler、对象池化、可见性剔除和瓶颈识别。适用于诊断延迟、优化目标 FPS 或减少内存使用。关键词：性能分析、Godot Profiler、瓶颈、对象池化、VisibleOnScreenNotifier、绘制调用、MultiMesh。"
---

# 性能优化

性能分析驱动的分析、对象池化和可见性剔除定义了优化的游戏性能。

## 可用脚本

### [custom_performance_monitor.gd](scripts/custom_performance_monitor.gd)
用于在 Godot 调试器中添加和更新自定义性能监视器的管理器。

### [multimesh_foliage_manager.gd](scripts/multimesh_foliage_manager.gd)
专家级 MultiMesh 模式，用于高效渲染数千个植被实例。

## 在性能优化中永远不要做的事

- **永远不要在没有分析的情况下进行优化** — "我认为物理很慢" 但没有数据？过早优化。总是使用 调试 → 性能分析器 (F3) 来识别实际的瓶颈。
- **永远不要在发布版本中使用 `print()`** — 每一帧都使用 `print()` = 文件 I/O 瓶颈 + 日志泛滥。使用 `@warning_ignore` 或条件 `if OS.is_debug_build():`。
- **永远不要忽略屏幕外实体的 `VisibleOnScreenNotifier2D`** — 敌人在屏幕外处理逻辑 = 浪费 CPU。当 `screen_exited` 时禁用 `set_process(false)`。
- **永远不要在热循环中实例化节点** — `for i in 1000: var bullet = Bullet.new()` = 1000 次分配。使用对象池，重用实例。
- **永远不要在 `_process()` 中使用 `get_node()`** — 每秒调用 `get_node("Player")` 60 次 = 树遍历泛滥。使用 `@onready var player := $Player` 进行缓存。
- **永远不要忘记批处理绘制调用** — 1000 个独特的精灵 = 1000 个绘制调用。使用纹理集（精灵表）+ MultiMesh 进行实例化渲染。

---

**调试 → 性能分析器** (F3)

标签页:
- **时间**: 函数调用时间
- **内存**: RAM 使用情况
- **网络**: RPCs, 带宽
- **物理**: 碰撞检查

## 常见优化

### 对象池化

```gdscript
var bullet_pool: Array[Node] = []

func get_bullet() -> Node:
    if bullet_pool.is_empty():
        return Bullet.new()
    return bullet_pool.pop_back()

func return_bullet(bullet: Node) -> void:
    bullet.hide()
    bullet_pool.append(bullet)
```

### 可见性通知器

```gdscript
# 添加 VisibleOnScreenNotifier2D
# 当屏幕外时禁用处理
func _on_screen_exited() -> void:
    set_process(false)

func _on_screen_entered() -> void:
    set_process(true)
```

### 减少绘制调用

```
# 使用纹理集（精灵表）
# 批量处理相似材质
# 减少独特纹理
```

## 参考
- [Godot 文档: 性能优化](https://docs.godotengine.org/en/stable/tutorials/performance/general_optimization.html)


### 相关
- 主技能: [godot-master](../godot-master/SKILL.md)
