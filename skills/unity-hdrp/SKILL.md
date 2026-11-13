---
name: unity-hdrp
description: Unity的高清渲染管线配置，包括光线追踪、体积效果和高保真图形设置。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity HDRP 技能

用于在Unity中配置高保真图形的高清渲染管线。

## 概述

本技能提供配置和扩展Unity高清渲染管线的能力，支持光线追踪、体积效果和AAA级质量的图形。

## 能力

### 管线配置
- 配置HDRP资源质量设置
- 设置帧设置和渲染功能
- 管理扩散配置文件与材质
- 配置体积框架

### 光线追踪
- 启用光线追踪反射与全局光照
- 配置光线追踪环境光遮蔽
- 设置光线追踪阴影
- 为离线渲染实现路径追踪

### 体积效果
- 配置体积雾与光照
- 设置大气散射
- 实现体积云
- 创建上帝光效果

### 材质系统
- 创建HDRP Lit材质
- 配置次表面散射
- 设置织物与毛发着色器
- 实现贴花投影器

### 光照
- 配置物理光照单位
- 设置区域光与线光源
- 实现天空系统
- 配置反射探针

## 先决条件

- Unity 2021.3+ 并安装HDRP包
- 支持DirectX 12 / Vulkan的硬件
- 光线追踪要求：RTX 2000+ 或同级显卡

## 使用模式

### HDRP材质设置

```csharp
// 配置HDRP Lit材质
var material = new Material(Shader.Find("HDRP/Lit"));
material.SetFloat("_Metallic", 0.8f);
material.SetFloat("_Smoothness", 0.9f);
material.EnableKeyword("_NORMALMAP");
```

### 体积配置

```
1. 创建体积（全局或局部）
2. 添加体积配置文件
3. 添加覆盖设置（雾、曝光等）
4. 配置优先级与混合距离
```

## 最佳实践

1. 使用物理光照单位实现真实光照
2. 尽早分析光线追踪性能
3. 为体积效果创建LOD设置
4. 使用HDRP向导进行项目设置
5. 频繁在目标硬件上测试

## 参考资料

- [HDRP文档](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@latest)
- [HDRP中的光线追踪](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@latest/index.html?subfolder=/manual/Ray-Tracing-Getting-Started.html)
