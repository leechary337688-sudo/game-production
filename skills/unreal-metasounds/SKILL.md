---
名称：虚幻引擎MetaSounds
描述：用于程序化音频、实时合成和高级音频图的虚幻引擎MetaSounds技能。
允许工具：读取、搜索、写入、Bash、编辑、全局、网络获取
---

# 虚幻MetaSounds技能

虚幻引擎的程序化音频系统MetaSounds。

## 概述

此技能提供使用虚幻引擎MetaSounds系统实现程序化音频的能力。

## 能力

### 音频图
- 创建MetaSound源
- 构建音频处理图
- 处理触发器和参数
- 实现自定义节点

### 合成
- 使用振荡器
- 实现滤波器
- 创建包络
- 处理调制

### 程序化音频
- 生成音效
- 创建自适应音乐
- 实现音频变化
- 处理随机化

### 集成
- 从游戏玩法触发
- 控制参数
- 处理空间化
- 管理性能

## 先决条件

- 虚幻引擎5.0+
- 启用MetaSounds插件

## 使用模式

### MetaSound源

```
1. 创建MetaSound源
2. 添加输入参数
3. 构建音频图
4. 配置输出
5. 在Sound Cue中或直接使用
```

### 参数控制

```cpp
UAudioComponent* AudioComp = CreateAudioComponent();
AudioComp->SetFloatParameter(FName("强度"), 0.8f);
AudioComp->SetTriggerParameter(FName("击中时"));
```

## 最佳实践

1. 为常见模式使用预设
2. 分析CPU使用情况
3. 处理语音管理
4. 使用组进行组织
5. 在所有平台上测试

## 参考

- [MetaSounds文档](https://docs.unrealengine.com/5.0/en-US/metasounds-in-unreal-engine/)
