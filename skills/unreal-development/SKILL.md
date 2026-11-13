---
名称：虚幻引擎开发
描述：用于C++/蓝图开发的虚幻引擎集成技能，包括Actor生命周期管理、插件开发和编辑器自动化。使LLM能够通过MCP服务器与虚幻编辑器交互，进行关卡操作、蓝图生成和自动化工作流。
允许工具：读取、搜索、写入、Bash、编辑、全局搜索、网络获取
---

# 虚幻引擎开发技能

全面的虚幻引擎开发集成，用于AI辅助游戏创作、编辑器自动化和项目管理。

## 概述

此技能提供与虚幻引擎项目交互的能力，包括C++开发、蓝图可视化脚本、Actor管理和构建自动化。当可用时，它利用虚幻MCP生态系统进行直接编辑器集成。

## 能力

### 项目管理
- 创建和配置虚幻项目
- 管理项目设置（项目设置、DefaultEngine.ini等）
- 配置插件依赖项
- 为代码组织设置模块结构

### C++开发
- 使用适当的UCLASS宏生成Actor和组件类
- 创建具有反射支持的UObject子类
- 实现接口（UInterface）
- 编写自定义编辑器模块
- 使用自动化框架生成单元测试

### 蓝图可视化脚本
- 根据规范生成蓝图类
- 创建蓝图函数库
- 设计蓝图接口
- 构建可重用的蓝图宏
- 生成仅数据蓝图

### Actor和组件系统
- 以编程方式创建和修改Actor
- 设计组件层次结构
- 实现Tick和生命周期管理
- 为多人游戏设置Actor复制

### 关卡设计
- 创建和修改关卡
- 放置Actor并配置属性
- 设置关卡流
- 配置世界分区设置

### 构建系统
- 为多个平台配置构建设置
- 使用BuildGraph创建构建脚本
- 设置CI/CD流水线
- 管理平台特定配置

## 先决条件

### 虚幻引擎安装
- 推荐虚幻引擎5.0或更高版本
- 带有C++游戏开发工作负载的Visual Studio 2022
- 用于工具的.NET 6.0 SDK

### MCP服务器（推荐）
用于直接虚幻编辑器集成：

```json
{
  "mcpServers": {
    "unreal": {
      "command": "python",
      "args": ["-m", "unreal_mcp"],
      "env": {
        "UNREAL_PROJECT_PATH": "/path/to/project.uproject"
      }
    }
  }
}
```

替代MCP服务器：
- `UnrealMCP` (kvick-games) - 带有JSON命令的TCP服务器
- `unreal-mcp` (chongdashu) - 自然语言控制
- `Unreal_mcp` (ChiR24) - C++自动化桥接

## 使用模式

### 创建Actor类（C++）

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

UCLASS()
class MYGAME_API AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    float MoveSpeed = 600.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
    float JumpHeight = 420.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class UCameraComponent* CameraComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    class USpringArmComponent* SpringArmComponent;

private:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void StartJump();
    void StopJump();
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建弹簧臂
    SpringArmComponent = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
    SpringArmComponent->SetupAttachment(RootComponent);
    SpringArmComponent->TargetArmLength = 400.0f;
    SpringArmComponent->bUsePawnControlRotation = true;

    // 创建相机
    CameraComponent = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    CameraComponent->SetupAttachment(SpringArmComponent);

    // 配置移动
    GetCharacterMovement()->MaxWalkSpeed = MoveSpeed;
    GetCharacterMovement()->JumpZVelocity = JumpHeight;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
}

void AMyCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AMyCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    PlayerInputComponent->BindAxis("MoveForward", this, &AMyCharacter::MoveForward);
    PlayerInputComponent->BindAxis("MoveRight", this, &AMyCharacter::MoveRight);
    PlayerInputComponent->BindAction("Jump", IE_Pressed, this, &AMyCharacter::StartJump);
    PlayerInputComponent->BindAction("Jump", IE_Released, this, &AMyCharacter::StopJump);
}

void AMyCharacter::MoveForward(float Value)
{
    if (Value != 0.0f)
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);
        const FVector Direction = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        AddMovementInput(Direction, Value);
    }
}

void AMyCharacter::MoveRight(float Value)
{
    if (Value != 0.0f)
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);
        const FVector Direction = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
        AddMovementInput(Direction, Value);
    }
}

void AMyCharacter::StartJump()
{
    Jump();
}

void AMyCharacter::StopJump()
{
    StopJumping();
}
```

### 创建数据资产（C++）

```cpp
// EnemyDataAsset.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "EnemyDataAsset.generated.h"

UENUM(BlueprintType)
enum class EEnemyType : uint8
{
    Melee,
    Ranged,
    Boss
};

