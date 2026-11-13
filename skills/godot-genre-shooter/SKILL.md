---
名称: godot-genre-shooter
描述: "FPS/TPS射击游戏（如《使命召唤》、《反恐精英》、《Apex英雄》、《堡垒之夜》）的专家蓝图，涵盖武器系统、后坐力模式、命中扫描与弹道、辅助瞄准、多人预测和枪战手感。适用于构建竞争性射击游戏、大逃杀或需要响应式战斗的战术FPS游戏。关键词：命中扫描、后坐力模式、辅助瞄准、客户端预测、武器原型、弹道物理、命中注册。"
---

# 类型：射击游戏（FPS/TPS）

枪战手感、响应式战斗和竞争平衡定义射击游戏。

## 可用脚本

### [advanced_weapon_controller.gd](scripts/advanced_weapon_controller.gd)
高级后坐力、扩散和双命中扫描/弹道系统的专家模式，包含对象池笔记。

## 核心循环

`交战 → 瞄准 → 开火 → 击杀确认 → 获取下一个`

## 射击游戏中绝不要做

- **绝不要在 `_process()` 中进行命中检测** — 命中扫描必须在 `_physics_process()` 或按需使用物理射线检测。帧率依赖的准确性会破坏竞争完整性。
- **绝不要将后坐力应用于武器模型变换** — 后坐力影响摄像机旋转（视图）和扩散（准确性），而不是枪的视觉位置。玩家学习控制摄像机，而非3D模型。
- **绝不要使用单个 `AudioStreamPlayer` 处理枪声** — 分层音频（射击声 + 机械声 + 尾音）创造有力感。单流枪声听起来平淡且业余。
- **绝不要使用 `rpc()` 每子弹同步弹道** — 带宽死亡。对视觉效果使用客户端预测，服务器权威命中验证。压缩：发送开火事件，而非每帧位置。
- **绝不要使用 `Area3D` 重叠进行命中扫描命中** — 这比 `PhysicsRayQueryParameters3D` 慢10-100倍。区域用于触发器（如生命值拾取），而非即时弹道。
- **绝不要在武器脚本中硬编码伤害值** — 将状态导出到 `Resource` 以存储武器数据。设计师需要迭代而无需代码更改。使用 `WeaponData.tres`。
- **绝不允许在多人游戏中客户端权威命中决策** — 客户端说“我射中了你” = 黑客天堂。服务器使用延迟补偿（回滚）验证所有伤害。

---

## 武器系统架构

```gdscript
class_name Weapon
extends Node3D

@export_group("状态")
@export var damage: int = 20
@export var fire_rate: float = 0.1  # 射击间隔秒数
@export var magazine_size: int = 30
@export var reload_time: float = 2.0
@export var range: float = 100.0

@export_group("后坐力")
@export var base_recoil: Vector2 = Vector2(0.5, 2.0)  # X, Y 度
@export var recoil_recovery_speed: float = 5.0
@export var max_spread: float = 5.0

@export_group("类型")
@export var is_hitscan: bool = true
@export var projectile_scene: PackedScene

var current_ammo: int
var can_fire: bool = true
var current_recoil: Vector2 = Vector2.ZERO
var current_spread: float = 0.0

signal fired
signal reloaded
signal ammo_changed(current: int, max: int)
```

---

## 命中扫描 vs 弹道

### 命中扫描（即时命中）

```gdscript
func fire_hitscan() -> void:
    if not can_fire or current_ammo <= 0:
        return
    
    current_ammo -= 1
    ammo_changed.emit(current_ammo, magazine_size)
    
    var camera := get_viewport().get_camera_3d()
    var ray_origin := camera.global_position
    var ray_direction := -camera.global_basis.z
    
    # 应用扩散
    ray_direction = apply_spread(ray_direction)
    
    var space := get_world_3d().direct_space_state
    var query := PhysicsRayQueryParameters3D.create(
        ray_origin,
        ray_origin + ray_direction * range
    )
    query.collision_mask = collision_mask
    
    var result := space.intersect_ray(query)
    if result:
        var hit_point: Vector3 = result.position
        var hit_normal: Vector3 = result.normal
        var hit_object: Object = result.collider
        
        spawn_impact_effect(hit_point, hit_normal)
        
        if hit_object.has_method("take_damage"):
            var hit_zone := determine_hit_zone(result)
            var final_damage := calculate_damage(damage, hit_zone)
            hit_object.take_damage(final_damage, hit_zone)
    
    apply_recoil()
    start_fire_cooldown()
    fired.emit()

func determine_hit_zone(result: Dictionary) -> String:
    # 使用碰撞形状名称或骨骼检测命中区域
    if "headshot" in result.collider.name.to_lower():
        return "头部"
    elif "chest" in result.collider.name.to_lower():
        return "胸部"
    return "身体"

func calculate_damage(base: int, zone: String) -> int:
    match zone:
        "头部": return int(base * 2.5)
        "胸部": return int(base * 1.0)
        _: return int(base * 0.8)
```

