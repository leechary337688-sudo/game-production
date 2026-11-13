---
name: unreal-gamesframework
description: 虚幻引擎游戏玩法能力系统（GAS）技能，用于属性、能力和游戏效果。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# 虚幻引擎GAS技能

虚幻引擎游戏玩法能力系统。

## 概述

本技能提供使用虚幻引擎游戏玩法能力系统（GAS）实现复杂游戏玩法系统的能力。

## 功能

### 能力
- 创建游戏玩法能力
- 处理能力激活
- 管理能力消耗
- 实现冷却时间

### 属性
- 定义属性集
- 处理属性修饰符
- 实现派生属性
- 管理属性复制

### 游戏效果
- 创建即时效果
- 实现持续时间效果
- 处理堆叠效果
- 管理效果移除

### 集成
- 实现能力任务
- 处理能力事件
- 创建能力标签
- 管理能力实例

## 先决条件

- 虚幻引擎5.0+
- 已启用GameplayAbilities插件

## 使用模式

### 属性集

```cpp
UCLASS()
class UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_Health)
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_MaxHealth)
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)
};
```

### 游戏玩法能力

```cpp
UCLASS()
class UGA_Attack : public UGameplayAbility
{
    GENERATED_BODY()

protected:
    virtual void ActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        const FGameplayEventData* TriggerEventData) override;
};
```

## 最佳实践

1. 广泛使用标签
2. 保持能力模块化
3. 正确处理预测
4. 彻底测试多人游戏
5. 记录能力交互

## 参考资料

- [GAS文档](https://docs.unrealengine.com/5.0/en-US/gameplay-ability-system-for-unreal-engine/)
