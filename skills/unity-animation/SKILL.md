---
名称: unity-animation
描述: 用于Animator控制器、动画装配、时间轴集成和动画状态机的Unity动画技能。
允许工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity动画技能

在Unity中实现和配置动画系统。

## 概述

此技能提供使用Unity的Animator、动画装配和时间轴系统实现角色和对象动画的能力。

## 能力

### Animator控制器
- 创建状态机
- 配置混合树
- 设置动画层
- 处理状态转换

### 动画装配
- 实现IK约束
- 创建程序化动画
- 设置多目标约束
- 处理运行时装配

### 时间轴
- 创建动画片段
- 编排过场动画
- 与Cinemachine集成
- 处理动画事件

### 化身系统
- 配置人形化身
- 设置动画重定向
- 处理肌肉设置
- 管理化身遮罩

## 先决条件

- Unity 2021.3+
- 动画装配包（可选）
- 时间轴包（内置）

## 使用模式

### Animator控制器

```csharp
public class CharacterAnimator : MonoBehaviour
{
    private Animator animator;
    private static readonly int SpeedHash = Animator.StringToHash("Speed");
    private static readonly int JumpTrigger = Animator.StringToHash("Jump");

    void Update()
    {
        float speed = GetMovementSpeed();
        animator.SetFloat(SpeedHash, speed, 0.1f, Time.deltaTime);

        if (Input.GetButtonDown("Jump"))
        {
            animator.SetTrigger(JumpTrigger);
        }
    }
}
```

### 动画装配

```csharp
[RequireComponent(typeof(RigBuilder))]
public class AimRig : MonoBehaviour
{
    [SerializeField] private MultiAimConstraint aimConstraint;
    [SerializeField] private Transform aimTarget;

    public void SetAimWeight(float weight)
    {
        aimConstraint.weight = weight;
    }
}
```

## 最佳实践

1. 使用参数哈希以提高性能
2. 按身体部位组织层
3. 使用化身遮罩处理部分动画
4. 分析Animator更新性能
5. 使用子状态机进行组织

## 参考资料

- [动画文档](https://docs.unity3d.com/Manual/AnimationSection.html)
