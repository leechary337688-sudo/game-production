---
name: unreal-lumen
description: Unreal Engine Lumen 技能，用于全局光照、反射和动态照明。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unreal Lumen 技能

用于虚幻引擎的 Lumen 全局光照和反射。

## 概述

此技能提供在虚幻引擎中实现 Lumen 动态全局光照和反射的能力。

## 能力

### 全局光照
- 配置 Lumen GI 设置
- 处理最终聚集
- 管理无限次反弹
- 优化追踪设置

### 反射
- 配置反射方法
- 处理屏幕追踪
- 管理反射捕获
- 优化质量设置

### 集成
- 与 Nanite 结合
- 处理自发光材质
- 管理天光
- 配置曝光

### 性能
- 硬件光线追踪选项
- 软件光线追踪回退
- 场景复杂度处理
- 平台可扩展性

## 先决条件

- 虚幻引擎 5.0+
- 现代 GPU（如需硬件光线追踪，需 RTX）

## 使用模式

### 项目设置

```
Lumen 全局光照：
- 在项目设置中启用
- 配置最终聚集质量
- 设置追踪距离
- 配置场景细节
```

### 后期处理体积

```
1. 添加后期处理体积
2. 启用无限范围
3. 配置 Lumen 设置
4. 按区域调整质量
```

## 最佳实践

1. 对小光源使用自发光
2. 保持场景光照充足
3. 避免过暗区域
4. 使用 Lumen 可视化工具进行分析
5. 测试软件和硬件光线追踪

## 参考资料

- [Lumen 文档](https://docs.unrealengine.com/5.0/en-US/lumen-global-illumination-and-reflections-in-unreal-engine/)
