---
name: godot-physics-3d
description: "Godot 3D物理的专家模式（Jolt/PhysX），包括Ragdolls、PhysicalBones、Joint3D约束、RayCasting优化和碰撞层。用于刚体模拟、角色物理或复杂交互。触发关键词：RigidBody3D、PhysicalBone3D、Jolt、Ragdoll、Skeleton3D、Joint3D、PinJoint3D、HingeJoint3D、Generic6DOFJoint3D、RayCast3D、PhysicsDirectSpaceState3D。"
---

# 3D 物理 (Jolt/原生)

高性能3D物理和Ragdoll的专家指导。

## 切勿执行

- **切勿缩放RigidBody3D** — 缩放碰撞形状，切勿缩放物体本身。非均匀缩放会破坏物理引擎逻辑。
- **切勿在 `_process` 中使用 `move_and_slide`** — 始终使用 `_physics_process`。帧率依赖性会破坏模拟稳定性。
- **切勿持续模拟Ragdoll 24/7** — 仅在死亡或碰撞时启用物理骨骼。否则使用静态网格动画以节省CPU。
- **切勿忽略Jolt** — 对于稳定性和性能，Godot Jolt插件在4.x版本中严格优于默认Godot物理。如果可能，请使用它。
- **切勿对动态物体使用ConcaveCollisionShape3D** — 凹面形状（Trimesh）仅用于静态地面。移动物体必须是凸面或基本形状（Box/Capsule）。

---

## 可用脚本

### [ragdoll_manager.gd](scripts/ragdoll_manager.gd)
专家管理器，用于将Skeleton3D从动画过渡到物理模拟（死亡效果）。处理脉冲应用和清理。

### [raycast_visualizer.gd](scripts/raycast_visualizer.gd)
调试工具，可视化游戏中RayCast3D的命中点和法线。
## 核心架构

### 1. 图层和遮罩 (3D)
与2D相同：
- **图层**: 对象是什么。
- **遮罩**: 对象击中什么。

### 2. 物理骨骼 (Ragdoll)
Godot使用附加到 `Skeleton3D` 骨骼的 `PhysicalBone3D` 节点。
设置步骤：
1. 选择Skeleton3D。
2. 点击顶部菜单中的“创建物理骨架”。
3. 这会生成 `PhysicalBone3D` 节点。

### 3. Jolt 关节
几乎对所有情况使用 `Generic6DOFJoint3D`。它覆盖了铰链、滑块和球窝需求，配置比特定节点更简单。

---

## Ragdoll 实现

```gdscript
# simple_ragdoll.gd
extends Skeleton3D

func start_ragdoll() -> void:
    physical_bones_start_simulation()
    
func stop_ragdoll() -> void:
    physical_bones_stop_simulation()
```


## 参考
- 主技能: [godot-master](../godot-master/SKILL.md)
