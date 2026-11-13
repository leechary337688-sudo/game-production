---
name: godot-genre-horror
description: "专家蓝图，用于恐怖游戏，包括紧张节奏（锯齿波：构建/峰值/缓解）、Director系统（宏观AI控制节奏）、感官AI（视觉/声音检测）、理智/压力系统（相机抖动、音频失真）、照明氛围（体积雾、动态阴影）和'双脑'AI（作弊导演+诚实感官）。适用于心理恐怖、生存恐怖或氛围游戏。触发关键词：horror_game, tension_pacing, director_system, sensory_perception, sanity_system, volumetric_fog, AI_reaction_time."
---

# 类型：恐怖

专家蓝图，用于恐怖游戏，平衡紧张、氛围和玩家代理。

## 永远不要做

- **永远不要保持持续紧张** — 玩家会麻木。在惊吓之间强制执行“缓解”期（安全房间、平静音乐）以锯齿波节奏。
- **永远不要让AI立即检测玩家** — 立即检测感觉不公平。给AI 1-3秒反应时间或“怀疑计量表”在完全攻击之前。
- **永远不要让环境太暗** — 黑暗应该隐藏*细节*，而不是*导航*。使用边缘照明或弱手电筒。
- **永远不要仅依赖跳跃惊吓** — 跳跃惊吓在2-3次使用后失去效果。通过氛围和预期构建恐惧。
- **永远不要给玩家太多力量** — 无限弹药/治疗打破恐怖。稀缺性创造紧张（有限电池、健康、弹药）。
---

## 可用脚本

> **必读**：在实现相应模式之前阅读适当的脚本。

### [predator_stalking_ai.gd](scripts/predator_stalking_ai.gd)
AI跟踪玩家同时避免视线。通过点积检查玩家视野锥，检测时垂直后退，保持跟踪距离。

---

## 核心循环
1.  **探索**：玩家在威胁环境中导航。
2.  **感知**：玩家听到/看到危险迹象。
3.  **反应**：玩家隐藏、逃跑或战斗（弱化战斗）。
4.  **生存**：玩家到达安全地点或解决谜题。
5.  **缓解**：紧张再次构建前的短暂平静时刻。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 氛围 | `godot-3d-lighting`, `godot-audio-systems` | 体积雾、动态阴影、空间音频 |
| 2. AI | `godot-state-machine-advanced`, `godot-navigation-pathfinding` | 猎手AI、感官感知 |
| 3. 玩家 | `characterbody-3d` | 倾斜、隐藏、缓慢移动 |
| 4. 稀缺性 | `godot-inventory-system` | 有限电池、弹药、健康 |
| 5. 逻辑 | `game-manager` | 控制节奏的“Director”系统 |

## 架构概述

### 1. Director系统（宏观AI）
控制游戏节奏以防止持续疲惫。

```gdscript
# director.gd
extends Node

enum TensionState { BUILDUP, PEAK, RELIEF, QUIET }
var current_tension: float = 0.0
var player_stress_level: float = 0.0

func _process(delta: float) -> void:
    match current_tension_state:
        TensionState.BUILDUP:
            current_tension += 0.5 * delta
            if current_tension > 75.0:
                 trigger_event()
        TensionState.RELIEF:
            current_tension -= 2.0 * delta

func trigger_event() -> void:
    # 提示怪物AI检查玩家附近房间，而不是玩家所在位置
    monster_ai.investigate_area(player.global_position + Vector3(randf(), 0, randf()) * 10)
```

### 2. 感官感知（微观AI）
怪物的实际感官。

```gdscript
# sensory_component.gd
extends Area3D

signal sound_heard(position: Vector3, volume: float)
signal player_spotted(position: Vector3)

func check_vision(target: Node3D) -> bool:
    var space_state = get_world_3d().direct_space_state
    var query = PhysicsRayQueryParameters3D.create(global_position, target.global_position)
    var result = space_state.intersect_ray(query)
    
    if result and result.collider == target:
        return true
    return false
```

### 3. 理智/压力系统
基于恐惧扭曲世界。

```gdscript
# sanity_manager.gd
func update_sanity(amount: float) -> void:
    current_sanity = clamp(current_sanity + amount, 0.0, 100.0)
    # 效果：相机抖动
    camera_shake_intensity = (100.0 - current_sanity) * 0.01
    # 效果：音频失真
    audio_bus.get_effect(0).drive = (100.0 - current_sanity) * 0.05
```

## 关键机制实现

### 节奏（锯齿波）
恐怖需要高峰和低谷。
1.  **安全**：保存房间。
2.  **不安**：奇怪噪音、灯光闪烁。
3.  **恐惧**：怪物已知靠近。
4.  **恐怖**：追逐序列/战斗。
5.  **缓解**：逃到安全。

### “双脑”AI
*   **Director（全知）**：作弊以保持怪物相关性（如果距离远则传送它，引导它到玩家大致区域）。
*   **Alien（仅感官）**：诚实AI。必须实际看到/听到玩家才能攻击。

## Godot特定提示

*   **体积雾**：使用`WorldEnvironment` -> `VolumetricFog`以即时氛围。动画`density`以动态恐惧。
*   **Light Occluder 2D**：对于2D恐怖，阴影投射至关重要。
*   **AudioBus**：在主总线使用`Reverb`和`LowPassFilter`，由脚本控制，模拟害怕或隐藏时的“闷响”听力。
*   **AnimationTree**：使用混合空间平滑“潜行”、“行走”和“奔跑”动画之间的过渡。

## 常见陷阱

1.  **持续紧张**：玩家麻木。**修复**：强制执行“缓解”期，期间无事发生。
2.  **令人沮丧的AI**：AI立即看到玩家。**修复**：给AI“反应时间”或“怀疑计量表”在完全攻击之前。
3.  **太暗**：玩家什么都看不到。**修复**：黑暗应该隐藏*细节*，而不是*导航*。使用边缘照明或弱手电筒。


## 参考
- 大师技能： [godot-master](../godot-master/SKILL.md)
