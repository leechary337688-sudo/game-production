---
名称：虚幻引擎序列器
描述：用于电影、镜头剪辑和游戏内过场动画的虚幻引擎序列器技能。
允许使用的工具：读取、全局正则表达式打印、写入、Bash、编辑、全局匹配、网络获取
---

# 虚幻引擎序列器技能

用于虚幻引擎中电影和过场动画的序列器。

## 概述

本技能提供使用虚幻引擎序列器创建电影的能力，包括镜头工作、角色动画和事件触发。

## 能力

### 序列创建
- 创建关卡序列
- 管理主序列
- 处理序列层级结构
- 实现序列播放器

### 镜头工作
- 创建镜头剪辑
- 实现镜头轨道
- 处理镜头动画
- 管理镜头绑定

### 角色动画
- 关键帧角色变换
- 处理骨骼动画
- 实现音频轨道
- 管理事件触发器

### 集成
- 从游戏玩法触发
- 处理序列事件
- 实现绑定覆盖
- 管理序列过渡

## 前提条件

- 虚幻引擎5.0+
- 序列器（内置）

## 使用模式

### 关卡序列设置

```cpp
// 从代码播放序列
ULevelSequence* Sequence = LoadSequence();
ALevelSequenceActor* SequenceActor;
ULevelSequencePlayer* Player =
    ULevelSequencePlayer::CreateLevelSequencePlayer(
        GetWorld(),
        Sequence,
        FMovieSceneSequencePlaybackSettings(),
        SequenceActor
    );
Player->Play();
```

### 事件轨道

```
1. 向序列添加事件轨道
2. 在所需时间添加关键帧
3. 在蓝图中创建事件
4. 将事件绑定到函数
```

## 最佳实践

1. 使用主序列进行组织
2. 小心处理绑定
3. 测试序列加载
4. 管理长序列的内存
5. 分析播放性能

## 参考资料

- [序列器文档](https://docs.unrealengine.com/5.0/en-US/sequencer-editor-unreal-engine/)