### 弹道（物理子弹）

```gdscript
class_name Projectile
extends CharacterBody3D

@export var speed := 100.0
@export var damage := 20
@export var gravity_affected := true
@export var lifetime := 5.0

var direction: Vector3
var shooter: Node3D

func _ready() -> void:
    await get_tree().create_timer(lifetime).timeout
    queue_free()

func _physics_process(delta: float) -> void:
    if gravity_affected:
        velocity.y -= 9.8 * delta
    
    velocity = direction * speed
    var collision := move_and_collide(velocity * delta)
    
    if collision:
        var collider := collision.get_collider()
        if collider != shooter and collider.has_method("take_damage"):
            collider.take_damage(damage)
        spawn_impact(collision.get_position(), collision.get_normal())
        queue_free()
```

---

## 后坐力系统

三种后坐力类型协同工作：

```gdscript
class_name RecoilSystem
extends Node

var visual_recoil: Vector2 = Vector2.ZERO    # 摄像机抖动
var pattern_offset: Vector2 = Vector2.ZERO   # 确定性模式
var spread_bloom: float = 0.0                # 准确性损失

@export var recoil_pattern: Array[Vector2]   # 预定义散射模式
var pattern_index: int = 0

func apply_recoil(weapon: Weapon) -> void:
    # 1. 视觉后坐力 - 摄像机抖动
    visual_recoil.y += weapon.base_recoil.y * randf_range(0.8, 1.2)
    visual_recoil.x += weapon.base_recoil.x * randf_range(-1.0, 1.0)
    
    # 2. 模式后坐力 - 可学习的散射
    if pattern_index < recoil_pattern.size():
        pattern_offset += recoil_pattern[pattern_index]
        pattern_index += 1
    
    # 3. 扩散膨胀 - 减少准确性
    spread_bloom = min(spread_bloom + 0.5, weapon.max_spread)

func recover_recoil(delta: float, recovery_speed: float) -> void:
    visual_recoil = visual_recoil.lerp(Vector2.ZERO, recovery_speed * delta)
    pattern_offset = pattern_offset.lerp(Vector2.ZERO, recovery_speed * delta)
    spread_bloom = lerp(spread_bloom, 0.0, recovery_speed * delta)
    
    if visual_recoil.length() < 0.01:
        pattern_index = 0  # 重置模式

func get_spread_direction(base_direction: Vector3) -> Vector3:
    var spread_angle := deg_to_rad(spread_bloom)
    var random_offset := Vector2(
        randf_range(-spread_angle, spread_angle),
        randf_range(-spread_angle, spread_angle)
    )
    return base_direction.rotated(Vector3.UP, random_offset.x).rotated(Vector3.RIGHT, random_offset.y)
```

---

## 辅助瞄准（控制器支持）

```gdscript
class_name AimAssist
extends Node3D

@export var assist_range := 50.0
@export var assist_angle := 15.0  # 度
@export var friction_strength := 0.3  # 靠近目标时减速
@export var magnetism_strength := 0.1  # 向目标拉动

func apply_aim_assist(look_input: Vector2, camera: Camera3D) -> Vector2:
    var target := find_closest_target(camera)
    if not target:
        return look_input
    
    var to_target := target.global_position - camera.global_position
    var camera_forward := -camera.global_basis.z
    var angle := rad_to_deg(camera_forward.angle_to(to_target.normalized()))
    
    if angle > assist_angle:
        return look_input
    
    # 摩擦 - 靠近目标时减缓移动
    var friction := 1.0 - (friction_strength * (1.0 - angle / assist_angle))
    look_input *= friction
    
    # 磁性 - 轻微向目标拉动
    var target_screen_pos := camera.unproject_position(target.global_position)
    var screen_center := get_viewport().get_visible_rect().size / 2
    var pull_direction := (target_screen_pos - screen_center).normalized()
    look_input += pull_direction * magnetism_strength * (1.0 - angle / assist_angle)
    
    return look_input

func find_closest_target(camera: Camera3D) -> Node3D:
    var closest: Node3D = null
    var closest_angle := assist_angle
    
    for target in get_tree().get_nodes_in_group("enemies"):
        var to_target := target.global_position - camera.global_position
        var angle := rad_to_deg((-camera.global_basis.z).angle_to(to_target.normalized()))
        
        if angle < closest_angle and to_target.length() < assist_range:
            if has_line_of_sight(camera.global_position, target.global_position):
                closest = target
                closest_angle = angle
    
    return closest
```

