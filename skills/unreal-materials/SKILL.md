---
name: unreal-materials
description: 用于PBR工作流、材质实例、着色器复杂度和材质函数的虚幻引擎材质编辑器技能。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# 虚幻引擎材质技能

使用虚幻引擎材质编辑器进行材质开发。

## 概述

本技能提供了在虚幻引擎中创建材质的能力，包括PBR工作流、材质实例和自定义着色器开发。

## 能力

### 材质创建
- 构建PBR材质
- 配置材质域
- 处理混合模式
- 管理材质属性

### 材质实例
- 创建实例层级结构
- 暴露参数
- 处理静态开关
- 管理实例覆盖

### 材质函数
- 创建可重用函数
- 构建材质层
- 处理函数输入
- 管理函数库

### 高级技术
- 世界位置偏移
- 像素深度偏移
- 自定义UV操作
- 次表面散射

## 前提条件

- 虚幻引擎5.0+
- 材质编辑器知识

## 使用模式

### 材质参数设置

```
1. 创建材质参数集合
2. 定义标量/向量参数
3. 在材质中引用
4. 从蓝图/C++更新
```

### 动态材质实例

```cpp
UMaterialInstanceDynamic* DynMat =
    UMaterialInstanceDynamic::Create(BaseMaterial, this);
DynMat->SetScalarParameterValue(FName("Damage"), DamageAmount);
MeshComponent->SetMaterial(0, DynMat);
```

### 材质层

```
1. 创建材质层资产
2. 定义层参数
3. 创建材质层混合
4. 配置混合
5. 在材质中使用
```

## 最佳实践

1. 使用材质实例处理变体
2. 创建材质函数以实现重用
3. 监控着色器复杂度
4. 使用LOD材质切换
5. 使用GPU可视化器进行分析

## 参考资料

- [材质文档](https://docs.unrealengine.com/5.0/en-US/unreal-engine-materials/)
