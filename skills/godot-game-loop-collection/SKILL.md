---
name: godot-game-loop-collection
description: 用于实现收藏任务、寻宝游戏或“找到所有X”目标时使用。
---

# 收藏游戏循环

## 概述
这个技能提供了一个标准化的框架，用于“收藏循环”——玩家必须找到并收集一组特定物品的游戏目标（例如，隐藏的彩蛋、数据日志、硬币）。

## 核心组件

### 1. 收藏管理器 (`collection_manager.gd`)
狩猎的中心大脑。
- **角色**: 跟踪进度（`当前 / 目标`）。
- **行为**: 监听 `item_collected(id)` -> 更新物品 -> 在有效计数时发出 `collection_completed` 信号。
- **提示**: 使用 `collection_id` 字符串来同时运行多个狩猎（例如，“red_eggs” vs “blue_eggs”）。

### 2. 可收藏物品 (`collectible_item.gd`)
世界中的物理对象。
- **角色**: 处理交互和自我销毁。
- **行为**: 在交互时 -> 播放VFX -> 发出信号 -> 队列释放。

### 3. 隐藏物品生成器 (`hidden_item_spawner.gd`)
自动化物品的放置。
- **角色**: 填充关卡。
- **行为**: 在以下位置实例化物品场景：
    -   手动放置的 `Marker3D` 节点（确定性）。
    -   在 `CollisionShape` 体积内的随机点（过程性）。

## 使用示例

```gdscript
# 在关卡脚本或游戏模式中
@onready var manager = $CollectionManager

func _ready():
    manager.start_collection("easter_egg_2024", 10)
    manager.collection_completed.connect(_on_all_eggs_found)

func _on_all_eggs_found():
    print("你找到了所有的彩蛋！这里是一顶兔子帽子。")
    # 解锁奖励
```

## 最佳实践
- **持久性**: 与 `godot-mechanic-secrets` 结合使用，以保存玩家退出和恢复时找到的具体ID。
- **永远不要在代码中硬编码生成位置**: 始终在场景中使用 `Marker3D` 或 `CollisionShape3D` 节点，这样设计师可以在不接触代码的情况下调整布局。
- **避免“上帝对象”**: `CollectionManager` 不应该处理输入、UI和音频。让它发出信号，让其他系统反应。
- **汁液**: 总是在物品消失*之前*生成粒子或播放声音。立即 `queue_free()` 感觉很干。
