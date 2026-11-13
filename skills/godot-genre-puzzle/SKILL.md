---
名称：godot-genre-puzzle
描述： "谜题游戏的专家蓝图，包括撤销系统（用于状态反转的命令模式）、基于网格的逻辑（类似Sokoban的机制）、非语言教程（通过关卡设计教学）、胜利条件检查、状态管理和视觉反馈（有效移动的即时确认）。适用于逻辑谜题、物理谜题或匹配3游戏。触发关键词：puzzle_game, undo_system, command_pattern, grid_logic, non_verbal_tutorial, state_management。"
---

# 类型：谜题

强调清晰度、实验性和“顿悟”时刻的谜题游戏专家蓝图。

## 绝不要做

- **绝不要惩罚实验** — 谜题是关于测试想法的。始终提供撤销/重置。不要惩罚尝试。
- **绝不要要求像素完美输入** — 逻辑谜题不应需要精确瞄准。使用网格吸附或宽容的命中框。
- **绝不要允许未检测到的不可解状态** — 自动检测软锁或提供显著的“重置关卡”按钮。
- **绝不要隐藏规则** — 视觉反馈必须即时且清晰。例如，电线连接时亮起以教学规则。
- **绝不要跳过非语言教程** — 关卡1 = 在安全房间中单独介绍新机制。关卡2 = 简单使用。关卡3 = 与现有机制结合。
---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [command_undo_redo.gd](scripts/command_undo_redo.gd)
用于撤销/重做的命令模式。在双栈中存储可逆操作，新操作时清除重做历史。包括 MoveCommand 示例。

---

## 核心循环
1.  **观察**：玩家评估关卡布局和机制。
2.  **实验**：玩家与元素互动（推、拉、切换）。
3.  **反馈**：游戏反应（门打开、激光被阻挡）。
4.  **顿悟**：玩家理解逻辑（“顿悟”时刻）。
5.  **执行**：玩家执行解决方案以推进。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 交互 | `godot-input-handling`, `raycasting` | 点击、拖动、网格移动 |
| 2. 逻辑 | `command-pattern`, `state-management` | 撤销/重做、跟踪关卡状态 |
| 3. 反馈 | `godot-tweening`, `juice` | 有效移动的视觉确认 |
| 4. 进度 | `godot-save-load-systems`, `level-design` | 解锁关卡、跟踪星星/分数 |
| 5. 润色 | `ui-minimalism` | 非侵入式HUD |

## 架构概览

### 1. 命令模式（撤销系统）
对谜题游戏至关重要。绝不惩罚测试。

```gdscript
# command.gd
class_name Command extends RefCounted

func execute() -> void: pass
func undo() -> void: pass

# level_manager.gd
var history: Array[Command] = []
var history_index: int = -1

func commit_command(cmd: Command) -> void:
    # 如果偏离，清除重做历史
    if history_index < history.size() - 1:
        history = history.slice(0, history_index + 1)
        
    cmd.execute()
    history.append(cmd)
    history_index += 1

func undo() -> void:
    if history_index >= 0:
        history[history_index].undo()
        history_index -= 1
```

### 2. 网格系统（TileMap 与自定义）
对于基于网格的谜题（如Sokoban），自定义数据结构通常比仅读取物理更好。

```gdscript
# grid_manager.gd
var grid_size: Vector2i = Vector2i(16, 16)
var objects: Dictionary = {} # Vector2i -> Node

func move_object(obj: Node, direction: Vector2i) -> bool:
    var start_pos = grid_pos(obj.position)
    var target_pos = start_pos + direction
    
    if is_wall(target_pos):
        return false
        
    if objects.has(target_pos):
        # 在此处处理推动逻辑
        return false
        
    # 执行移动
    objects.erase(start_pos)
    objects[target_pos] = obj
    tween_movement(obj, target_pos)
    return true
```

## 关键机制实现

### 胜利条件检查
每次移动后检查胜利状态。

```gdscript
func check_win_condition() -> void:
    for target in targets:
        if not is_satisfied(target):
            return
    
    level_complete.emit()
    save_progress()
```

### 非语言教程
通过关卡设计而非文本来教学机制。
1.  **隔离**：关卡1仅在安全房间中介绍新机制。
2.  **强化**：关卡2需要使用它来解决一个简单问题。
3.  **组合**：关卡3将其与先前机制结合。

## 常见陷阱

1.  **严格性**：对逻辑谜题要求像素完美输入。**修复**：使用网格吸附或宽容命中框。
2.  **死胡同**：允许玩家进入不可解状态而不自知。**修复**：自动检测失败或提供显著的“重置”按钮。
3.  **模糊性**：隐藏规则。**修复**：视觉反馈必须即时且清晰（例如，电线连接时亮起）。

## Godot 特定提示

*   **缓动**：对所有网格移动使用 `create_tween()`。感觉比瞬间吸附好得多。
*   **自定义资源**：将关卡数据（布局、起始位置）存储在 `.tres` 文件中，便于在检查器中编辑。
*   **信号**：使用像 `state_changed` 这样的信号来更新UI/视觉，与逻辑解耦。


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
