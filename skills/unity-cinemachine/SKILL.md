---
name: unity-cinemachine
description: Unity Cinemachine 技能，用于虚拟摄像机、程序化摄像机控制和电影序列。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity Cinemachine 技能

使用 Unity Cinemachine 的程序化摄像机系统。

## 概述

此技能提供使用 Cinemachine 实现动态摄像机系统的能力，包括虚拟摄像机、摄像机混合和电影序列。

## 能力

### 虚拟摄像机
- 为不同视图创建虚拟摄像机
- 配置跟随目标和注视目标
- 设置取景变换器
- 实现轨道摄像机

### 摄像机行为
- 配置抖动噪声配置文件
- 实现死区和软区
- 设置摄像机碰撞
- 处理屏幕构图

### 混合与过渡
- 配置混合曲线
- 设置摄像机优先级
- 使用时间线实现过场动画
- 处理状态驱动摄像机

### 高级功能
- 创建轨道路径
- 实现目标组
- 设置清晰镜头
- 配置限制器扩展

## 先决条件

- Unity 2021.3+
- 已安装 Cinemachine 包

## 使用模式

### 玩家跟随摄像机

```csharp
// 在编辑器或通过脚本配置
var vcam = GetComponent<CinemachineVirtualCamera>();
vcam.Follow = playerTransform;
vcam.LookAt = playerTransform;

// 取景变换器设置
var transposer = vcam.GetCinemachineComponent<CinemachineFramingTransposer>();
transposer.m_ScreenX = 0.5f;
transposer.m_ScreenY = 0.4f;
```

### 摄像机抖动

```csharp
public void TriggerShake(float intensity, float duration)
{
    var noise = vcam.GetCinemachineComponent<CinemachineBasicMultiChannelPerlin>();
    noise.m_AmplitudeGain = intensity;
    StartCoroutine(ResetShake(duration));
}
```

## 最佳实践

1. 为游戏状态使用虚拟摄像机
2. 配置适当的优先级
3. 测试摄像机过渡
4. 使用时间线处理过场动画
5. 分析摄像机更新性能

## 参考

- [Cinemachine 文档](https://docs.unity3d.com/Packages/com.unity.cinemachine@latest)
