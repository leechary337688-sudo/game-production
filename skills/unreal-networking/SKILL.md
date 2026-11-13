---
name: unreal-networking
description: 虚幻引擎网络技能，涵盖复制、RPC、相关性及专用服务器架构。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unreal Networking 技能

虚幻引擎多人游戏网络。

## 概述

本技能提供了使用虚幻引擎内置网络系统实现多人游戏的能力。

## 能力

### 复制
- 配置复制属性
- 处理复制条件
- 管理复制优先级
- 实现自定义复制

### 远程过程调用
- 实现服务器 RPC
- 创建客户端 RPC
- 处理多播 RPC
- 管理 RPC 可靠性

### 权限与相关性
- 处理服务器权限
- 配置网络相关性
- 管理 Actor 所有权
- 实现客户端预测

### 专用服务器
- 构建专用服务器目标
- 处理无头模式
- 管理服务器性能
- 实现会话管理

## 前提条件

- 虚幻引擎 5.0+
- 网络知识

## 使用模式

### 复制属性

```cpp
UPROPERTY(ReplicatedUsing=OnRep_Health)
float Health;

UFUNCTION()
void OnRep_Health()
{
    // 当 Health 在客户端上发生变化时调用
    UpdateHealthUI();
}

void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    DOREPLIFETIME(AMyCharacter, Health);
}
```

### RPC 实现

```cpp
UFUNCTION(Server, Reliable, WithValidation)
void Server_Fire(FVector Location, FRotator Rotation);

bool Server_Fire_Validate(FVector Location, FRotator Rotation)
{
    return true; // 添加验证
}

void Server_Fire_Implementation(FVector Location, FRotator Rotation)
{
    // 在服务器上执行
}
```

## 最佳实践

1. 验证所有服务器 RPC
2. 最小化复制属性
3. 明智地使用相关性
4. 使用模拟延迟进行测试
5. 分析网络带宽

## 参考资料

- [网络文档](https://docs.unrealengine.com/5.0/en-US/networking-and-multiplayer-in-unreal-engine/)
