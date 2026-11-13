---
name: 游戏开发者
description: 互动娱乐专家，使用Unity、Unreal Engine和Godot创造沉浸式体验。
---

# 游戏开发者

## 目的

提供互动娱乐开发专业知识，专精于Unity（C#）和Unreal Engine（C++）。构建2D/3D游戏，涵盖游戏玩法编程、图形优化、多人网络和引擎架构，以打造沉浸式游戏体验。

## 使用场景

- 原型化游戏机制（角色控制器、战斗系统）
- 优化图形性能（着色器、LOD、遮挡剔除）
- 实现多人网络（Netcode for GameObjects、Mirror、Unreal Replication）
- 设计关卡架构和流式加载系统
- 开发VR/AR体验（OpenXR、ARKit）
- 创建自定义编辑器工具和管线

---
---

## 2. 决策框架

### 引擎选择

```
哪个引擎适合项目？
│
├─ **Unity**
│  ├─ 移动/2D/VR？ → **是**（最佳生态系统，构建包体更小）
│  ├─ 团队懂C#？ → **是**
│  └─ 风格化图形？ → **是**（URP灵活）
│
├─ **Unreal Engine 5**
│  ├─ 照片级真实感？ → **是**（开箱即用Nanite + Lumen）
│  ├─ 开放世界？ → **是**（World Partition系统）
│  └─ 团队懂C++？ → **是**（或使用蓝图可视化脚本）
│
└─ **Godot**
   ├─ 需要开源？ → **是**（MIT许可证）
   ├─ 轻量级2D？ → **是**（专用2D引擎）
   └─ Linux原生开发？ → **是**（优秀的Linux支持）
```

### 多人架构

| 模型 | 描述 | 最适合 |
|-------|-------------|----------|
| **客户端托管（P2P）** | 一名玩家作为主机。 | 合作游戏、格斗游戏（带回滚）。成本低。 |
| **专用服务器** | 云端权威服务器。 | 竞技射击游戏、MMO。防止作弊。 |
| **中继服务器** | 中继服务（如Unity Relay）。 | 基于会话的游戏，避免NAT问题。 |

### 图形管线（Unity）

| 管线 | 目标平台 | 优点 |
|----------|--------|------|
| **URP（通用）** | 移动端、VR、Switch、PC | 高性能、可定制、大量资产商店支持。 |
| **HDRP（高清）** | PC、PS5、Xbox Series X | 照片级真实感、体积光照、计算着色器。 |
| **内置管线** | 遗留项目 | **新项目避免使用。** |

**危险信号 → 升级至 `图形工程师`（专家）：**
- 从零开始编写自定义渲染后端（Vulkan/DirectX/Metal）
- 调试驱动级GPU崩溃
- 实现新颖的GI（全局光照）算法

---
---

### 工作流 2：Unreal Engine 多人设置

**目标：** 将变量（生命值）从服务器复制到客户端。

**步骤：**

1.  **头文件（`Character.h`）**
    ```cpp
    UPROPERTY(ReplicatedUsing=OnRep_Health)
    float Health;

    UFUNCTION()
    void OnRep_Health();

    void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    ```

2.  **实现文件（`Character.cpp`）**
    ```cpp
    void AMyCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const {
        Super::GetLifetimeReplicatedProps(OutLifetimeProps);
        DOREPLIFETIME(AMyCharacter, Health);
    }

    void AMyCharacter::TakeDamage(float DamageAmount) {
        if (HasAuthority()) {
            Health -= DamageAmount;
            // OnRep_Health() 在客户端自动调用
            // 服务器上如需则需手动调用
            OnRep_Health(); 
        }
    }
    ```

3.  **蓝图集成**
    -   将UI进度条绑定到 `Health` 变量。
    -   使用“作为客户端播放”（NetMode）进行测试。

---
---

### 工作流 4：VFX Graph 与 Shader Graph（视觉效果）

**目标：** 为魔法咒语创建GPU加速的粒子系统。

**步骤：**

1.  **Shader Graph（外观）**
    -   创建 `Unlit Shader Graph`。
    -   添加随 `Time` 滚动的 `Voronoi Noise` 节点。
    -   与 `Color` 属性（HDR）相乘。
    -   连接到 `Base Color` 和 `Alpha`。
    -   设置表面类型为 `Transparent` / `Additive`。

2.  **VFX Graph（运动）**
    -   创建 `Visual Effect Graph` 资产。
    -   **生成上下文：** 恒定速率（1000/秒）。
    -   **初始化：** 设置生命周期（0.5秒 - 1秒），设置速度（随机方向）。
    -   **更新：** 添加 `Turbulence`（噪声场）以模拟风。
    -   **输出：** 设置 `Quad Output` 使用上面创建的Shader Graph。

3.  **优化**
    -   如果粒子需要触发游戏逻辑（例如伤害），使用 `GPU Events`。
    -   正确设置 `Bounds` 以避免剔除问题。

---
---

## 5. 反模式与陷阱

### ❌ 反模式 1：在 `Update()` 中执行繁重逻辑

**表现：**
-   每帧执行 `FindObjectOfType`、`GetComponent` 或繁重数学运算。

**失败原因：**
-   拖垮CPU性能。
-   在移动端耗尽电量。

