---
名称: unity-input-system
描述: Unity新输入系统配置技能，用于动作映射、设备绑定、控制方案和跨平台输入处理。
允许工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity 输入系统技能

Unity新输入系统的配置与实现。

## 概述

此技能提供实现Unity新输入系统的能力，包括动作映射、设备支持和跨平台输入处理。

## 能力

### 动作配置
- 创建输入动作资产
- 定义动作映射和动作
- 配置绑定和交互
- 设置动作类型（值、按钮、直通）

### 设备支持
- 配置游戏手柄支持
- 实现键盘/鼠标处理
- 设置触摸控制
- 处理XR控制器

### 控制方案
- 定义控制方案
- 实现方案切换
- 支持本地多人游戏
- 配置设备要求

### 运行时处理
- 生成C#输入类
- 处理输入事件
- 实现重绑定UI
- 管理设备变更

## 前提条件

- Unity 2021.3+
- 已安装输入系统包

## 使用模式

### 输入动作资产

```csharp
// 生成的PlayerInput类用法
public class PlayerController : MonoBehaviour
{
    private PlayerInputActions inputActions;

    void Awake()
    {
        inputActions = new PlayerInputActions();
    }

    void OnEnable()
    {
        inputActions.Gameplay.Enable();
        inputActions.Gameplay.Jump.performed += OnJump;
        inputActions.Gameplay.Move.performed += OnMove;
    }

    void OnDisable()
    {
        inputActions.Gameplay.Disable();
    }

    void OnJump(InputAction.CallbackContext ctx)
    {
        // 处理跳跃
    }

    void OnMove(InputAction.CallbackContext ctx)
    {
        Vector2 movement = ctx.ReadValue<Vector2>();
    }
}
```

### 重绑定

```csharp
public void StartRebinding(InputAction action)
{
    action.PerformInteractiveRebinding()
        .WithControlsExcluding("Mouse")
        .OnComplete(operation => {
            operation.Dispose();
            SaveBindings();
        })
        .Start();
}
```

## 最佳实践

1. 使用输入动作资产而非直接轮询
2. 为实现可访问性实现重绑定
3. 测试所有支持的设备
4. 优雅处理设备断开连接
5. 将自定义绑定保存到PlayerPrefs

## 参考

- [输入系统文档](https://docs.unity3d.com/Packages/com.unity.inputsystem@latest)
