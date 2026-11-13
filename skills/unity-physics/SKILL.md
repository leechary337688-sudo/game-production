---
名称: Unity物理系统
描述: Unity物理技能，用于碰撞检测、刚体动力学、射线投射和物理配置。
允许工具: 读取, 搜索, 写入, 命令行, 编辑, 全局匹配, 网络获取
---

# Unity物理技能

Unity中的物理系统配置与实现。

## 概述

此技能提供使用Unity物理系统（PhysX 3D和Box2D 2D）实现基于物理的游戏玩法的能力。

## 能力

### 刚体配置
- 配置质量、阻力、约束
- 设置连续碰撞检测
- 处理插值模式
- 管理休眠阈值

### 碰撞检测
- 配置碰撞体和触发器
- 设置碰撞层和遮罩
- 处理碰撞事件
- 实现复合碰撞体

### 射线投射
- 执行射线投射和球体投射
- 使用重叠测试
- 处理层过滤
- 批量物理查询

### 物理设置
- 配置固定时间步长
- 设置求解器迭代次数
- 处理物理材质
- 管理自动同步变换

## 先决条件

- Unity 2021.3+
- 物理模块（内置）

## 使用模式

### 刚体设置

```csharp
public class PhysicsObject : MonoBehaviour
{
    private Rigidbody rb;

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        rb.interpolation = RigidbodyInterpolation.Interpolate;
        rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
    }

    void FixedUpdate()
    {
        rb.AddForce(Vector3.forward * 10f, ForceMode.Force);
    }
}
```

### 射线投射

```csharp
public bool CheckGround(out RaycastHit hit)
{
    return Physics.Raycast(
        transform.position,
        Vector3.down,
        out hit,
        1.1f,
        groundLayer,
        QueryTriggerInteraction.Ignore
    );
}
```

## 最佳实践

1. 使用FixedUpdate处理物理
2. 避免在运行时缩放碰撞体
3. 使用层进行过滤
4. 分析物理查询性能
5. 考虑Physics.autoSyncTransforms

## 参考

- [物理文档](https://docs.unity3d.com/Manual/PhysicsSection.html)
