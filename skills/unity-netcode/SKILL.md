---
name: unity-netcode
description: Unity Netcode for GameObjects 技能，用于多人联机网络、RPC、状态同步和服务器权威游戏玩法。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity Netcode 技能

使用 Unity Netcode for GameObjects 实现多人联机网络。

## 概述

此技能提供了使用 Unity 的 Netcode for GameObjects 实现多人游戏的能力，包括状态同步、RPC 和网络拓扑配置。

## 功能

### 网络架构
- 配置客户端-服务器拓扑
- 设置网络管理器
- 处理玩家生成
- 管理场景加载

### 状态同步
- 实现 NetworkVariables
- 配置同步模式
- 处理预测
- 管理网络变换组件

### 远程过程调用
- 实现 ServerRpc 方法
- 创建 ClientRpc 方法
- 处理 RPC 参数
- 管理 RPC 批处理

### 玩家管理
- 处理玩家连接
- 实现玩家生成
- 管理玩家状态
- 处理断开连接

## 先决条件

- Unity 2021.3+
- Netcode for GameObjects 包
- 传输层（推荐使用 UTP）

## 使用模式

### 网络对象

```csharp
public class PlayerNetworkBehaviour : NetworkBehaviour
{
    private NetworkVariable<int> health = new NetworkVariable<int>(100);

    public override void OnNetworkSpawn()
    {
        if (IsOwner)
        {
            // 初始化所属玩家
        }
    }

    [ServerRpc]
    public void TakeDamageServerRpc(int damage)
    {
        health.Value -= damage;
        if (health.Value <= 0)
        {
            DieClientRpc();
        }
    }

    [ClientRpc]
    private void DieClientRpc()
    {
        // 在所有客户端播放死亡效果
    }
}
```

### 网络管理器设置

```csharp
// 在 NetworkManager 组件中配置
networkManager.ConnectionApprovalCallback = ApprovalCheck;

void ApprovalCheck(NetworkManager.ConnectionApprovalRequest request,
                   NetworkManager.ConnectionApprovalResponse response)
{
    response.Approved = ValidatePlayer(request.Payload);
    response.CreatePlayerObject = true;
}
```

## 最佳实践

1. 使用 NetworkVariables 进行状态管理
2. 在服务器上验证所有 RPC
3. 最小化网络流量
4. 优雅地处理断开连接
5. 使用模拟延迟进行测试

## 参考资料

- [Netcode 文档](https://docs-multiplayer.unity3d.com/)
