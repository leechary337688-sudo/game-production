---
name: unity-addressables
description: Unity Addressables 资源管理技能，用于远程目录、内容更新、资源包和内存高效资源加载。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity Addressables 技能

用于 Unity 项目的可寻址资源管理系统。

## 概述

此技能提供了实现 Unity Addressables 系统的能力，用于高效的资源管理、远程内容交付和内存优化。

## 功能

### 资源组织
- 配置可寻址资源组
- 设置资源标签和地址
- 管理资源组模式和设置
- 按加载行为组织资源

### 远程内容
- 配置远程目录托管
- 设置内容更新工作流
- 管理资源包托管
- 实现 CDN 集成

### 加载策略
- 实现异步资源加载
- 处理加载依赖项
- 使用释放模式管理内存
- 配置预加载策略

### 构建管道
- 配置构建脚本
- 设置内容构建
- 生成目录和资源包
- 管理构建缓存

## 先决条件

- Unity 2021.3+
- 已安装 Addressables 包
- 远程托管设置（可选）

## 使用模式

### 加载资源

```csharp
// 按地址加载
var handle = Addressables.LoadAssetAsync<GameObject>("Prefabs/Player");
handle.Completed += (op) => {
    GameObject player = op.Result;
    Instantiate(player);
};

// 按标签加载
var allEnemies = await Addressables.LoadAssetsAsync<GameObject>(
    "enemies",
    (enemy) => { /* 每个资源的回调 */ }
);
```

### 内存管理

```csharp
// 完成后释放
Addressables.Release(handle);

// 实例管理
var instance = await Addressables.InstantiateAsync("Prefabs/Bullet");
// 稍后...
Addressables.ReleaseInstance(instance);
```

## 最佳实践

1. 按加载上下文对资源进行分组
2. 使用标签处理横切关注点
3. 不再需要时释放资源
4. 尽早使用远程资源包进行测试
5. 使用分析器监控内存

## 参考资料

- [Addressables 文档](https://docs.unity3d.com/Packages/com.unity.addressables@latest)
