---
name: unity-urp
description: Unity通用渲染管线配置技能，包括自定义着色器、光照设置、后期处理效果和渲染功能开发。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity URP 技能

为Unity项目提供全面的通用渲染管线配置与定制能力。

## 概述

本技能提供配置和扩展Unity通用渲染管线的能力，包括着色器开发、光照配置、后期处理设置和自定义渲染功能实现。

## 能力范围

### 管线配置
- 为不同质量等级配置URP资产设置
- 设置渲染器功能和渲染通道
- 配置全局渲染设置
- 管理管线资产变体

### 着色器开发
- 使用Shader Graph创建URP兼容的着色器
- 为URP编写自定义HLSL着色器
- 实现着色器变体和关键字
- 针对目标平台优化着色器

### 光照设置
- 配置实时和烘焙光照
- 设置反射探针和光照探针
- 实现屏幕空间环境光遮蔽
- 配置阴影和级联阴影

### 后期处理
- 设置后期处理体积配置文件
- 配置辉光、色彩分级、暗角等效果
- 实现自定义后期处理效果
- 管理体积混合和优先级

### 渲染功能
- 创建自定义渲染功能
- 实现可编程渲染通道
- 处理渲染目标和缓冲区
- 与现有管线集成

## 前提条件

- Unity 2021.3+ 并安装URP包
- 通过包管理器安装URP包
- 对渲染概念有基本理解

## 使用模式

### 创建URP Shader Graph

```
1. 创建新的Shader Graph（创建 > Shader Graph > URP > 光照着色器图）
2. 配置表面选项（不透明/透明）
3. 添加所需效果的节点
4. 连接到主堆栈输出
5. 保存并应用到材质
```

### 自定义渲染功能

```csharp
public class OutlineRenderFeature : ScriptableRendererFeature
{
    [System.Serializable]
    public class Settings
    {
        public RenderPassEvent renderPassEvent = RenderPassEvent.AfterRenderingOpaques;
        public Material outlineMaterial;
    }

    public Settings settings = new Settings();
    private OutlineRenderPass renderPass;

    public override void Create()
    {
        renderPass = new OutlineRenderPass(settings);
    }

    public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
    {
        renderer.EnqueuePass(renderPass);
    }
}
```

## 与Babysitter SDK集成

```javascript
const urpSetupTask = defineTask({
  name: 'urp-configuration',
  description: '配置URP设置',

  inputs: {
    qualityTier: { type: 'string', required: true },
    features: { type: 'array', required: true }
  },

  async run(inputs, taskCtx) {
    return {
      kind: 'skill',
      title: '配置URP管线',
      skill: {
        name: 'unity-urp',
        context: {
          operation: 'configure_pipeline',
          qualityTier: inputs.qualityTier,
          features: inputs.features
        }
      }
    };
  }
});
```

## 最佳实践

1. 为不同平台创建质量等级变体
2. 使用Shader Graph创建可维护的着色器
3. 分析渲染通道性能
4. 使用SRP批处理器兼容的着色器
5. 最小化过度绘制和填充率

## 参考资料

- [URP文档](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@latest)
- [Shader Graph手册](https://docs.unity3d.com/Packages/com.unity.shadergraph@latest)
