---
name: combat-system-creator
description: "这是一个用于创建和修改SHINOBI WAY游戏中战斗系统组件的工具，遵循双系统架构，专注于战斗机制的纯计算与状态管理分离，适用于添加新战斗特性和重构现有战斗代码。"
---
创建和修改SHINOBI WAY游戏中的战斗系统组件，遵循双系统架构（CombatCalculationSystem + CombatWorkflowSystem）。当用户想要添加新的战斗机制、伤害公式、状态效果、减免逻辑、回合阶段或重构现有战斗代码时使用。指导如何正确分离纯计算与状态管理。

## 架构原则

```
玩家行动 → CombatCalculationSystem（纯数学）→ CombatWorkflowSystem（应用到状态）
```

**CombatCalculationSystem**：纯函数，无变异，返回完整结果
**CombatWorkflowSystem**：状态管理，应用计算结果，控制流程

## 何时使用

- 添加新的损伤计算或公式
- 创建新的状态效果或减免机制
- 添加新的战斗阶段或回合逻辑
- 重构现有的战斗代码
- 平衡或修改战斗数学

## 快速参考

### 伤害流程（5步）

```
1. 命中检查    → 近战：速度 vs 速度 | 远程：精准度 vs 速度 | 自动：总是命中
2. 基础伤害  → 扩展属性 × 伤害倍数
3. 元素      → 超级：1.5×（+10% 暴击） | 抗性：0.5× | 中性：1.0×
4. 暴击     → 8% + （DEX × 0.5）+ 奖金，最大75%，倍数1.75×
5. 防御      → 固定（最大60%减免）然后%（软上限75%）
```

### 减免流程（优先顺序）

```
1. 无敌 → 阻挡所有伤害（返回0）
2. 反射      → 计算反射伤害（诅咒之前）
3. 诅咒           → 放大：伤害 × （1 + 诅咒值）
4. 护盾          → 在HP之前吸收伤害
5. 毅力            → 如果成功则在1点HP存活
```

### 防御公式

| 类型 | 固定 | 百分比（软上限） |
|------|------|-------------------|
| 物理 | `STR × 0.3` | `STR / (STR + 200)` |
| 元素 | `SPI × 0.3` | `SPI / (SPI + 200)` |
| 精神 | `CAL × 0.25` | `CAL / (CAL + 150)` |

### 伤害属性

| 属性 | 固定防御 | %防御 |
|----------|----------|-------|
| 普通 | ✅ （最大60%） | ✅ |
| 穿透 | ❌ | ✅ |
| 破甲 | ✅ | ❌ |
| 真实 | ❌ | ❌ |

## 工作流：添加新机制

### 第1步：确定系统
问：**这是纯数学还是状态管理？**

| CombatCalculationSystem | CombatWorkflowSystem |
|------------------------|---------------------|
| 伤害公式 | 应用伤害到HP |
| 命中/未命中/闪避判定 | 回合顺序管理 |
| 暴击计算 | 增益持续时间跟踪 |
| 防御减免 | 阶段转换 |
| 效果几率判定 | 战斗日志生成 |

### 第2步：设计计算接口

对于新计算，定义结果接口：

```typescript
interface NewMechanicResult {
  // 应用此机制所需的所有值
  value: number;
  triggered: boolean;
  // 用于日志记录的元数据
  logs: CombatLogEntry[];
}
```

### 第3步：实现纯函数

```typescript
// 在 CombatCalculationSystem
function calculateNewMechanic(
  attackerStats: DerivedStats,
  defenderStats: DerivedStats,
  context: CombatContext
): NewMechanicResult {
  // 纯计算 - 无状态变异
  return { value, triggered, logs };
}
```

### 第4步：实现工作流应用

```typescript
// 在 CombatWorkflowSystem
function applyNewMechanic(
  state: CombatWorkflowState,
  result: NewMechanicResult
): CombatWorkflowState {
  // 将结果应用到状态 - 返回新状态
  return { ...state, /* 更新值 */ };
}
```

## 创建新状态效果

### 可用效果类型

```typescript
// 持续伤害
DOT, BLEED, BURN, POISON

// 群体控制
STUN, CONFUSION, SILENCE

// 防御性
SHIELD, INVULNERABILITY, REFLECTION

// 属性修改器
BUFF, DEBUFF, CURSE

// 恢复
HEAL, REGEN, CHAKRA_DRAIN
```

### 效果接口

