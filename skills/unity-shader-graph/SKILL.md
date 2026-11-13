---
名称: unity-shader-graph
描述: 用于可视化着色器创作、自定义节点和材质效果的Unity Shader Graph技能。
允许使用的工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity Shader Graph 技能

使用Unity Shader Graph进行可视化着色器开发。

## 概述

本技能提供了使用Unity的Shader Graph可视化创建着色器的能力，使美术师和开发者无需编写代码即可构建复杂的材质。

## 能力

### 可视化创作
- 为URP/HDRP创建着色器图
- 连接节点以实现材质逻辑
- 实时预览效果
- 处理着色器变体

### 效果类型
- 表面着色器（光照、无光照）
- 顶点位移
- UV操作
- 程序化纹理

### 自定义开发
- 创建自定义节点
- 构建子图
- 实现着色器关键字
- 处理多通道渲染

### 材质系统
- 从图生成材质
- 暴露材质属性
- 处理纹理采样
- 实现三平面映射

## 先决条件

- Unity 2021.3+
- Shader Graph包
- URP或HDRP项目

## 使用模式

### 常见节点模式

```
溶解效果:
噪波 → 阶跃 → Alpha裁剪阈值 → Alpha

边缘光:
菲涅尔效应 → 相乘 → 添加自发光

滚动UV:
时间 → 相乘 → 添加UV → 采样纹理

顶点动画:
噪波 → 位置偏移 → 位置
```

### 自定义函数节点

```hlsl
// 用于Shader Graph的自定义HLSL函数
void MyCustomFunction_float(float3 输入, out float3 输出)
{
    输出 = 输入 * 2.0;
}
```

## 最佳实践

1. 使用子图实现可复用模式
2. 尽量减少纹理采样
3. 使用着色器关键字处理变体
4. 在目标平台上进行性能分析
5. 记录暴露的属性

## 参考资料

- [Shader Graph文档](https://docs.unity3d.com/Packages/com.unity.shadergraph@latest)
