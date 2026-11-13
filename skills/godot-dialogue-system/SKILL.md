---
名称: godot对话系统
描述: "分支对话系统的专家模式，包括对话图（基于资源）、角色肖像、玩家选择、条件对话（标志/任务）、打字机效果、本地化支持和语音集成。用于叙事游戏、RPG或视觉小说。触发关键词: DialogueLine, DialogueChoice, DialogueGraph, dialogue_manager, typewriter_effect, branching_dialogue, dialogue_flags, localization, voice_acting."
---

# 对话系统

构建灵活、数据驱动对话系统的专家指导。

## 绝不能做

- **切勿在脚本中硬编码对话** — 使用基于资源的DialogueLine/DialogueGraph。硬编码的对话不便于本地化维护。
- **切勿忘记检查选择条件** — 显示不可用的选择会混淆玩家。在显示前通过`check_conditions()`过滤选择。
- **切勿使用未验证的字符串ID** — `next_line_id`中的拼写错误会导致静默失败。添加`assert(dialogues.has(line_id))`检查。
- **切勿跳过打字机效果而不提供玩家选项** — 有些玩家想要即时文本。添加“跳过打字机”按钮或设置。
- **切勿在UI中存储对话状态** — UI应仅用于显示。将当前行/对话ID存储在DialogueManager（AutoLoad）中以支持场景切换。
---

## 可用脚本

> **强制**：在实现相应模式前阅读适当的脚本。

### [dialogue_engine.gd](scripts/dialogue_engine.gd)
基于图的对话，带有BBCode信号标签。从文本解析[trigger:event_id]标签，触发信号，并加载外部JSON对话图。

### [dialogue_manager.gd](scripts/dialogue_manager.gd)
数据驱动的对话引擎，支持分支、变量存储和条件选择。

---

## 对话数据

```gdscript
# dialogue_line.gd
class_name DialogueLine
extends Resource

@export var speaker: String
@export_multiline var text: String
@export var portrait: Texture2D
@export var choices: Array[DialogueChoice] = []
@export var conditions: Array[String] = []  # 任务标志等。
@export var next_line_id: String = ""
```

```gdscript
# dialogue_choice.gd
class_name DialogueChoice
extends Resource

@export var choice_text: String
@export var next_line_id: String
@export var conditions: Array[String] = []
@export var effects: Array[String] = []  # 设置标志、给予物品
```

## 对话管理器

```gdscript
# dialogue_manager.gd (AutoLoad)
extends Node

signal dialogue_started
signal dialogue_ended
signal line_displayed(line: DialogueLine)
signal choice_selected(choice: DialogueChoice)

var dialogues: Dictionary = {}
var flags: Dictionary = {}

func load_dialogue(path: String) -> void:
    var data := load(path)
    dialogues[path] = data

func start_dialogue(dialogue_id: String, start_line: String = "start") -> void:
    dialogue_started.emit()
    display_line(dialogue_id, start_line)

func display_line(dialogue_id: String, line_id: String) -> void:
    var line: DialogueLine = dialogues[dialogue_id].lines[line_id]
    
    # 检查条件
    if not check_conditions(line.conditions):
        # 跳转到下一行
        if line.next_line_id:
            display_line(dialogue_id, line.next_line_id)
        else:
            end_dialogue()
        return
    
    line_displayed.emit(line)
    
    # 自动前进或等待玩家
    if line.choices.is_empty() and line.next_line_id:
        # 等待玩家点击
        await get_tree().create_timer(0.1).timeout
    elif line.choices.is_empty():
        end_dialogue()

func select_choice(dialogue_id: String, choice: DialogueChoice) -> void:
    choice_selected.emit(choice)
    
    # 应用效果
    for effect in choice.effects:
        apply_effect(effect)
    
    # 继续到下一行
    if choice.next_line_id:
        display_line(dialogue_id, choice.next_line_id)
    else:
        end_dialogue()

func end_dialogue() -> void:
    dialogue_ended.emit()

func check_conditions(conditions: Array[String]) -> bool:
    for condition in conditions:
        if not flags.get(condition, false):
            return false
    return true

func apply_effect(effect: String) -> void:
    # 解析效果字符串，例如"set_flag:met_npc"
    var parts := effect.split(":")
    match parts[0]:
        "set_flag":
            flags[parts[1]] = true
        "give_item":
            # 与库存集成
            pass
```