UCLASS(BlueprintType)
class MYGAME_API UEnemyDataAsset : public UPrimaryDataAsset
{
    GENERATED_BODY()

public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Basic Info")
    FString EnemyName;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Basic Info")
    EEnemyType EnemyType;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
    float MaxHealth = 100.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
    float MoveSpeed = 300.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
    float AttackDamage = 10.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Combat")
    float AttackRange = 150.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Visuals")
    TObjectPtr<USkeletalMesh> Mesh;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Visuals")
    TObjectPtr<UAnimBlueprint> AnimBlueprint;

    // UPrimaryDataAsset接口
    virtual FPrimaryAssetId GetPrimaryAssetId() const override;
};
```

### 游戏能力系统示例

```cpp
// MyGameplayAbility.h
#pragma once

#include "CoreMinimal.h"
#include "Abilities/GameplayAbility.h"
#include "MyGameplayAbility.generated.h"

UCLASS()
class MYGAME_API UMyGameplayAbility : public UGameplayAbility
{
    GENERATED_BODY()

public:
    UMyGameplayAbility();

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Ability")
    float CooldownDuration = 1.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Ability")
    float ManaCost = 10.0f;

protected:
    virtual void ActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        const FGameplayEventData* TriggerEventData) override;

    virtual void EndAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        bool bReplicateEndAbility,
        bool bWasCancelled) override;
};
```

## 与Babysitter SDK集成

### 任务定义示例

```javascript
const unrealActorTask = defineTask({
  name: 'unreal-actor-generation',
  description: '生成虚幻引擎Actor类',

  inputs: {
    actorType: { type: 'string', required: true }, // Character, Pawn, Actor
    className: { type: 'string', required: true },
    components: { type: 'array', required: true },
    outputPath: { type: 'string', required: true }
  },

  outputs: {
    headerPath: { type: 'string' },
    sourcePath: { type: 'string' },
    success: { type: 'boolean' }
  },

  async run(inputs, taskCtx) {
    return {
      kind: 'skill',
      title: `生成虚幻Actor: ${inputs.className}`,
      skill: {
        name: 'unreal-development',
        context: {
          operation: 'generate_actor',
          actorType: inputs.actorType,
          className: inputs.className,
          components: inputs.components,
          outputPath: inputs.outputPath
        }
      },
      io: {
        inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
        outputJsonPath: `tasks/${taskCtx.effectId}/result.json`
      }
    };
  }
});
```

## MCP服务器集成

### 可用MCP工具（通过unreal-mcp）

| 工具 | 描述 |
|------|-------------|
| `unreal_spawn_actor` | 在关卡中生成Actor |
| `unreal_modify_actor` | 修改Actor属性 |
| `unreal_create_blueprint` | 生成蓝图类 |
| `unreal_compile` | 触发热重载/编译 |
| `unreal_build` | 为目标平台构建 |
| `unreal_run_automation` | 执行自动化测试 |
| `unreal_query_level` | 获取关卡结构 |
| `unreal_python_exec` | 执行虚幻Python命令 |

### 配置

```json
{
  "mcpServers": {
    "unreal": {
      "command": "python",
      "args": ["-m", "unreal_mcp"],
      "env": {
        "UNREAL_PROJECT_PATH": "C:/Projects/MyGame/MyGame.uproject",
        "UNREAL_ENGINE_PATH": "C:/Program Files/Epic Games/UE_5.3"
      }
    }
  }
}
```

## 最佳实践

1. **UCLASS宏**：始终使用适当的说明符（BlueprintType、Blueprintable等）
2. **属性说明符**：正确使用EditAnywhere/VisibleAnywhere和BlueprintReadWrite/BlueprintReadOnly
3. **复制**：使用UPROPERTY(Replicated)标记复制属性
4. **内存管理**：使用TObjectPtr处理对象指针，避免原始指针
5. **模块**：将代码组织到具有清晰依赖关系的逻辑模块中
6. **Tick优化**：仅在必要时启用tick，对周期性任务使用定时器

## 平台考虑

| 平台 | 关键考虑因素 |
|----------|-------------------|
| PC | 完整功能支持，着色器模型5+ |
| 游戏机 | 内存预算，认证要求 |
| 移动端 | 简化渲染，热管理 |
| VR | 帧率要求，防晕动症 |

## 参考

- [虚幻引擎文档](https://dev.epicgames.com/documentation/)
- [UnrealMCP (kvick-games)](https://github.com/kvick-games/UnrealMCP)
- [unreal-mcp (chongdashu)](https://github.com/chongdashu/unreal-mcp)
- [Unreal_mcp (ChiR24)](https://github.com/ChiR24/Unreal_mcp)
- [ClaudeAI Plugin for UE5](https://claudeaiplugin.com/)
- [虚幻C++文档](https://docs.unrealengine.com/5.0/en-US/programming-with-cplusplus-in-unreal-engine/)