---

## 武器手感优化

### 摄像机效果

```gdscript
func on_weapon_fired() -> void:
    # 屏幕抖动
    camera_shake(0.1, 0.05)
    
    # 视场冲击
    camera.fov += 2.0
    await get_tree().create_timer(0.05).timeout
    camera.fov -= 2.0
    
    # 枪口火焰
    muzzle_flash.visible = true
    await get_tree().create_timer(0.02).timeout
    muzzle_flash.visible = false

func on_weapon_reloaded() -> void:
    # 重装期间锁定控制
    can_fire = false
    can_aim = false
    
    play_animation("reload")
    await get_tree().create_timer(reload_time).timeout
    
    current_ammo = magazine_size
    can_fire = true
    can_aim = true
```

### 音频分层

```gdscript
@export var fire_sounds: Array[AudioStream]  # 随机选择
@export var tail_sound: AudioStream           # 混响/回声
@export var mechanical_sound: AudioStream     # 枪械机械声

func play_fire_audio() -> void:
    # 主要射击声
    var shot := fire_sounds.pick_random()
    fire_audio_player.stream = shot
    fire_audio_player.play()
    
    # 机械点击声
    mechanical_player.play()
    
    # 尾音（延迟混响）
    await get_tree().create_timer(0.1).timeout
    tail_player.play()
```

---

## 武器选择决策树

**设计武器平衡时：**
- 高射速（冲锋枪） = 单发伤害低，奖励跟踪瞄准
- 低射速（狙击枪） = 伤害高，奖励精准
- 霰弹枪 = 扩散模式（5-8颗弹丸），有效范围 <10米
- 突击步枪 = 全能型，各方面中等

**技术实现：**
- 手枪/突击步枪：命中扫描（即时反馈）
- 火箭/手榴弹：受重力影响的弹道
- 狙击枪：命中扫描带轨迹视觉

## 多人游戏客户端预测模式

```gdscript
# 客户端：即时反馈，无需等待服务器
func fire_client() -> void:
    play_effects_immediate()  # 枪口火焰、后坐力、音频
    local_hitscan_visual()    # 仅视觉血液溅射
    rpc_id(1, "server_validate_shot", camera.global_transform)

# 服务器：权威伤害
@rpc("any_peer")
func server_validate_shot(shooter_transform: Transform3D) -> void:
    var hit = perform_server_hitscan(shooter_transform)
    if hit and is_valid_shot(hit):
        rpc("confirm_hit", hit.victim_id, hit.damage)

# 边缘情况：如果客户端的视觉命中和服务器不匹配？
# 解决方案：服务器为准。如果不匹配，客户端显示“未注册”指示器。
```

## 常见陷阱与专家修复

- **子弹冲击感弱** → 三层音频（射击+尾音+机械声）+ 屏幕抖动 + 血液视觉效果 + 伤害数字
- **枪械感觉相同** → 独特后坐力模式（冲锋枪：紧密垂直，AK：强水平抖动）
- **无技能上限** → 可学习的散射模式（类似CS:GO风格），而非纯随机扩散
- **控制器瞄准挫败感** → 摩擦（靠近目标时0.3减速）+ 轻微0.1磁性

---

## Godot特定技巧

1. **射线检测**：使用带有适当层掩码的 `PhysicsRayQueryParameters3D`
2. **弹道**：根据物理需求使用 `CharacterBody3D` 或 `RigidBody3D`
3. **音频**：多个 `AudioStreamPlayer3D` 用于分层枪声
4. **动画**：使用 `AnimationTree` 处理武器状态机（待机、瞄准、开火、重装）

## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
