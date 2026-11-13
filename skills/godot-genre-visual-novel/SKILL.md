---
name: godot-genre-visual-novel
description: "专家蓝图，适用于视觉小说（如Doki Doki Literature Club、Phoenix Wright、Steins;Gate），专注于分支叙事、对话系统、选择后果、回滚机制和持久标志。用于构建故事驱动、选择导向或约会模拟游戏。关键词：视觉小说、对话系统、分支叙事、打字机效果、回滚、bbcode、RichTextLabel。"
---

# 流派：视觉小说

分支叙事、有意义的选择和品质功能定义了视觉小说。

## 核心循环
1.  **阅读**：消费叙事文本和角色对话
2.  **决策**：在关键时刻选择
3.  **分支**：故事根据选择分叉
4.  **后果**：立即反应或长期标志变化
5.  **结束**：达到多个结局之一

## 视觉小说中绝不要做的事

- **绝不要创造选择的幻觉**——如果所有选项立即导致相同结果，玩家会感到被欺骗。始终提供对话变化或标志变化，即使情节后来汇合。
- **绝不要跳过自动、跳过和保存/加载功能**——这些在VN流派中是强制性的。玩家重玩所有路线。缺少品质功能 = 低质量VN。
- **绝不要显示大段未分段的文本**——6行以上的文本 = 令人畏惧。将每对话框限制为3-4行。用角色反应或停顿打断。
- **绝不要在脚本中硬编码对话**——作家不是程序员。使用JSON/CSV/自定义格式。硬编码 = 叙事更改的迭代噩梦。
- **绝不要忘记回滚/历史**——玩家误点选择或想重读。缺少回滚 = 令人沮丧。在每一行之前存储状态，使用历史堆栈。
- **绝不要忽略BBCode/富文本效果**——纯文本 = 无聊。在RichTextLabel中使用`[wave]`、`[shake]`、`[color]`来增加情感节奏。“我[shake]恨[/shake]你” > “我恨你”。

---

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 文本与UI | `ui-system`, `rich-text-label` | 对话框、bbcode效果、打字效果 |
| 2. 逻辑 | `json-parsing`, `resource-management` | 加载脚本、管理角色数据 |
| 3. 状态 | `godot-save-load-systems`, `dictionaries` | 标志、历史、持久数据 |
| 4. 音频 | `audio-system` | 配音、背景音乐过渡 |
| 5. 抛光 | `godot-tweening`, `shaders` | 角色过渡、背景效果 |

## 架构概览

### 1. 故事管理器（驱动器）
解析脚本并指导其他系统。

```gdscript
# story_manager.gd
extends Node

var current_script: Dictionary
var current_line_index: int = 0
var flags: Dictionary = {}

func load_script(script_path: String) -> void:
    var file = FileAccess.open(script_path, FileAccess.READ)
    current_script = JSON.parse_string(file.get_as_text())
    current_line_index = 0
    display_next_line()

func display_next_line() -> void:
    if current_line_index >= current_script["lines"].size():
        return
        
    var line_data = current_script["lines"][current_line_index]
    
    if line_data.has("choice"):
        present_choices(line_data["choice"])
    else:
        CharacterManager.show_character(line_data.get("character"), line_data.get("expression"))
        DialogueUI.show_text(line_data["text"])
        current_line_index += 1
```

### 2. 对话UI（打字机效果）
逐字符显示文本。

```gdscript
# dialogue_ui.gd
func show_text(text: String) -> void:
    rich_text_label.text = text
    rich_text_label.visible_ratio = 0.0
    
    var tween = create_tween()
    tween.tween_property(rich_text_label, "visible_ratio", 1.0, text.length() * 0.05)
```

### 3. 历史与回滚
基本VN功能。在每一行之前存储状态。

```gdscript
var history: Array[Dictionary] = []

func save_state_to_history() -> void:
    history.append({
        "line_index": current_line_index,
        "flags": flags.duplicate(),
        "background": current_background,
        "music": current_music
    })

func rollback() -> void:
    if history.is_empty(): return
    var trusted_state = history.pop_back()
    restore_state(trusted_state)
```

## 关键机制实现

### 分支路径（标志）
跟踪决策以影响未来场景。

```gdscript
func make_choice(choice_id: String) -> void:
    match choice_id:
        "be_nice":
            flags["relationship_alice"] += 1
            jump_to_label("alice_happy")
        "be_mean":
            flags["relationship_alice"] -= 1
            jump_to_label("alice_sad")
```

### 脚本格式（JSON vs 资源）
*   **JSON**：易于外部编写，标准格式。
*   **自定义资源**：类型安全，可在检查器中编辑。
*   **文本解析器**：（例如，类Markdown语法）对作家更简单。

## 常见陷阱

1.  **文本过多**：大段文本令人畏惧。分段处理。**修复**：将行数限制在最多3-4行。
2.  **选择的幻觉**：选择立即导致相同结果感觉廉价。**修复**：使用对话中的小变化，即使主要情节汇合。
3.  **缺少品质功能**：无跳过、无自动、无保存。**修复**：这些是流派的强制功能。

## Godot特定提示

*   **RichTextLabel**：使用BBCode进行`[wave]`、`[shake]`、`[color]`效果，为文本增加情感。
*   **资源预加载器**：视觉小说有大量资源（4K背景）。异步加载场景或在章节之间使用加载屏幕。
*   **Dialogic**：提到这个插件很重要——它是Godot VN的行业标准。如果需要全套工具，请使用它；如果需要轻量级需求，请构建自己的。

## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
