---
名称: unity-vfx-graph
描述: Unity视觉特效图技能，用于GPU粒子系统、程序化效果和高性能视觉特效。
允许工具: 读取、Grep、写入、Bash、编辑、Glob、WebFetch
---

# Unity VFX Graph 技能

用于Unity中GPU加速粒子系统的视觉特效图开发。

## 概述

本技能提供使用Unity视觉特效图创建高性能视觉特效的能力，利用GPU计算处理数百万粒子。

## 能力

### 粒子系统
- 创建GPU粒子系统
- 配置生成、初始化、更新、输出上下文
- 处理粒子属性
- 实现粒子碰撞

### 程序化效果
- 使用噪声和湍流
- 实现基于SDF的效果
- 创建网格采样效果
- 构建基于摄像头的交互

### 视觉创作
- 在VFX Graph编辑器中设计效果
- 创建子图以供重用
- 实现属性表
- 构建事件驱动效果

### 集成
- 连接到C#脚本
- 处理事件和参数
- 与Timeline集成
- 管理性能预算

## 前提条件

- Unity 2021.3+ 并安装VFX Graph包
- SRP（URP或HDRP）项目
- 支持计算着色器的硬件

## 使用模式

### 从代码生成粒子

```csharp
public class VFXController : MonoBehaviour
{
    [SerializeField] private VisualEffect vfx;

    void Start()
    {
        // 设置属性
        vfx.SetFloat("SpawnRate", 100f);
        vfx.SetVector3("EmitterPosition", transform.position);
    }

    public void TriggerBurst()
    {
        // 发送事件
        vfx.SendEvent("OnBurst");
    }
}
```

### 属性绑定

```csharp
// 通过C#绑定暴露VFX属性
vfx.SetInt("ParticleCount", 1000);
vfx.SetGradient("ColorOverLife", gradient);
vfx.SetTexture("ParticleTexture", texture);
```

## 最佳实践

1. 使用子图实现可重用组件
2. 分析GPU性能
3. 设置粒子数量限制
4. 对远处效果使用LOD
5. 优化纹理采样

## 参考

- [VFX Graph 文档](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@latest)
