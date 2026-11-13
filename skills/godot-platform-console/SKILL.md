---
name: godot-platform-console
description: "专家蓝图，面向控制台平台（PlayStation、Xbox、Nintendo Switch），涵盖控制器优先的UI、认证要求（TRCs/TCRs）、平台服务（成就、云存档）和性能合规性。适用于目标控制台发布或实现仅手柄接口时。关键词：控制台、PlayStation、Xbox、Switch、TRC、TCR、认证、控制器、手柄、成就。"
---

# 平台：控制台

控制器优先设计、认证合规性和锁定的帧率定义了控制台开发。

## 可用脚本

### [console_compliance_handler.gd](scripts/console_compliance_handler.gd)
专家控制台认证助手（焦点丢失处理、保存指示器）。

## 控制台开发中的不要做事项

- **永不显示鼠标光标** — 控制台上显示鼠标 = 认证失败。仅使用控制器。使用 `Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)` 隐藏光标。
- **永不在焦点丢失时跳过暂停** — 用户按Home键而未暂停 = TRC违规。监听 `NOTIFICATION_APPLICATION_FOCUS_OUT`，强制暂停。
- **永不使用未锁定的帧率** — 可变FPS = 屏幕撕裂 + 认证失败。锁定到30或60 FPS：`Engine.max_fps = 60` + VSync。
- **永不忘记D-Pad导航** — UI仅通过模拟摇杆可导航？无障碍性失败。必须支持所有菜单的D-Pad导航。
- **永不硬编码按钮标签** — “按A”在PlayStation上显示错误的图标。使用 `Input.get_joy_button_string()` 或平台特定的图标映射。
- **永不超出平台内存限制** — Switch有约3.5GB可用RAM。超出 = 崩溃/拒绝。使用Godot Profiler→Memory标签进行分析。

---

- **始终显示按钮提示** (A/B/X/Y 或 ⬜/✕/△/○)
- **D-Pad导航** 用于所有菜单
- **后退按钮支持** (B/○)
- **无鼠标光标**

## 输入处理

```gdscript
func _input(event: InputEvent) -> void:
    if event is InputEventJoypadButton:
        match event.button_index:
            JOY_BUTTON_A:
                on_confirm()
            JOY_BUTTON_B:
                on_cancel()
```

## 性能要求

- **锁定30/60 FPS** - 不允许掉帧
- **内存限制** - 严格预算
- **认证测试** - 需要QA

## 平台服务

- 成就/奖杯
- 云存档
- 多人匹配
- 平台好友

## 最佳实践

1. **仅控制器** - 无鼠标/键盘
2. **焦点丢失时暂停** - 必需
3. **保存提示** - 必须通知保存
4. **认证** - 遵循TRCs/TCRs

## 参考
- 相关：`godot-export-builds`, `godot-input-handling`


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
