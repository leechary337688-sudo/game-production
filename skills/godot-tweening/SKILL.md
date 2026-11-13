---
name: godot-tweening
description: "专家蓝图，用于使用Tween实现程序化动画，以实现平滑的属性过渡、UI效果、摄像机移动和特效。涵盖缓动函数、并行Tween、链式和生命周期管理。在实现UI动画或程序化运动时使用。关键词：Tween, 缓动, 插值, EASE_IN_OUT, TRANS_CUBIC, tween_property, tween_callback。"
---

# Tween动画

Tween属性动画、缓动曲线、链式和生命周期管理定义了平滑的程序化运动。

## 可用脚本

### [juice_manager.gd](scripts/juice_manager.gd)
专家基于Tween的特效系统，带有可重用效果预设（弹跳、摇晃、脉冲等）。

## 在Tween动画中绝不做的事

- **绝不创建Tween而不杀死之前的** — 点击按钮时创建100个Tween？内存泄漏加冲突动画。在创建新Tween前总是 `if tween: tween.kill()`。
- **绝不使用 `_process` 创建Tween而不调用 `create_tween()`** — 每帧都 `create_tween()`？每秒60帧 × 60次 = 3600个Tween对象。创建一次，重用或杀死旧的。
- **绝不忘记使用 `set_parallel` 实现同时动画** — 链式 `tween_property()` 期望同时发生？默认是顺序的。首先使用 `tween.set_parallel(true)`。
- **绝不使用0时长Tween实现即时变化** — 用 `tween_property(x, 0.0)` 进行传送？Tween系统的开销。直接设置属性：`sprite.position = target`。
- **绝不跳过 `finished` 信号进行清理** — Tween完成，节点仍引用它？内存被持有。连接 `tween.finished` 进行清理或置空引用。
- **绝不使用线性插值于UI** — `TRANS_LINEAR` 用于按钮悬停？机械感。使用 `EASE_OUT + TRANS_QUAD` 或 `EASE_IN_OUT + TRANS_CUBIC` 实现有机运动。

---

```gdscript
extends Sprite2D

func _ready() -> void:
    # 创建Tween
    var tween := create_tween()
    
    # 在2秒内动画位置
    tween.tween_property(self, "position", Vector2(100, 100), 2.0)
```

## Tween方法

### 属性动画

```gdscript
# Tween单个属性
var tween := create_tween()
tween.tween_property($Sprite, "modulate:a", 0.0, 1.0)  # 淡出

# 链式多个Tween
tween.tween_property($Sprite, "position:x", 200, 1.0)
tween.tween_property($Sprite, "position:y", 100, 0.5)
```

### 回调

```gdscript
var tween := create_tween()
tween.tween_property($Sprite, "position", Vector2(100, 0), 1.0)
tween.tween_callback(func(): print("动画完成！"))
tween.tween_callback(queue_free)  # 动画后删除
```

### 间隔

```gdscript
var tween := create_tween()
tween.tween_property($Label, "modulate:a", 0.0, 0.5)
tween.tween_interval(1.0)  # 等待1秒
tween.tween_property($Label, "modulate:a", 1.0, 0.5)
```

## 缓动函数

```gdscript
var tween := create_tween()
tween.set_ease(Tween.EASE_IN_OUT)  # 平滑开始和结束
tween.set_trans(Tween.TRANS_CUBIC)  # 立方曲线
tween.tween_property($Sprite, "position:x", 200, 1.0)
```

**常见组合：**
- `EASE_IN + TRANS_QUAD`：加速
- `EASE_OUT + TRANS_QUAD`：减速
- `EASE_IN_OUT + TRANS_CUBIC`：平滑S曲线
- `EASE_OUT + TRANS_BOUNCE`：弹跳效果

## 高级模式

### 循环动画

```gdscript
var tween := create_tween()
tween.set_loops()  # 无限循环
tween.tween_property($Sprite, "rotation", TAU, 2.0)
```

### 并行Tween

```gdscript
var tween := create_tween()
tween.set_parallel(true)

# 两者同时发生
tween.tween_property($Sprite, "position", Vector2(100, 100), 1.0)
tween.tween_property($Sprite, "scale", Vector2(2, 2), 1.0)
```

### UI按钮悬停效果

```gdscript
extends Button

func _ready() -> void:
    mouse_entered.connect(_on_mouse_entered)
    mouse_exited.connect(_on_mouse_exited)

func _on_mouse_entered() -> void:
    var tween := create_tween()
    tween.tween_property(self, "scale", Vector2(1.1, 1.1), 0.2)

func _on_mouse_exited() -> void:
    var tween := create_tween()
    tween.tween_property(self, "scale", Vector2.ONE, 0.2)
```

### 数字计数器

```gdscript
extends Label

func count_to(target: int, duration: float = 1.0) -> void:
    var current := int(text)
    var tween := create_tween()
    
    tween.tween_method(
        func(value: int): text = str(value),
        current,
        target,
        duration
    )
```

### 摄像机平滑跟随

```gdscript
extends Camera2D

@export var follow_speed := 5.0
var target: Node2D

func _process(delta: float) -> void:
    if target:
        var tween := create_tween()
        tween.tween_property(
            self,
            "global_position",
            target.global_position,
            1.0 / follow_speed
        )
```

## 最佳实践

### 1. 杀死之前Tween

```gdscript
var current_tween: Tween = null

func animate_to(pos: Vector2) -> void:
    if current_tween:
        current_tween.kill()  # 停止之前动画
    
    current_tween = create_tween()
    current_tween.tween_property(self, "position", pos, 1.0)
```

### 2. 使用信号完成

```gdscript
var tween := create_tween()
tween.tween_property($Sprite, "position", Vector2(100, 0), 1.0)
tween.finished.connect(_on_tween_finished)

func _on_tween_finished() -> void:
    print("动画完成！")
```

### 3. 链式实现序列

```gdscript
var tween := create_tween()

# 淡出
tween.tween_property($Sprite, "modulate:a", 0.0, 0.5)
# 不可见时移动
tween.tween_property($Sprite, "position", Vector2(200, 0), 0.0)
# 新位置淡入
tween.tween_property($Sprite, "modulate:a", 1.0, 0.5)
```

## 常见陷阱

**问题**：节点移除时Tween停止
```gdscript
# 解决方案：绑定Tween到SceneTree
var tween := get_tree().create_tween()
tween.tween_property($Sprite, "position", Vector2(100, 0), 1.0)
```

**问题**：多个冲突Tween
```gdscript
# 解决方案：使用单个Tween或杀死之前的
# 总是存储引用以杀死旧Tween
```

## 参考
- [Godot文档：Tween](https://docs.godotengine.org/en/stable/classes/class_tween.html)


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
