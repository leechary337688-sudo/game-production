---
name: godot-genre-moba
description: "MOBA游戏的专家蓝图，包括线路逻辑（每30秒生成小兵波）、塔攻击优先级（英雄攻击盟友优先于小兵优先于英雄）、点击移动控制（RTS风格射线投射）、英雄技能系统（QWER冷却时间、法力消耗）、战争迷雾（SubViewport投影）和权威网络（服务器验证伤害）。用于竞争性5v5或竞技场游戏。触发关键词：MOBA、lane_manager、minion_waves、tower_aggro、click_to_move、ability_cooldowns、fog_of_war、comeback_mechanics。"
---

# 类型：MOBA（多人在线战术竞技游戏）

MOBA的专家蓝图，强调竞争平衡和战略深度。

## 永远不要做

- **永远不要客户端伤害计算** — 客户端说“我朝方向V施放Q”，服务器计算伤害。否则黑客会轻易破坏游戏。
- **永远不要忽视滚雪球效应** — 获胜团队变得太强。实施翻盘机制（击杀赏金、追赶经验）。
- **永远不要每帧为所有小兵路径规划** — 100+小兵会导致延迟。在多帧上时间分片路径规划。
- **永远不要每帧同步位置** — 使用客户端预测。以10-20Hz同步位置修正，而不是60Hz。
- **永远不要忘记小兵避让** — 启用NavigationAgent3D.avoidance_enabled，使小兵像水一样流动，而不是堆叠。
---

## 可用脚本

> **强制**：在实现相应模式前，阅读适当的脚本。

### [skill_shot_indicator.gd](scripts/skill_shot_indicator.gd)
鼠标跟随的技能射击预告。绘制矩形指示器，在_physics_process中朝向光标旋转以预览技能范围。

### [tower_priority_aggro.gd](scripts/tower_priority_aggro.gd)
塔目标优先级堆栈：攻击盟友的英雄 > 小兵 > 英雄。确定性目标选择，使用最近距离作为平局决胜器。

---

## 核心循环
1.  **线路**：玩家在指定线路中击杀小兵获取金币/经验。
2.  **交换**：玩家与对手英雄交换伤害。
3.  **突袭**：玩家游走到其他线路以奇袭敌人。
4.  **推进**：团队摧毁塔以打开地图。
5.  **结束**：摧毁敌人核心/枢纽。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 控制 | `rts-controls` | 右键移动、A移动、停止 |
| 2. 人工智能 | `godot-navigation-pathfinding` | 小兵波、塔攻击逻辑 |
| 3. 战斗 | `godot-ability-system`, `godot-rpg-stats` | QWER技能、冷却时间、缩放 |
| 4. 网络 | `godot-multiplayer-networking` | 权威、延迟补偿、预测 |
| 5. 地图 | `godot-3d-world-building` | 线路、野区、河流、基地 |

## 架构概述

### 1. 线路管理器
定期生成小兵波。

```gdscript
# lane_manager.gd
extends Node

@export var lane_path: Path3D
@export var spawn_interval: float = 30.0
var timer: float = 0.0

func _process(delta: float) -> void:
    timer -= delta
    if timer <= 0:
        spawn_wave()
        timer = spawn_interval

func spawn_wave() -> void:
    # 生成3个近战、3个远程、1个炮车（每第三波）
    for i in range(3):
        spawn_minion(MeleeMinion, lane_path)
        await get_tree().create_timer(1.0).timeout
```

### 2. 小兵人工智能
简单但遵循严格规则。

```gdscript
# minion_ai.gd
extends CharacterBody3D

enum State { MARCH, COMBAT }
var current_target: Node3D

func _physics_process(delta: float) -> void:
    match state:
        State.MARCH:
            move_along_path()
            scan_for_enemies()
        State.COMBAT:
            if is_instance_valid(current_target):
                attack(current_target)
            else:
                state = State.MARCH
```

### 3. 塔攻击逻辑
新手玩家最常误解的机制。

```gdscript
# tower.gd
func _on_aggro_check() -> void:
    # 优先级1：攻击盟友的敌人英雄
    var hero_target = check_for_hero_aggro()
    if hero_target:
        current_target = hero_target
        return

    # 优先级2：最近的小兵
    # 优先级3：最近的英雄
```

## 关键机制实现

### 点击移动（RTS风格）
从相机到地形的射线投射。

```gdscript
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("move"):
        var result = raycast_from_mouse()
        if result:
            nav_agent.target_position = result.position
```

### 技能系统（数据驱动）
定义“火球”或“钩子”而不为每个事物编写独特脚本。

```gdscript
# ability_data.gd
class_name Ability extends Resource
@export var cooldown: float
@export var mana_cost: float
@export var damage: float
@export var effect_scene: PackedScene
```

## Godot特定提示

*   **NavigationAgent3D**：使用`avoidance_enabled`让 小兵像水一样流动，而不是堆叠。
*   **MultiplayerSynchronizer**：同步健康、法力和冷却时间。如果使用客户端预测（高级），不要每帧同步位置。
*   **战争迷雾**：使用带迷雾纹理的`SubViewport`。在盟友所在位置在纹理上“挖洞”。将此纹理投射到地形着色器上。

## 常见陷阱

1.  **滚雪球效应**：获胜团队变得太快太强。**修复**：实施“翻盘经验/金币”机制（赏金）。
2.  **路径规划延迟**：100个小兵每帧路径规划。**修复**：在多帧上分布路径规划更新（时间分片）。
3.  **黑客攻击**：客户端说“我造成了1000伤害”。**修复**：客户端说“我朝方向V施放技能Q”。服务器计算伤害。

## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
