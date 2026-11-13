---
名称: godot-scene-management
描述: "用于场景加载、转换、异步（后台）加载、实例管理和缓存的专家蓝图。涵盖淡入淡出过渡、加载屏幕、动态生成和场景持久化。适用于实现关卡更改或动态内容加载。关键词：场景、加载、转换、异步、ResourceLoader、change_scene、preload、PackedScene、淡入淡出。"
---

# 场景管理

异步加载、转换、实例池和缓存定义了平滑的场景工作流。

## 可用脚本

### [async_scene_manager.gd](scripts/async_scene_manager.gd)
专家级异步场景加载器，带有进度跟踪、错误处理和转换回调。

### [scene_pool.gd](scripts/scene_pool.gd)
用于频繁生成场景（如子弹、粒子、敌人）的对象池。

### [scene_state_manager.gd](scripts/scene_state_manager.gd)
使用“持久化”组模式跨转换保存和恢复场景状态。

> **强制 - 为了平滑过渡**：在实现加载屏幕前，请阅读 async_scene_manager.gd。


## 场景管理中切勿做

- **切勿在游戏代码中使用 load()** — `var scene = load("res://level.tscn")` 会阻塞整个游戏直到加载完成。使用 `preload()` 或 `ResourceLoader.load_threaded_request()`。
- **切勿忘记检查 THREAD_LOAD_FAILED** — 异步加载而不检查状态？静默失败会导致黑屏。必须处理 `THREAD_LOAD_FAILED` 状态。
- **切勿在未清理的情况下更改场景** — 活动的计时器/补间跨场景持续存在会导致内存泄漏和意外行为。在转换前停止计时器、断开信号。
- **切勿在 _ready() 中使用 get_tree().change_scene_to_file()** — 在 `_ready()` 中更改场景会导致崩溃（场景树被锁定）。使用 `call_deferred("change_scene")`。
- **切勿在未进行空值检查的情况下实例化场景** — `var obj = scene.instantiate()` 如果场景加载失败？崩溃。首先检查 scene != null。
- **切勿忘记在动态实例上调用 queue_free()** — 生成了 1000 个敌人，都已死亡但未释放？内存泄漏。使用 `queue_free()` 或实例池。

---

```gdscript
# 即时场景更改
get_tree().change_scene_to_file("res://levels/level_2.tscn")

# 或使用打包场景
var next_scene := load("res://levels/level_2.tscn")
get_tree().change_scene_to_packed(next_scene)
```

## 带淡入淡出的场景转换

```gdscript
# scene_transitioner.gd (自动加载)
extends CanvasLayer

signal transition_finished

func change_scene(scene_path: String) -> void:
    # 淡出
    $AnimationPlayer.play("fade_out")
    await $AnimationPlayer.animation_finished
    
    # 更改场景
    get_tree().change_scene_to_file(scene_path)
    
    # 淡入
    $AnimationPlayer.play("fade_in")
    await $AnimationPlayer.animation_finished
    
    transition_finished.emit()

# 用法：
SceneTransitioner.change_scene("res://levels/level_2.tscn")
await SceneTransitioner.transition_finished
```

## 异步（后台）加载

```gdscript
extends Node

var loading_status: int = 0
var progress := []

func load_scene_async(path: String) -> void:
    ResourceLoader.load_threaded_request(path)
    
    while true:
        loading_status = ResourceLoader.load_threaded_get_status(
            path,
            progress
        )
        
        if loading_status == ResourceLoader.THREAD_LOAD_LOADED:
            var scene := ResourceLoader.load_threaded_get(path)
            get_tree().change_scene_to_packed(scene)
            break
        
        # 更新加载条
        print("加载中: ", progress[0] * 100, "%")
        await get_tree().process_frame
```

## 加载屏幕模式

```gdscript
# loading_screen.gd
extends Control

@onready var progress_bar: ProgressBar = $ProgressBar

func load_scene(path: String) -> void:
    show()
    ResourceLoader.load_threaded_request(path)
    
    var progress := []
    var status: int
    
    while true:
        status = ResourceLoader.load_threaded_get_status(path, progress)
        
        if status == ResourceLoader.THREAD_LOAD_LOADED:
            var scene := ResourceLoader.load_threaded_get(path)
            get_tree().change_scene_to_packed(scene)
            break
        elif status == ResourceLoader.THREAD_LOAD_FAILED:
            push_error("加载场景失败: " + path)
            break
        
        progress_bar.value = progress[0] * 100
        await get_tree().process_frame
    
    hide()
```

## 动态场景实例

### 作为子节点添加场景

```gdscript
# 运行时生成敌人
const ENEMY_SCENE := preload("res://enemies/goblin.tscn")

func spawn_enemy(position: Vector2) -> void:
    var enemy := ENEMY_SCENE.instantiate()
    enemy.global_position = position
    add_child(enemy)
```

### 实例管理

```gdscript
# 跟踪生成的敌人
var active_enemies: Array[Node] = []

func spawn_enemy(pos: Vector2) -> void:
    var enemy := ENEMY_SCENE.instantiate()
    enemy.global_position = pos
    add_child(enemy)
    active_enemies.append(enemy)
    
    # 当敌人死亡时清理
    enemy.tree_exited.connect(
        func(): active_enemies.erase(enemy)
    )

func clear_all_enemies() -> void:
    for enemy in active_enemies:
        enemy.queue_free()
    active_enemies.clear()
```

## 子场景

```gdscript
# 作为子场景加载 UI
@onready var ui := preload("res://ui/game_ui.tscn").instantiate()

func _ready() -> void:
    add_child(ui)
```

## 场景持久化

```gdscript
# 更改场景时保持场景加载
var persistent_scene: Node

func make_persistent(scene: Node) -> void:
    persistent_scene = scene
    scene.get_parent().remove_child(scene)
    get_tree().root.add_child(scene)

func restore_persistent() -> void:
    if persistent_scene:
        get_tree().root.remove_child(persistent_scene)
        add_child(persistent_scene)
```

## 重新加载当前场景

```gdscript
# 重启关卡
get_tree().reload_current_scene()
```

## 场景缓存

```gdscript
# 缓存常用场景
var scene_cache: Dictionary = {}

func get_cached_scene(path: String) -> PackedScene:
    if not scene_cache.has(path):
        scene_cache[path] = load(path)
    return scene_cache[path]

# 用法：
var enemy := get_cached_scene("res://enemies/goblin.tscn").instantiate()
```

## 最佳实践

### 1. 使用 SceneTransitioner 自动加载

```gdscript
# 集中式场景管理
# 所有转换通过一个系统进行
# 一致的淡入淡出效果
```

### 2. 预加载常见场景

```gdscript
# ✅ 良好 - 在编译时预加载
const BULLET := preload("res://projectiles/bullet.tscn")

# ❌ 差 - 在运行时加载
var bullet := load("res://projectiles/bullet.tscn")
```

### 3. 转换前清理

```gdscript
func change_level() -> void:
    # 清理计时器、补间等
    for timer in get_tree().get_nodes_in_group("timers"):
        timer.stop()
    
    SceneTransitioner.change_scene("res://levels/next.tscn")
```

### 4. 错误处理

```gdscript
func load_scene_safe(path: String) -> bool:
    if not ResourceLoader.exists(path):
        push_error("场景未找到: " + path)
        return false
    
    get_tree().change_scene_to_file(path)
    return true
```

## 参考
- [Godot 文档: SceneTree](https://docs.godotengine.org/en/stable/classes/class_scenetree.html)
- [Godot 文档: 后台加载](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html)


### 相关
- 主要技能: [godot-master](../godot-master/SKILL.md)
