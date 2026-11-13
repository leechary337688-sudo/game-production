---
name: unreal-cpp
description: Unreal Engine C++编程技能，涵盖UCLASS宏、反射系统、垃圾回收和引擎集成。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unreal C++ 技能

用于虚幻引擎开发的C++编程。

## 概述

本技能提供了使用C++实现虚幻引擎游戏逻辑和系统的能力，包括反射系统、宏和引擎集成。

## 能力范围

### UCLASS 系统
- 实现 UCLASS 宏
- 处理 UPROPERTY 说明符
- 创建 UFUNCTION 方法
- 管理 USTRUCT 类型

### 内存管理
- 使用智能指针
- 处理垃圾回收
- 管理对象生命周期
- 实现弱引用

### 引擎集成
- 创建 Actor 类
- 实现组件
- 处理子系统
- 创建插件

### 蓝图暴露
- 将C++暴露给蓝图
- 处理 BlueprintCallable
- 实现 BlueprintNativeEvent
- 创建蓝图函数库

## 先决条件

- Unreal Engine 5.0+
- Visual Studio 2022 / Rider
- C++ 编程知识

## 使用模式

### Actor 类

```cpp
UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float Health = 100.f;

    UFUNCTION(BlueprintCallable, Category = "Combat")
    void TakeDamage(float Damage);

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
};
```

### 组件

```cpp
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UHealthComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintAssignable)
    FOnHealthChanged OnHealthChanged;

    UFUNCTION(BlueprintCallable)
    void ModifyHealth(float Delta);

private:
    UPROPERTY(EditDefaultsOnly)
    float MaxHealth = 100.f;

    float CurrentHealth;
};
```

## 最佳实践

1. 使用 UPROPERTY 确保垃圾回收可见性
2. 尽可能使用前向声明
3. 使用接口进行解耦
4. 使用 Unreal Insights 进行性能分析
5. 遵循虚幻引擎编码标准

## 参考资料

- [Unreal C++ 文档](https://docs.unrealengine.com/5.0/en-US/programming-with-cplusplus-in-unreal-engine/)
