---
name: godot-quest-system
description: "使用基于资源的任务、信号驱动更新和自动加载管理器，实现任务跟踪系统（目标、进度、奖励、分支链）的专家蓝图。适用于RPG任务或任务系统。关键词：任务、目标、任务资源、任务目标、信号驱动、分支、奖励、自动加载。"
---

# 任务系统

基于资源的数据、信号驱动的更新和自动加载协调定义了可扩展的任务架构。

## 可用脚本

### [quest_manager.gd](scripts/quest_manager.gd)
具有目标进度和奖励分发的专家自动加载任务追踪器。

### [quest_graph_manager.gd](scripts/quest_graph_manager.gd)
基于图的任务的运行时管理器。跟踪目标和节点进度。

## 在任务系统中切勿做的事情

- **切勿在节点中存储任务数据** — 在`player.gd`变量中存储任务进度？场景重载时丢失。使用基于资源的任务或自动加载单例。
- **切勿在不使用注册表的情况下使用字符串作为任务ID** — `update_objective("kil_bandts", ...)` 拼写错误 = 静默失败。使用常量或根据注册表验证ID。
- **切勿忘记断开信号连接** — 任务完成但信号仍连接？下一次更新时任务再次完成 = 重复奖励。在`_on_quest_completed()`中断开连接。
- **切勿轮询目标更新** — 每帧检查`if enemy_count == 10` = 浪费。使用信号：`enemy.died.connect(quest_manager.on_enemy_killed)`。
- **切勿跳过任务的保存/加载** — 玩家完成任务5，游戏重启，任务重置？沮丧。必须持久化`active_quests` + `completed_quests`数组。
- **切勿在不进行空值检查的情况下使用`all()`处理目标** — `objectives.all(func(obj): return obj.is_complete())` 有null目标？崩溃。首先验证数组内容。

---

```gdscript
# quest.gd
class_name Quest
extends Resource

signal progress_updated(objective_id: String, progress: int)signal completed

@export var quest_id: String
@export var quest_name: String
@export_multiline var description: String
@export var objectives: Array[QuestObjective] = []
@export var rewards: Array[QuestReward] = []
@export var required_level: int = 1

func is_complete() -> bool:
    return objectives.all(func(obj): return obj.is_complete())

func check_completion() -> void:
    if is_complete():
        completed.emit()
```

## 任务目标

```gdscript
# quest_objective.gd
class_name QuestObjective
extends Resource

enum Type { KILL, COLLECT, TALK, REACH }

@export var objective_id: String
@export var type: Type
@export var target: String  # 敌人名称、物品ID、NPC名称、位置
@export var required_amount: int = 1
@export var current_amount: int = 0

func progress(amount: int = 1) -> void:
    current_amount += amount
    current_amount = mini(current_amount, required_amount)

func is_complete() -> bool:
    return current_amount >= required_amount
```

## 任务管理器

```gdscript
# quest_manager.gd (AutoLoad)
extends Node

signal quest_accepted(quest: Quest)
signal quest_completed(quest: Quest)
signal objective_updated(quest: Quest, objective: QuestObjective)

var active_quests: Array[Quest] = []
var completed_quests: Array[String] = []

func accept_quest(quest: Quest) -> void:
    if quest.quest_id in completed_quests:
        return
    
    active_quests.append(quest)
    quest.completed.connect(func(): _on_quest_completed(quest))
    quest_accepted.emit(quest)

func _on_quest_completed(quest: Quest) -> void:
    active_quests.erase(quest)
    completed_quests.append(quest.quest_id)
    
    # 给予奖励
    for reward in quest.rewards:
        reward.grant()
    
    quest_completed.emit(quest)

func update_objective(quest_id: String, objective_id: String, amount: int = 1) -> void:
    for quest in active_quests:
        if quest.quest_id == quest_id:
            for obj in quest.objectives:
                if obj.objective_id == objective_id:
                    obj.progress(amount)
                    objective_updated.emit(quest, obj)
                    quest.check_completion()
                    return

func get_active_quest(quest_id: String) -> Quest:
    for quest in active_quests:
        if quest.quest_id == quest_id:
            return quest
    return null
```

## 任务触发器

```gdscript
# 示例：击杀任务集成
# enemy.gd
func _on_died() -> void:
    QuestManager.update_objective("kill_bandits", "kill_bandit", 1)

# 示例：收集任务集成
# item_pickup.gd
func _on_collected() -> void:
    QuestManager.update_objective("gather_herbs", "collect_herb", 1)

# 示例：对话任务集成
# npc.gd
func interact() -> void:
    DialogueManager.start_dialogue(dialogue_id)
    QuestManager.update_objective("find_elder", "talk_to_elder", 1)
```

## 任务UI

```gdscript
# quest_ui.gd
extends Control

@onready var quest_list := $QuestList

func _ready() -> void:
    QuestManager.quest_accepted.connect(_on_quest_accepted)
    QuestManager.objective_updated.connect(_on_objective_updated)
    refresh_ui()

func refresh_ui() -> void:
    for child in quest_list.get_children():
        child.queue_free()
    
    for quest in QuestManager.active_quests:
        var quest_entry := create_quest_entry(quest)
        quest_list.add_child(quest_entry)

func create_quest_entry(quest: Quest) -> Control:
    var entry := VBoxContainer.new()
    
    var title := Label.new()
    title.text = quest.quest_name
    entry.add_child(title)
    
    for obj in quest.objectives:
        var obj_label := Label.new()
        obj_label.text = "%s: %d/%d" % [obj.target, obj.current_amount, obj.required_amount]
        entry.add_child(obj_label)
    
    return entry
```

## 最佳实践

1. **信号驱动** — 发出事件，系统监听
2. **保存进度** — 跟踪已完成任务
3. **验证** — 接受前检查先决条件

## 参考
- 相关：`godot-dialogue-system`、`godot-save-load-systems`


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