## 对话UI

```gdscript
# dialogue_ui.gd
extends Control

@onready var speaker_label := $Panel/Speaker
@onready var text_label := $Panel/Text
@onready var portrait := $Panel/Portrait
@onready var choices_container := $Panel/Choices

var current_dialogue: String
var current_line: DialogueLine

func _ready() -> void:
    DialogueManager.line_displayed.connect(_on_line_displayed)
    DialogueManager.dialogue_ended.connect(_on_dialogue_ended)
    visible = false

func _on_line_displayed(line: DialogueLine) -> void:
    visible = true
    current_line = line
    
    speaker_label.text = line.speaker
    portrait.texture = line.portrait
    
    # 打字机效果
    text_label.text = ""
    for char in line.text:
        text_label.text += char
        await get_tree().create_timer(0.03).timeout
    
    # 显示选择
    if line.choices.is_empty():
        # 等待输入继续
        pass
    else:
        show_choices(line.choices)

func show_choices(choices: Array[DialogueChoice]) -> void:
    # 清除现有
    for child in choices_container.get_children():
        child.queue_free()
    
    # 添加选择按钮
    for choice in choices:
        if not DialogueManager.check_conditions(choice.conditions):
            continue
        
        var button := Button.new()
        button.text = choice.choice_text
        button.pressed.connect(func(): _on_choice_selected(choice))
        choices_container.add_child(button)

func _on_choice_selected(choice: DialogueChoice) -> void:
    DialogueManager.select_choice(current_dialogue, choice)

func _on_dialogue_ended() -> void:
    visible = false
```

## NPC交互

```gdscript
# npc.gd
extends CharacterBody2D

@export var dialogue_path: String = "res://dialogues/npc_1.tres"
@export var start_line: String = "start"

func interact() -> void:
    DialogueManager.start_dialogue(dialogue_path, start_line)
```

## 对话图（资源）

```gdscript
# dialogue_graph.gd
class_name DialogueGraph
extends Resource

@export var lines: Dictionary = {}  # line_id → DialogueLine

func _init() -> void:
    # 示例结构
    lines["start"] = create_line("Hero", "Hello!")
    lines["response"] = create_line("NPC", "Greetings, traveler!")

func create_line(speaker: String, text: String) -> DialogueLine:
    var line := DialogueLine.new()
    line.speaker = speaker
    line.text = text
    return line
```

## 本地化

```gdscript
# 使用Godot内置的CSV导入
# dialogue_en.csv:
# dialogue_id,speaker,text
# npc_1_start,Hero,"Hello!"
# npc_1_response,NPC,"Greetings!"

func get_localized_line(line_id: String) -> String:
    return tr(line_id)
```

## 高级：语音表演

```gdscript
@onready var voice_player := $AudioStreamPlayer

func play_voice_line(line_id: String) -> void:
    var audio := load("res://voice/" + line_id + ".mp3")
    if audio:
        voice_player.stream = audio
        voice_player.play()
```

## 最佳实践

1. **基于资源** - 将对话存储为资源
2. **标志系统** - 跟踪玩家选择
3. **打字机效果** - 增加精致感
4. **跳过按钮** - 让玩家可以跳过

## 参考
- 相关：`godot-signal-architecture`, `godot-save-load-systems`, `godot-ui-rich-text`


### 相关
- 主要技能：[godot-master](../godot-master/SKILL.md)
