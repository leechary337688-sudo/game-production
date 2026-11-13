---
name: exploration-creator
description: 创建SHINOBI WAY游戏的探索内容，使用基于节点的路径导航。当用户想要添加新区域、地点、房间布局、情报任务、路径网络或探索机制时使用。通过情报控制的路径选择，引导用户通过区域→地点→房间的层级结构。（项目）
---

# 探索系统创建器

为SHINOBI WAY: THE INFINITE TOWER创建基于节点导航系统的探索内容，并包含情报控制的路径选择。

## 核心层级结构

```
区域（例如，波之国）
├── 地点 × 10-15 （例如，码头，渔村）
│   ├── 房间 × 每个地点10个（1→2→4→2→1分支）
│   │   ├── 房间1-9：随机活动（战斗，事件，商人等）
│   │   └── 房间10：情报任务（总是精英战斗）
│   └── 路径（连接到其他地点）
└──  Boss（最终目的地）
```

## 关键机制

| 机制 | 描述 |
|----------|-------------|
| **单向前进** | 不能返回到之前的地点（类似roguelike风格） |
| **路径选择** | 有情报：选择路径。没有：随机目的地 |
| **情报任务** | 房间10精英战斗。胜利=情报。跳过=随机路径 |
| **循环** | 通过情报发现的特殊路径回到早期地点 |
| **秘密** | 通过情报、物品、功德或故事解锁的隐藏地点 |

## 工作流程

### 第1步：设计区域

定义区域的身份：

```typescript
const region: Region = {
  id: 'region_id',
  name: '区域名称',
  theme: '叙事主题描述',
  description: '氛围描述',
  entryPoints: ['location_1', 'location_2'],  // 1-2个起始地点
  bossLocation: 'boss_location_id',
  lootTheme: {
    primaryElement: ElementType.WATER,
    equipmentFocus: ['speed', 'dexterity'],
    goldMultiplier: 0.8
  }
};
```

查看[region-system.md](references/region-system.md)了解完整的区域结构。

### 第2步：规划地点（10-15）

用危险进度映射地点：

| 列 | 阶段 | 危险 | 地点数量 |
|--------|-------|--------|----------------|
| 0 | 入口 | 1-2 | 1-2个地点 |
| 1 | 早期 | 3-4 | 2-3个地点 |
| 2 | 中期 | 4-5 | 3-4个地点 |
| 3 | 晚期 | 5-6 | 2-3个地点 |
| 4 | Boss | 7 | 1个地点 |

**地点类型：**

| 类型 | 战斗 | 商人 | 休息 | 焦点 |
|------|--------|----------|------|-------|
| `settlement` | 低 | 是 | 是 | 故事，社交 |
| `wilderness` | 中等 | 否 | 可能 | 探索 |
| `stronghold` | 高 | 可能 | 否 | 重度战斗 |
| `landmark` | 中等 | 可能 | 可能 | 平衡，故事 |
| `secret` | 不同 | 稀有 | 稀有 | 独特奖励 |
| `boss` | BOSS | 否 | 否 | 最终遭遇 |

查看[location-system.md](references/location-system.md)了解地点数据结构和地形类型。

### 第3步：定义房间活动

每个地点有10个房间，采用1→2→4→2→1的分支结构。玩家每个地点访问5个房间。

**活动权重（仅限房间1-9）：**

| 活动 | 权重 | 描述 |
|----------|--------|-------------|
| `combat` | 40% | 与地点池中的敌人战斗 |
| `event` | 25% | 氛围事件与选择 |
| `merchant` | 10% | 买卖（每个地点最多1个） |
| `rest` | 8% | 恢复HP/查克拉（每个地点最多1个） |
| `treasure` | 8% | 战利品箱 |
| `training` | 5% | 永久性状态升级 |
| `story_event` | 4% | 来自故事树的叙事 |

**房间10总是情报任务** - 精英战斗或Boss。

查看[room-system.md](references/room-system.md)了解房间布局和连接。

### 第4步：配置情报任务

每个地点的房间10包含一个情报任务：

```
玩家到达房间10 → 战斗或跳过
├── 战斗 → 胜利 → 情报 + 战利品 → 选择下一条路径
├── 战斗 → 失败 → 游戏结束
└── 跳过 → 无奖励 → 随机下一条路径
```

**地点类型按精英等级缩放：**

| 地点类型 | 精英等级 | 备注 |
|---------------|-------------|-------|
| Settlement | 2-3 | 守卫，间谍 |
| Wilderness | 3-5 | 野兽，强盗 |
| Stronghold | 5-7 | 指挥官 |
| Landmark | 4-5 | 守护者 |
| Secret | 4-7 | 独特精英 |
| Boss | 8-10 | **不能跳过** |

查看[intel-mission-system.md](references/intel-mission-system.md)了解情报奖励和Boss处理。

### 第5步：映射路径网络

定义地点之间的连接：

**路径类型：**

| 类型 | 方向 | 发现 | 描述 |
|------|-----------|-----------|-------------|
| `forward` | → | 始终可见 | 标准进度 |
| `branch` | → | 始终可见 | 替代路线 |
| `loop` | ← | 通过情报提示 | 返回早期地点 |
| `secret` | → | 通过情报/物品/功德 | 隐藏地点访问 |
| `boss` | → | 始终可见 | 最终通往Boss的路径 |

**导航规则：**
1. 单向前进（除循环外）
2. 访问过的地点关闭
3. 情报=玩家选择路径
4. 没有情报=随机目的地
5. 循环一次性使用
6. Boss完成区域

查看[navigation-system.md](references/navigation-system.md)了解路径数据结构和循环系统。

### 第6步：验证

**区域检查清单：**
- [ ] 总共10-15个地点
- [ ] 1-2个入口点（isEntry: true）
- [ ] 1个Boss地点（isBoss: true）
- [ ] 所有地点从入口可达
- [ ] 多条通往Boss的路径（至少2-3条）
- [ ] 危险曲线：入口（1-2）→ Boss（7）

**地点检查清单：**
- [ ] 唯一ID和名称
- [ ] 有效的类型和危险等级
- [ ] 1-3条前进路径（除Boss外）
- [ ] 定义情报任务
- [ ] 标志与类型匹配

**房间检查清单：**
- [ ] 每个地点10个房间
- [ ] 房间10=intel_mission
- [ ] 最多1个商人，最多1个休息
- [ ] 连接遵循1→2→4→2→1

查看[types.md](references/types.md)了解完整的TypeScript接口。

## 参考文件

- [region-system.md](references/region-system.md) - 区域结构和数据
- [location-system.md](references/location-system.md) - 地点类型，地形，标志
- [room-system.md](references/room-system.md) - 10房间布局和活动
- [intel-mission-system.md](references/intel-mission-system.md) - 精英战斗和情报奖励
- [navigation-system.md](references/navigation-system.md) - 路径，循环，秘密
- [types.md](references/types.md) - TypeScript类型定义
- [example-waves.md](references/example-waves.md) - 完整的波之国区域

## 输出格式

为新区域/地点生成TypeScript代码，准备集成到游戏系统中。
