---
name: godot-shaders
description: Godot着色器语言技能，用于视觉着色器、自定义渲染和材质效果。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Godot着色器技能

用于Godot引擎的着色器开发。

## 概述

本技能提供使用Godot着色语言和视觉着色器系统创建着色器的能力。

## 能力范围

### 着色器类型
- 空间着色器（3D）
- 画布项目着色器（2D）
- 粒子着色器
- 天空着色器

### 视觉着色器
- 基于节点的创作
- 自定义节点
- 着色器预设
- 导出为代码

### 着色器语言
- 类GLSL语法
- 内置函数
- 统一变量和可变变量
- 渲染模式

### 效果
- 后处理
- 材质效果
- 屏幕空间效果
- 程序化纹理

## 先决条件

- Godot 4.0+
- 着色器知识

## 使用模式

### 空间着色器

```glsl
shader_type spatial;

uniform vec4 albedo_color : source_color = vec4(1.0);
uniform float metallic : hint_range(0, 1) = 0.0;
uniform float roughness : hint_range(0, 1) = 0.5;

void fragment() {
    ALBEDO = albedo_color.rgb;
    METALLIC = metallic;
    ROUGHNESS = roughness;
}
```

### 画布项目着色器

```glsl
shader_type canvas_item;

uniform float outline_width = 2.0;
uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);

void fragment() {
    vec4 color = texture(TEXTURE, UV);
    // 轮廓逻辑
    COLOR = color;
}
```

## 最佳实践

1. 使用视觉着色器进行原型设计
2. 优化纹理采样
3. 谨慎处理精度
4. 分析着色器复杂度
5. 在目标硬件上测试

## 参考资料

- [Godot着色器](https://docs.godotengine.org/en/stable/tutorials/shaders/)
