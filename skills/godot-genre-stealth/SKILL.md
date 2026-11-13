---
name: godot-genre-stealth
description: "潜行游戏的专家蓝图（参考《细胞分裂》、《杀手》、《耻辱》、《神偷》），涵盖AI检测系统、视觉锥、声音传播、警戒状态、光影机制和系统化设计。适用于构建潜行动作、战术潜入或沉浸式模拟游戏，需要敌人感知系统。关键词：视觉锥、检测、警戒状态、声音传播、光照水平、系统化AI、渐进检测。"
---

# 类型：潜行

玩家选择、系统化AI和清晰通信定义了潜行游戏。

## 可用脚本

### [stealth_ai_controller.gd](scripts/stealth_ai_controller.gd)
具有渐进检测、声音响应和警戒状态管理的专家AI控制器。

## 核心循环

`观察 → 计划 → 执行 → 适应 → 完成`

## 在潜行游戏中永远不要做的事情

- **永远不要使用即时二元检测** — 使用渐进式0-100%检测并提供视觉反馈（填充计量表）。二元“看到/未看到”会剥夺玩家代理权，感觉不公平。
- **永远不要让守卫看穿墙壁** — 使用基于射线投射的视觉和碰撞掩码。`has_line_of_sight()` 必须检查几何体。穿墙破坏潜行完整性。
- **永远不要使用简单距离检查声音** — 声音通过 `NavigationServer3D` 路径传播，而不是直线距离。穿墙听力破坏沉浸感。
- **永远不要让战斗像潜行一样可行** — 如果枪战比潜行更容易，玩家会忽略潜行。战斗应该高风险（寡不敌众、弹药有限、声响警报）。
- **永远不要对玩家隐藏检测原因** — 显示为什么被检测到（光照水平高、发出噪音、在视觉锥内）。突然死亡会挫败玩家，无法教学。
- **永远不要使用单一样本点检查玩家可见性** — 采样多个身体部位（头部、躯干、脚部）。躲在低矮掩体后应隐藏躯干但暴露头部。
- **永远不要忘记周边视觉** — 人类有约180°周边视觉（效果较差）和60°集中视觉。单一锥体不真实。使用复合形状（《细胞分裂》方法）。

---

## 设计原则

来自行业专家（《细胞分裂》、《耻辱》、《杀手》开发者）：

1. **玩家选择**：每个场景都有多种有效方法
2. **系统化设计**：基于规则的AI，玩家可以学习和利用
3. **清晰通信**：玩家始终理解游戏状态和威胁
4. **公平检测**：没有“突然袭击”时刻 — 威胁在危险前可见

---

## AI检测系统

### 视觉锥实现

基于《细胞分裂：黑名单》GDC演讲 — 真实视觉使用**复合形状**：

```gdscript
class_name EnemyVision
extends Node3D

@export var forward_vision_range := 20.0    # 主视觉锥
@export var peripheral_range := 10.0        # 周边视觉
@export var forward_fov := 60.0             # 度数
@export var peripheral_fov := 120.0          # 度数
@export var detection_speed := 1.0          # 检测速度

var detection_level := 0.0  # 0-100
var target: Node3D = null

func _physics_process(delta: float) -> void:
    var player := get_player_if_visible()
    if player:
        # 检测速率变化因素：
        # - 距离（更近 = 更快）
        # - 玩家光照水平
        # - 玩家移动（移动 = 更可见）
        # - 在周边 vs 直接视觉中
        var rate := calculate_detection_rate(player)
        detection_level = min(100, detection_level + rate * delta)
    else:
        detection_level = max(0, detection_level - detection_speed * 0.5 * delta)

func get_player_if_visible() -> Player:
    var player := get_tree().get_first_node_in_group("player")
    if not player:
        return null
    
    var to_player := player.global_position - global_position
    var distance := to_player.length()
    var angle := rad_to_deg(global_basis.z.angle_to(-to_player.normalized()))
    
    # 检查前方锥体
    if angle < forward_fov / 2.0 and distance < forward_vision_range:
        if has_line_of_sight(player):
            return player
    
    # 检查周边（效果较差）
    elif angle < peripheral_fov / 2.0 and distance < peripheral_range:
        if has_line_of_sight(player):
            return player
    
    return null

func calculate_detection_rate(player: Player) -> float:
    var distance := global_position.distance_to(player.global_position)
    var distance_factor := 1.0 - (distance / forward_vision_range)
    
    var light_factor := player.get_light_level()  # 0.0 = 黑暗, 1.0 = 明亮
    var movement_factor := 1.0 if player.velocity.length() > 0.5 else 0.3
    
    return detection_speed * distance_factor * light_factor * movement_factor * 50.0
```

### 声音检测系统

基于《神偷》/《杀手》实现 — 声音沿导航路径传播：

```gdscript
class_name SoundPropagation
extends Node

# 声音通过连接的导航点传播，而不是穿透墙壁
func propagate_sound(origin: Vector3, loudness: float, sound_type: String) -> void:
    for enemy in get_tree().get_nodes_in_group("enemies"):
        var path := NavigationServer3D.map_get_path(
            get_world_3d().navigation_map,
            origin,
            enemy.global_position,
            true
        )
        
        if path.is_empty():
            continue  # 无路径 = 声音被阻挡
        
        var path_distance := calculate_path_length(path)
        var heard_loudness := loudness - (path_distance * 0.5)  # 衰减
        
        if heard_loudness > enemy.hearing_threshold:
            enemy.hear_sound(origin, sound_type, heard_loudness)

func calculate_path_length(path: PackedVector3Array) -> float:
    var length := 0.0
    for i in range(1, path.size()):
        length += path[i].distance_to(path[i - 1])
    return length
```

