---
name: godot-mechanic-secrets
description: 用于实现作弊码、隐藏交互或基于玩家输入/行为的可解锁内容。
---

# 秘密与彩蛋（机制）

## 概述
这个技能提供可重用组件，用于基于玩家特定动作（如科乐美码、重复交互）隐藏内容，并管理这些发现的持久性。

## 核心组件

### 1. 输入序列监视器（input_sequence_watcher.gd）
一个监听特定序列的InputEvent的节点。
- **用途**：经典“作弊码”，隐藏调试菜单，“科乐美码”实现。
- **行为**：缓冲输入 -> 检查目标 -> 发射sequence_matched信号。

### 2. 交互阈值触发器（interaction_threshold_trigger.gd）
一个跟踪对象被交互了多少次的组件。
- **用途**：“别戳我”语音线，N次击打破墙，隐藏成就。
- **行为**：计数信号 -> 在特定计数时发射threshold_reached信号。

### 3. 秘密持久性（secret_persistence_handler.gd）
一个标准化的方式来保存/加载“已解锁”状态。
- **用途**：确保玩家不必每个会话重新输入代码。
- **行为**：包装ConfigFile来将布尔标志保存到user://secrets.cfg。

## 使用示例（作弊码）

```gdscript
# 在游戏管理器或玩家控制器中
@onready var cheat_watcher = $InputSequenceWatcher

func _ready():
    # 定义上，上，下，下...
    cheat_watcher.sequence = [
        "ui_up", "ui_up", "ui_down", "ui_down"
    ]
    cheat_watcher.sequence_matched.connect(_on_cheat_unlocked)

func _on_cheat_unlocked():
    print("上帝模式已启用！")
    SecretPersistence.unlock_secret("god_mode")
```

## 反模式
- **绝不硬编码输入检查**：绝不要在_process中使用Input.is_action_just_pressed来处理序列。它依赖于帧并且脆弱。始终使用基于事件的缓冲区。
- **绝不污染PlayerPrefs**：绝不将隐藏可解锁内容保存在用户的主要settings.cfg（分辨率，音量）中。如果用户删除设置来修复图形故障，他们不应该失去已解锁的作弊。使用user://secrets.cfg。
- **绝不信任客户端输入用于竞争性秘密**：如果你的秘密提供竞争优势（例如，在多人游戏中），绝不在客户端单独验证它。
