---
name: hlsl
description: 用于DirectX、计算着色器和优化的HLSL着色器编程技能。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# HLSL 技能

用于基于DirectX引擎的HLSL着色器编程。

## 概述

此技能提供为基于DirectX的引擎编写HLSL着色器的能力。

## 能力

- 顶点和像素着色器
- 计算着色器
- 常量缓冲区管理
- 着色器优化

## 使用模式

```hlsl
cbuffer ConstantBuffer : register(b0)
{
    float4x4 WorldViewProj;
}

float4 PSMain(PSInput input) : SV_TARGET
{
    return input.Color;
}
```

## 参考资料

- [HLSL 文档](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/)
