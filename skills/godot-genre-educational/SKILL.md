---
名称: godot-genre-educational
描述: "教育游戏专家蓝图，包括游戏化循环（学习/应用/反馈/适应）、进度跟踪（学生档案、掌握率%）、自适应难度（目标70%成功率）、间隔重复、课程树（先决条件系统）和视觉反馈（彩带、经验条）。适用于学习应用、训练模拟或教育娱乐。触发关键词：educational_game, gamification, adaptive_difficulty, spaced_repetition, student_profile, curriculum_tree, mastery_tracking。"
---

# 类型: 教育 / 游戏化

教育游戏专家蓝图，通过游戏机制使学习变得吸引人。

## 永远不要做

- **永远不要用“游戏结束”惩罚失败** — 学习需要安全实验。使用“再试一次”或“这里有个提示”而不是失败状态。
- **永远不要将学习与游戏玩法分开** — “巧克力覆盖的西兰花”感觉像作业。让机制本身就是学习（例如，《死亡打字员》）。
- **永远不要使用大段文本** — 玩家跳过教程。展示，而不是讲述。先互动，然后简短解释。
- **永远不要跳过间隔重复** — 回答错误的问题应该在稍后重新出现。一次性问题不能建立掌握。
- **永远不要向学习者隐藏进度** — 可见的经验条、掌握率和技能树激励持续学习。不透明的系统令人沮丧。
---

## 可用脚本

> **强制**: 在实现相应模式之前阅读适当的脚本。

### [adaptive_difficulty_adjuster.gd](scripts/adaptive_difficulty_adjuster.gd)
成功比率跟踪与分支提示。基于滑动窗口调整难度上下，提供连续失败时的渐进提示披露。

---

## 核心循环
1.  **学习**: 玩家接收新信息（文本、图表、视频）。
2.  **应用**: 玩家使用该信息解决问题或完成任务。
3.  **反馈**: 游戏提供即时纠正或奖励。
4.  **适应**: 系统根据表现调整未来问题。
5.  **掌握**: 玩家解锁新主题或装饰性奖励。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. UI | `godot-ui-rich-text`, `godot-ui-theming` | 可读文本，拖放答案 |
| 2. 数据 | `godot-save-load-systems`, `json-serialization` | 学生档案，进度跟踪 |
| 3. 逻辑 | `state-machine` | 测验流程（问题 -> 答案 -> 结果） |
| 4. 动效 | `godot-particles`, `godot-tweening` | 让学习感觉有回报 |
| 5. 元 | `godot-scene-management` | 在课程和地图之间导航 |

## 架构概述

### 1. 帷幕（问题管理器）
管理单个“课程”或“测验”的流程。

```gdscript
# quiz_manager.gd
extends Node

var current_question: QuestionData
var correct_streak: int = 0

func submit_answer(answer_index: int) -> void:
    if current_question.is_correct(answer_index):
        handle_success()
    else:
        handle_failure()

func handle_success() -> void:
    correct_streak += 1
    EffectManager.play_confetti()
    StudentProfile.add_xp(current_question.topic, 10)
    load_next_question()

func handle_failure() -> void:
    correct_streak = 0
    # 间隔重复: 将这个问题加回队列
    question_queue.push_back(current_question)
    show_explanation()
```

### 2. 学生档案
持久化数据跟踪掌握程度。

```gdscript
# student_profile.gd
class_name StudentProfile extends Resource

@export var topic_mastery: Dictionary = {} # "math_add": 0.5 (50%)
@export var total_xp: int = 0
@export var badges: Array[String] = []

func get_mastery(topic: String) -> float:
    return topic_mastery.get(topic, 0.0)
```

### 3. 课程树
定义知识的依赖图。

```gdscript
# curriculum_node.gd
extends Resource
@export var id: String
@export var title: String
@export var required_topics: Array[String] # 先决条件
```

## 关键机制实现

### 自适应难度算法
如果玩家表现出色，给出更难的问题。如果挣扎，放松难度。

```gdscript
func get_next_question() -> QuestionData:
    var player_rating = StudentProfile.get_rating(current_topic)
    # 目标70%成功率以实现“心流状态”
    var target_difficulty = player_rating + 0.1 
    return QuestionBank.find_question(target_difficulty)
```

### 动效（“Duolingo效应”）
学习很难。游戏必须在视觉上大力奖励努力。
*   **声音**: 正确时的满意“叮！”声。
*   **视觉效果**: 屏幕震动，godot-particles，倍数弹窗。
*   **UI**: 进度条平滑填充（补间动画）。

## Godot特定技巧

*   **RichTextLabel**: 对于数学公式或着色关键词（BBCode）至关重要。
*   **拖放**: Godot的Control节点有内置的`_get_drag_data`和`_drop_data`方法。非常适合“匹配项目”谜题。
*   **本地化**: 教育游戏通常需要支持多种语言。从一开始就使用Godot的`TranslationServer`。

## 常见陷阱

1.  **巧克力覆盖的西兰花**: 游戏循环和学习循环分开。**修复**: 让机制本身就是学习（例如，《死亡打字员》）。
2.  **惩罚失败**: 玩家因错误而“游戏结束”。**修复**: 永远不要失败状态。只需“再试一次”或“这里有个提示”。
3.  **大段文本**: 太多阅读。**修复**: 先互动。展示，而不是讲述。


## 参考
- 大师技能: [godot-master](../godot-master/SKILL.md)