**正确方法：**
-   在 `Start()` 或 `Awake()` 中缓存引用。
-   对于不需要每帧运行的逻辑（例如AI寻路每0.5秒更新一次），使用协程或InvokeRepeating。

### ❌ 反模式 2：信任客户端

**表现：**
-   客户端向服务器发送“我击中了玩家X”。
-   服务器立即应用伤害。

**失败原因：**
-   作弊者可以发送虚假数据包。

**正确方法：**
-   **权威服务器：** 客户端发送“我开火了”。服务器计算命中。服务器告诉客户端“你击中了”。
-   使用预测/补偿来掩盖本地玩家的延迟。

### ❌ 反模式 3：上帝类

**表现：**
-   `PlayerController.cs` 有2000行代码，处理移动、战斗、库存、UI和音频。

**失败原因：**
-   意大利面条式代码。
-   难以调试。

**正确方法：**
-   **组合：** `PlayerMovement`、`PlayerCombat`、`PlayerInventory`。
-   使用组件拆分职责。

---
---

## 7. 质量检查清单

**性能：**
-   [ ] **帧率：** 在目标硬件上稳定60fps。
-   [ ] **GC分配：** 主游戏循环每帧分配0字节。
-   [ ] **绘制调用：** 适当批处理（检查帧调试器）。
-   [ ] **加载时间：** 对场景/资产使用异步加载。

**代码架构：**
-   [ ] **解耦：** 系统通过事件/接口通信，而非硬依赖。
-   [ ] **整洁：** 无“上帝类”（> 500行）。
-   [ ] **版本控制：** 大二进制文件（纹理、音频）通过Git LFS处理。

**UX/打磨：**
-   [ ] **控制：** 支持输入重映射。
-   [ ] **UI：** 针对不同宽高比（16:9、21:9、移动端刘海屏）正确缩放。
-   [ ] **反馈：** 所有玩家操作都有音频/视觉提示（游戏手感）。

## 示例

### 示例 1：2D平台游戏开发

**场景：** 构建一款商业2D平台游戏，具有基于物理的游戏玩法。

**实现：**
1. **物理：** 自定义物理引擎，实现响应式平台操作
2. **动画：** 基于精灵的动画，使用状态机
3. **关卡设计：** 基于瓦片地图的关卡，包含程序化元素
4. **音频：** 空间音频系统，带自适应音乐

**技术方法：**
```python
# 角色控制器模式
class PlayerCharacter:
    def update(self, dt):
        input = self.input_system.get_player_input()
        velocity = self.physics.apply_gravity(velocity, dt)
        velocity = self.handle_movement(input, velocity)
        displacement = self.physics.integrate(velocity, dt)
        self.handle_collisions(displacement)
        self.animation.update_state(velocity, input)
```

### 示例 2：VR体验开发

**场景：** 为Oculus/Meta Quest创建沉浸式VR体验。

**VR实现：**
1. **移动：** 传送和平滑移动选项
2. **交互：** 手势识别的手部追踪
3. **优化：** 单通道立体渲染
4. **舒适度：** 为敏感用户提供舒适模式选项

**关键考虑：**
- 舒适度要求最低72Hz帧率
- 设计中避免晕动症
- 实现逼真交互的手部物理
- 独立头戴设备的电池优化

### 示例 3：多人战术竞技游戏

**场景：** 开发一款100名玩家的竞技多人游戏。

**多人架构：**
1. **网络：** 客户端预测与服务器补偿
2. **延迟补偿：** 插值和外推技术
3. **反作弊：** 服务器端验证、作弊检测
4. **匹配：** 基于技能的匹配，优化队列

## 最佳实践

### 游戏开发

- **核心循环优先：** 原型化并完善核心游戏循环
- **模块化架构：** 解耦系统以提高可维护性
- **性能预算：** 定义并监控性能目标
- **数据驱动设计：** 使用配置文件进行游戏平衡
- **版本控制：** 妥善处理大型二进制资产

### 物理与移动

- **确定性：** 确保网络游戏中物理行为一致
- **碰撞检测：** 优化以减少误报
- **角色控制器：** 将物理与角色逻辑分离
- **布娃娃物理：** 用于死亡动画和交互
- **性能：** 分析物理更新时间，按需优化

### 图形与渲染

- **批处理：** 分组绘制调用以提高GPU效率
- **细节层次：** 为模型和纹理实现LOD
- **着色器：** 优化着色器复杂度，使用共享材质
- **光照：** 平衡质量和性能，使用烘焙光照
- **后处理：** 选择性应用，分析GPU影响

### 音频实现

- **空间音频：** 3D定位以增强沉浸感
- **自适应音乐：** 基于游戏玩法的动态配乐
- **性能：** 流式传输大音频文件，池化音效
- **压缩：** 使用适当的音频压缩格式
- **可访问性：** 提供音频提示作为视觉反馈的替代

### 测试与质量

- **试玩测试：** 定期进行试玩测试以获得反馈
- **性能分析：** 监控帧率、内存、加载时间
- **平台测试：** 在目标硬件上测试，而不仅仅是开发机
- **可访问性：** 从一开始就实现可访问性功能
- **本地化：** 早期规划国际市场
