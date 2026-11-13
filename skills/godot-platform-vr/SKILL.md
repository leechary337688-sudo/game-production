---
name: godot-platform-vr
description: "VR平台专家蓝图，涵盖XR工具包（OpenXR）、舒适设置（渐晕、快速转向、瞬移）、运动控制、手部追踪和90+ FPS要求。当针对VR头显或实现沉浸式3D体验时使用。关键词：VR, XR, OpenXR, Meta Quest, 晕动症, 舒适, 移动, XRController3D, 注视点渲染。"
---

# 平台：VR

90+ FPS、舒适优先设计和运动控制准确性定义了VR开发。

## 可用脚本

### [vr_physics_hand.gd](scripts/vr_physics_hand.gd)
基于物理的专家手部控制器，具有抓取检测和速度投掷功能。

## 在VR开发中永远不要做的事

- **永远不要低于90 FPS** — 在VR中72 FPS = 立即恶心。必须维持90 FPS最低（Quest 2/3），120 FPS为佳。积极使用Debug → Profiler。
- **永远不要在没有渐晕的情况下使用平滑旋转** — 平滑相机旋转 = 前庭不匹配 = 晕动症。提供快速转向（30°/45°）或在旋转期间使用渐晕。
- **永远不要将UI放得太近或太远** — UI在0.5米处 = 眼睛疲劳，在10米处 = 难以阅读。最佳距离：距离玩家1-3米。
- **永远不要忽略运动到光子的延迟** — >20毫秒延迟 = 手部跟踪可见延迟 = 破坏沉浸感。最小化物理步骤 + 渲染延迟。
- **永远不要跳过瞬移移动选项** — 不是所有人都能忍受平滑移动。必须提供瞬移作为替代方案以实现无障碍。
- **永远不要忘记物理边界** — 玩家在现实世界中撞墙 = 诉讼。使用 `XRServer.get_reference_frame()` 来尊重守护者/陪伴者边界。
- **永远不要使用标准3D音频** — 在VR中使用立体声音频 = 迷惑。使用空间音频（AudioStreamPlayer3D）进行位置声音提示。

---

```gdscript
# Enable XR
func _ready() -> void:
    var xr_interface := XRServer.find_interface("OpenXR")
    if xr_interface and xr_interface.initialize():
        get_viewport().use_xr = true
```

## 舒适设置

- **渐晕**在移动期间
- **快速转向**（30°/45°增量）
- **瞬移移动**选项
- **坐姿模式**支持

## 运动控制

```gdscript
# XRController3D for hands
@onready var left_hand := $XROrigin3D/LeftController
@onready var right_hand := $XROrigin3D/RightController

func _process(delta: float) -> void:
    if left_hand.is_button_pressed("trigger"):
        grab_with_left()
```

## 性能

- **90 FPS最低** - 对舒适性至关重要
- **低延迟** - < 20毫秒运动到光子
- **注视点渲染**如果支持

## 最佳实践

1. **舒适优先** - 预防晕动症
2. **高FPS** - 90+ 要求
3. **物理空间** - 尊重边界
4. **UI距离** - 距离玩家1-3米

## 参考
- 相关：`godot-camera-systems`, `godot-input-handling`


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