```typescript
interface SkillEffect {
  type: EffectType;
  value: number;           // 伤害/治疗量或倍数
  duration: number;        // 回合（-1 = 永久）
  chance: number;          // 0.0-1.0 应用几率
  targetStat?: PrimaryStat; // 对于BUFF/DEBUFF
  damageType?: DamageType;  // 对于DoTs
  damageProperty?: DamageProperty;
}
```

### DoT伤害公式

```typescript
// DoTs获得50%防御减免
dotDamage = max(1, baseDamage - (flatDef × 0.5) - (damage × percentDef × 0.5))
```

## 创建新的战斗阶段

### 现有的回合阶段

**玩家回合：**
1. TURN_START → 重置标志
2. UPKEEP → 切换成本，被动再生
3. MAIN_ACTION → 技能执行
4. DEATH_CHECK → 胜利/失败
5. TURN_END → 标记回合完成

**敌人回合：**
1. DOT_ENEMY → 处理敌人DoTs
2. DOT_PLAYER → 处理玩家DoTs（通过盾牌）
3. DEATH_CHECK_DOT → 检查DoT击杀
4. ENEMY_ACTION → AI技能选择+执行
5. DEATH_CHECK_ATTACK → 检查战斗击杀
6. RESOURCE_RECOVERY → 冷却，查克拉再生
7. TERRAIN_HAZARDS → 环境伤害
8. FINAL_DEATH_CHECK → 危险击杀

### 添加新阶段

```typescript
// 1. 添加到 CombatPhase 枚举
enum CombatPhase {
  // ... 现有的
  NEW_PHASE,
}

// 2. 创建计算函数
function calculateNewPhaseEffects(state: CombatWorkflowState): NewPhaseResult;

// 3. 创建工作流处理程序
function processNewPhase(state: CombatWorkflowState): CombatWorkflowState;

// 4. 在 processEnemyTurn 或 executePlayerAction 中插入到回合流程
```

## 输出模板

### 新计算函数

```typescript
/**
 * [这个计算什么]
 * @param attackerStats - 攻击者的衍生属性
 * @param defenderStats - 防守者的衍生属性
 * @param skill - 使用的技能
 * @returns [ResultType] 包含所有计算细节
 */
export function calculateX(
  attackerStats: DerivedStats,
  defenderStats: DerivedStats,
  skill: Skill
): XResult {
  const result: XResult = {
    // 初始化结果对象
  };

  // 这里进行纯计算
  // 无状态变异
  // 使用Math.random()进行掷骰

  return result;
}
```

### 新工作流函数

```typescript
/**
 * [这个状态变化应用了什么]
 * @param state - 当前战斗状态
 * @param result - 计算结果以应用
 * @returns 新的战斗状态，已应用更改
 */
export function applyX(
  state: CombatWorkflowState,
  result: XResult
): CombatWorkflowState {
  // 创建新的状态对象（不可变）
  const newState = { ...state };

  // 将结果值应用到状态
  // 添加战斗日志
  // 检查战斗结束条件

  return newState;
}
```

### 新效果实现

```typescript
// 在 constants/index.ts - 添加到 SKILLS
NEW_SKILL: {
  id: 'new_skill',
  name: '新技能名称',
  // ... 其他属性
  effects: [{
    type: EffectType.NEW_EFFECT,
    value: 10,
    duration: 3,
    chance: 0.8,
    damageType: DamageType.PHYSICAL,
    damageProperty: DamageProperty.NORMAL
  }]
}

// 在 CombatSystem.ts - 在 applyMitigation 或 processDoT 中处理
if (buff.effect.type === EffectType.NEW_EFFECT) {
  // 计算效果
  // 应用到适当的目标
}
```

## 参考文件

- [combat-mechanics.md](references/combat-mechanics.md) - 完整的战斗公式和常数
- [architecture.md](references/architecture.md) - 双系统架构细节

## 平衡常数

### 资源池
- HP: `50 + (WIL × 12)`
- 查克拉: `30 + (CHA × 8)`
- HP再生: `maxHP × 0.02 × (WIL / 20)`
- 查克拉再生: `INT × 2`

### 战斗常数
- 基础命中: 92%
- 命中范围: 30-98%
- 基础暴击: 8%
- 暴击上限: 75%
- 暴击倍数: 1.75×
- 固定防御上限: 伤害的60%
- %防御上限: 75%

### 生存
- 毅力: `WIL / (WIL + 200)`
- 状态抗性: `CAL / (CAL + 80)`
- 闪避: `SPD / (SPD + 250)`