### 玩家光照水平

```gdscript
class_name LightDetector
extends Node3D

@export var sample_points: Array[Marker3D]  # 玩家身体上的多个点

func get_light_level() -> float:
    var total := 0.0
    var space := get_world_3d().direct_space_state
    
    for point in sample_points:
        for light in get_tree().get_nodes_in_group("lights"):
            var dir := light.global_position - point.global_position
            var query := PhysicsRayQueryParameters3D.create(
                point.global_position,
                light.global_position
            )
            var result := space.intersect_ray(query)
            
            if result.is_empty():  # 未被阻挡
                total += light.light_energy / dir.length_squared()
    
    return clamp(total / sample_points.size(), 0.0, 1.0)
```

---

## AI警戒状态

三阶段系统（行业标准）：

```gdscript
enum AlertState { IDLE, SUSPICIOUS, ALERTED, COMBAT }

class_name EnemyAI
extends CharacterBody3D

var alert_state := AlertState.IDLE
var suspicion_point: Vector3
var search_timer := 0.0

signal alert_state_changed(new_state: AlertState)

func transition_to(new_state: AlertState) -> void:
    alert_state = new_state
    alert_state_changed.emit(new_state)
    
    match new_state:
        AlertState.SUSPICIOUS:
            play_animation("suspicious")
            speak_dialogue("what_was_that")
        AlertState.ALERTED:
            speak_dialogue("who_goes_there")
            # 范围内的其他守卫听到并变得可疑
            alert_nearby_guards()
        AlertState.COMBAT:
            speak_dialogue("intruder")
            trigger_alarm()
```

### 视觉反馈（关键！）

```gdscript
class_name AlertIndicator
extends Node3D

@export var idle_icon: Texture2D
@export var suspicious_icon: Texture2D  # "?" 
@export var alerted_icon: Texture2D     # "!"
@export var detection_meter: ProgressBar  # 显示填充检测

func update_indicator(state: AlertState, detection: float) -> void:
    detection_meter.value = detection
    
    match state:
        AlertState.IDLE:
            icon.texture = idle_icon
            detection_meter.visible = false
        AlertState.SUSPICIOUS:
            icon.texture = suspicious_icon
            detection_meter.visible = true
        AlertState.ALERTED:
            icon.texture = alerted_icon
            detection_meter.visible = false
```

---

## 玩家能力

五种潜行工具类别（基于Mark Brown分析）：

### 1. 移动修改

```gdscript
# 蹲下、爬行、奔跑（嘈杂 vs 安静）
func calculate_noise_level() -> float:
    if is_crouching:
        return 0.2
    elif is_running:
        return 1.0
    else:
        return 0.5
```

### 2. 信息收集

```gdscript
# 窥视、侦察、标记敌人
func activate_detective_vision() -> void:
    for enemy in get_tree().get_nodes_in_group("enemies"):
        enemy.show_outline()
        enemy.show_vision_cone()
```

### 3. AI操纵

```gdscript
# 投掷分心物
func throw_distraction(target_position: Vector3) -> void:
    var rock := distraction_scene.instantiate()
    rock.global_position = target_position
    add_child(rock)
    SoundPropagation.propagate_sound(target_position, 30.0, "impact")
```

### 4. 空间控制

```gdscript
# 射击灯光、创建藏匿点
func shoot_light(light: Light3D) -> void:
    light.visible = false
    # 更新区域光照水平
```

### 5. 敌人消灭

```gdscript
func perform_takedown(enemy: EnemyAI, lethal: bool) -> void:
    if enemy.alert_state == AlertState.COMBAT:
        return  # 无法潜行击杀警觉敌人
    
    if lethal:
        enemy.die()
    else:
        enemy.knockout()
    
    # 尸体变为可交互
    spawn_body(enemy)
```

---

## 关卡设计

### 前哨设计（开放区域）

```
                      [观察的安全周界]
                               |
           [边缘稀疏守卫 - 可隔离]
                               |
                [密集中心的目]
                               |
              [多个入口点/路线]
```

### 有限遭遇设计（走廊）

- 敌人在接触前8+米可见
- 多种通过路径
- 掩护物体和藏匿点
- 紧急逃生路线

---

## UI通信

基于《神偷》的“光照宝石”创新：

```gdscript
class_name StealthHUD
extends Control

@onready var visibility_meter: TextureProgressBar
@onready var sound_meter: TextureProgressBar
@onready var minimap: Control

func _process(_delta: float) -> void:
    visibility_meter.value = player.get_light_level() * 100
    sound_meter.value = player.current_noise_level * 100
```

---

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 即时检测 | 使用渐进检测并提供清晰反馈 |
| 守卫看穿墙壁 | 基于射线投射的视觉和正确碰撞 |
| 不公平巡逻模式 | 使模式可学习，带有提示 |
| 两个游戏（潜行 + 战斗） | 要么致力于潜行，要么使战斗高风险 |
| 不清晰检测 | 始终显示为什么玩家被检测到 |

---

## Godot特定提示

1. **视觉射线投射**：使用 `PhysicsRayQueryParameters3D` 和碰撞掩码
2. **NavigationAgent3D**：用于巡逻路线和路径查找
3. **Area3D**：用于声音传播区域和触发区域
4. **AnimationTree**：混合警戒状态动画


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
