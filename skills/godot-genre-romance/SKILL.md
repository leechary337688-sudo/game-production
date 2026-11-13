---
名称: godot-genre-romance
描述: "专家蓝图，专为浪漫游戏和约会模拟（如《心跳回忆》、《怪物舞会》、《Persona》社交链接）设计，聚焦于情感系统、多统计关系、约会事件和路线分支。当构建以关系为中心的游戏、社交模拟或乙女游戏时使用。关键词：浪漫、约会模拟、情感系统、关系统计、约会事件、角色路线、爱情对象。"
---

# 类型：浪漫与约会模拟

浪漫游戏基于"情感经济"——管理玩家时间和资源以影响NPC的吸引力、信任和亲密关系。

## 核心循环
1.  **相遇**：遇到潜在的爱情对象并建立基础关系。
2.  **约会**：参与结构化事件，了解偏好并测试兼容性。
3.  **加深**：投资资源（时间、礼物、选择）以增加情感/统计值。
4.  **分支**：故事根据重大里程碑分化为角色特定的"路线"。
5.  **解决**：基于关系质量达到专门结局（好/正常/坏）。

## 在浪漫游戏中绝不要做

- **绝不要创建"自动售货机"式浪漫**——如果给10份礼物总等于告白，角色会感觉像物体。总是融入变量，如当前情绪、时机和统计阈值（例如，"必须有10点勇气才能邀约"）。
- **绝不要使用100%不透明的统计**——如果玩家不知道为什么约会失败，他们会感到被骗。总是提供微妙反馈或可见的"关系屏幕"（例如，心跳脉冲、信任条填充）。
- **绝不要使用二元情感（爱/恨）**——真实关系是复杂的。使用多轴统计，如**吸引力**（身体/化学反应）、**信任**（情感安全）和**舒适度**（熟悉度）进行更深的模拟。
- **绝不要陷入"相同约会顺序"陷阱**——为每个角色重复完全相同的约会序列会让游戏感觉重复。总是根据爱情对象变化约会地点、活动和对话结构。
- **绝不要忘记"可错过"里程碑**——如果玩家因为工作错过了"情人节"事件，那是一个有意义的（即使痛苦的）后果。不要强制每个事件都发生，无论玩家选择如何。
- **绝不要忽视NPC自主性**——如果NPC只为玩家存在，他们会感觉空洞。给他们自己的日程、目标，以及如果特定条件（如低信任）未满足时*拒绝*玩家的能力。

---

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 统计 | `字典`, `资源` | 跟踪多轴情感、角色配置文件 |
| 2. 时间线 | `自动加载架构`, `信号` | 管理时间/天数，触发预定的约会 |
| 3. 叙事 | `godot-对话系统`, `视觉小说` | 对话分支和选择后果 |
| 4. 持久性 | `godot-保存加载系统` | 保存关系状态、CG图库、标志 |
| 5. 美学 | `UI主题化`, `godot-补间动画` | 心形主题UI、脸红效果、情感图标 |

## 架构概述

### 1. 情感管理器（核心）
处理所有角色的复杂关系统计和礼物偏好。

```gdscript
# affection_manager.gd
class_name AffectionManager
extends Node

signal milestone_reached(character_id, level)

var relationship_data: Dictionary = {} # character_id: { attraction: 0, trust: 0, comfort: 0 }

func add_affection(char_id: String, type: String, amount: int) -> void:
    if not relationship_data.has(char_id):
        relationship_data[char_id] = {"attraction": 0, "trust": 0, "comfort": 0}
    
    relationship_data[char_id][type] = clamp(relationship_data[char_id][type] + amount, -100, 100)
    check_milestones(char_id)

func get_gift_effect(char_id: String, item_id: String) -> int:
    # 逻辑用于喜欢/不喜欢与递减回报
    return 10 # 占位符
```

### 2. 约会事件系统
管理浪漫约会的成功或失败。

```gdscript
# date_event_system.gd
func run_date(character_id: String, location_res: DateLocation) -> void:
    var score = 0
    # 加权计算
    score += relationship_data[character_id]["attraction"] * location_res.chemistry_mod
    score += relationship_data[character_id]["trust"] * location_res.safety_mod
    
    if score > location_res.success_threshold:
        play_date_outcome("SUCCESS", character_id)
    else:
        play_date_outcome("FAILURE", character_id)
```

### 3. 路线管理器
控制故事分支和持久性解锁。

```gdscript
# route_manager.gd
var unlocked_routes: Array[String] = []

func lock_in_route(char_id: String):
    # 在这里检测与其他路线的冲突
    if flags.get("on_route"): return
    
    current_route = char_id
    flags["on_route"] = true
    unlocked_cgs.append(char_id + "_prologue")
```

## 关键机制实现

### 情感反馈（果汁）
不要只改变数字；展示变化。

```gdscript
# ui_feedback.gd
func play_heart_burst(pos: Vector2):
    var heart = heart_scene.instantiate()
    add_child(heart)
    heart.global_position = pos
    var tween = create_tween().set_parallel()
    tween.tween_property(heart, "scale", Vector2(1.5, 1.5), 0.5)
    tween.tween_property(heart, "modulate:a", 0.0, 0.5)
```

### 时间限定事件
浪漫在于期待。

*   **截止时间调度**："在6月15日前告白，否则失败。"
*   **上下文对话**：角色根据时间或天气反应不同。

## 常见陷阱

1.  **"变态"陷阱**：强制玩家总是选择最调情的选项以获胜。**修复**：允许"信任"和"友谊"路径最终导致浪漫。
2.  **不透明成功**：约会失败而不知原因。**修复**：使用角色对话暗示偏好（"我不太喜欢吵闹的地方..."）。
3.  **路线冲突**：意外约会两个人而零后果。**修复**：在路线管理器中实现"嫉妒"或"冲突检测"系统。

## Godot特定技巧

*   **角色资源**：使用`CharacterProfile`资源存储基础统计、精灵和礼物偏好。
*   **RichTextLabel动画**：使用自定义BBCode实现"脸红"文本（脉冲粉色）或"紧张"文本（颤抖）。
*   **Dialogic集成**：虽然此技能专注于*系统*，但建议与Godot的**Dialogic**插件配对处理实际对话框。


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
- 子专长：[godot-genre-visual-novel](../godot-genre-visual-novel/SKILL.md)
