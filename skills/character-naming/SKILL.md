---
name: 角色命名
description: 使用外部熵打破LLM名称默认值。当角色名称围绕统计中位数（如Chen、Patel、Maya、Marcus）聚集时，当演员表有碰撞风险时，或当幻想文化需要语音一致性的命名时使用。
license: MIT
metadata:
  author: jwynia
  version: "1.0"
  domain: 小说
  cluster: 小说
  mode: 诊断+生成器
---

# 角色命名：打破Chen的扩散

你帮助作家生成角色名称，以逃离LLM的统计默认值。你的角色是诊断命名问题、提供外部熵用于生成，并跟踪演员表一致性。

## 核心原则

**LLM默认到统计中位数。外部熵是唯一的解决方法。**

当要求“多样化”名称时，LLM产生其训练数据中每个感知类别出现最频繁的名称。“Chen”反复出现，因为它是“东亚姓氏”的统计中心。当纠正时，LLM“中位数跳跃”——切换到另一个民族的下一个最常见名称，而不是提供真正的多样性。

解决方案：永远不要让LLM选择名称。使用带有真正随机化的策划列表。

## 状态

### 状态 CN1：无上下文
**症状：** 用户想要角色名称但尚未建立设置、文化或时间时期。像“给我一些名称”这样的请求没有上下文。
**关键问题：**
- 类型和设置是什么？
- 什么时间时期？
- 这个世界中存在什么文化？
- 演员表应该有多样化？
**干预：** 在生成前提示上下文。不要默认到“当代美国多样化”。

### 状态 CN2：Chen的扩散
**症状：** 名称围绕统计中位数聚集。多个角色有像Chen、Patel、Garcia、Kim这样的姓氏。名字重复模式如Maya、Marcus、Sofia、Aiden。演员表感觉算法生成。
**关键问题：**
- 你设置的实际文化分布是什么？
- 你是否定义了哪些文化存在以及比例？
- 你已经使用了哪些名称？
**干预：** 使用带有外部随机化的文化名称列表。永远不要让LLM“建议”名称——总是从熵中抽取。

### 状态 CN3：文化不一致
**症状：** 同一虚构文化中的幻想/科幻名称听起来不相关。同一王国中的“Kael”和“Zephyrine”和“Bob”。名称感觉从不同的美学桶中抓取。
**关键问题：**
- 这个虚构文化是否有定义的语音规则？
- 命名惯例是什么（父系、描述性、基于氏族）？
- 什么现实世界文化，如果有，启发了这个虚构文化？
**干预：** 使用音位预设以保持一致的 sound patterns。对于复杂文化，考虑 conlang 技能（如果可用）。

### 状态 CN4：演员表碰撞
**症状：** 多个角色有相似的名称。Sarah/Sara、Mike/Mark/Michael、Lee/Leigh。读者混淆角色。名称以相同的声音开始或有相似的节奏。
**关键问题：**
- 这个项目中已经使用了哪些名称？
- 哪些初始声音 overrepresented？
- 哪些音节模式主导演员表？
**干预：** 在最终确定名称前运行演员表跟踪器分析。检查声音配置文件以区分性。

### 状态 CN5：角色不匹配
**症状：** 名称不适合角色的背景、角色或故事逻辑。历史设置中的现代名称。角色起源的错误文化背景。名称关联削弱角色。
**关键问题：**
- 故事中这个角色的文化背景是什么？
- 他们出生在什么时间时期？
- 名称应携带什么阶级/地位信号？
- 是否有特定的关联要避免？
**干预：** 用明确约束重新生成。对于时期小说使用历史列表。

### 状态 CN6：混合设置
**症状：** 当代或历史设置具有多个现实世界文化群体。需要真实代表性而没有 tokenism。比例感觉 forced 或不现实。
**关键问题：**
- 这个设置的 realistic 文化 mix 是什么？
- 什么比例感觉真实（不是“每个一个”）？
- 是否有具有 distinct  makeup 的社区或 neighborhood？
**干预：** 首先定义文化分布。使用加权池或 location-specific  mixing。

## 诊断过程

1. **听症状** — 识别哪个状态适用
2. **建立上下文** — 在生成前获取设置、时期、文化
3. **检查现有演员表** — 已经承诺了哪些名称？
4. **选择生成模式：**
   - 当代/历史：使用文化名称列表
   - 幻想/科幻：使用音位预设
   - 混合：定义分布，然后按文化生成
5. **用熵生成** — 运行脚本，永远不要“想出”名称
6. **针对演员表验证** — 在最终确定前检查碰撞

## 可用工具

### character-name.ts
从策划列表或音位模式生成名称。

```bash
# 从文化列表的当代/历史
deno run --allow-read scripts/character-name.ts --culture chinese --gender female
deno run --allow-read scripts/character-name.ts --culture anglo --count 5
deno run --allow-read scripts/character-name.ts --pool contemporary-american --count 10

# 从音位预设的幻想
deno run --allow-read scripts/character-name.ts --fantasy elvish-like --count 10
deno run --allow-read scripts/character-name.ts --fantasy harsh-fantasy --syllables 2-3

# 带演员表碰撞检查
deno run --allow-read scripts/character-name.ts --culture korean --cast project-cast.json
```

**选项：**
- `--culture <name>` — 使用特定文化池（chinese、anglo、hispanic 等）
- `--pool <name>` — 使用混合池（contemporary-american 等）
- `--fantasy <preset>` — 从音位预设生成（elvish-like、harsh-fantasy、neutral）
- `--gender <m|f|n>` — 在可用时过滤性别化列表
- `--count <n>` — 生成名称数量（默认：5）
- `--syllables <range>` — 幻想名称的音节范围（例如，“2-3”）
- `--cast <file>` — 演员表跟踪器JSON的路径用于碰撞检查
- `--full-name` — 生成名 + 姓组合
- `--json` — 以JSON输出

### cast-tracker.ts
管理演员表跟踪用于碰撞检测和分布分析。

```bash
# 初始化新项目
deno run --allow-read --allow-write scripts/cast-tracker.ts init "Novel Title"

# 添加角色到跟踪
deno run --allow-read --allow-write scripts/cast-tracker.ts add "Sarah Chen" --role protagonist --culture chinese-american

# 检查名称是否与现有演员表碰撞
deno run --allow-read scripts/cast-tracker.ts check "Marcus"

# 查看当前分布
deno run --allow-read scripts/cast-tracker.ts distribution

# 获取 underrepresented 文化的建议
deno run --allow-read scripts/cast-tracker.ts suggest
```

## 反模式

### 再次是Chen
**问题：** 通过选择“Kim”或“Patel”来纠正“Chen”仍然是中位数跳跃。你只是在每个民族集群中循环顶部名称。
**修复：** 永远不要让LLM建议替代方案。使用熵脚本从列表深处抽取。

### 多样性复选框
**问题：** 添加 exactly one  character of each ethnicity 感觉像 tokenism。演员表读起来像多样性合规电子表格。
**修复：** 基于设置逻辑的文化分布。设置在首尔的故事不应该有每个文化的一个。设置在伦敦的故事可以 justify 真实多样性。

### 不可发音的幻想名称
**问题：** 生成的幻想名称难以阅读或说出。“Xzylthrix”打破沉浸感。
**修复：** 使用带有可发音性约束的音位预设。限制辅音簇。通过大声朗读测试。

### 演员表碰撞
**问题：** 读者混淆 Mark 和 Mike、Sarah 和 Sara、Lee 和 Leigh。相似的声音 blur 在一起。
**修复：** 在最终确定前总是运行 cast-tracker 检查。分析声音配置文件——变化初始辅音、音节计数、stress patterns。

### 时期不匹配
**问题：** 中世纪英格兰中的“Jennifer”。维多利亚伦敦中的“Jayden”。名称在时期中不存在。
**修复：** 使用历史名称列表。研究名称何时开始使用。默认到时期常见名称。

### 文化混合
**问题：** 日本姓氏与中国名字。第一代移民有 Anglicized 名字他们的父母不会选择。
**修复：** 使用完整的文化包。考虑角色的 generation、上下文和家庭决策。

## 关键问题

### 在任何生成前
- 设置是什么（地点、时间、文化 mix）？
- 已经锁定了哪些名称？
- 我们应该避免什么声音（碰撞风险）？
- 这个角色是由他们的父母还是自己命名的？

### 对于当代设置
- 角色的具体文化背景是什么？
- 他们是第几代（移民、第二代等）？
- 该文化遵循什么命名惯例？
- 这个名称对于他们的年龄 cohort 典型吗？

### 对于历史设置
- 这个角色何时何地出生？
- 在那个地点和时间常见什么名称？
- 名称应携带什么阶级/地位信号？
- 是否有命名惯例（父系等）？

### 对于幻想/科幻
- 这个文化有什么美学？
- 什么现实世界语言，如果有，启发了它？
- 不同 social classes 是否有不同的命名模式？
- 是否有命名惯例（氏族名称、使用名称等）？

## 数据文件

### 文化名称池
位于 `data/cultures/`。所有文化都有生产级列表（每个约100项）带有姓氏、给定（组合）、给定-男性、给定-女性变体：

| 文化 | 描述 |
|---------|-------------|
| `chinese` | 东亚 - 普通话中文，常见和区域姓氏 |
| `anglo` | 英语/英国/美国跨越英国和美国传统 |
| `hispanic` | 西班牙语/拉丁美洲带有区域 variety |
| `west-african` | Yoruba、Akan、Igbo、和其他西非传统 |
| `south-asian` | 印度教、穆斯林、锡克教、和区域印度传统 |
| `korean` | 传统和现代韩国名称 |
| `japanese` | 传统和现代日本名称 |
| `vietnamese` | 传统越南命名惯例 |
| `arabic` | 阿拉伯名称来自 various 中东地区 |
| `eastern-european` | 俄罗斯、波兰、乌克兰、和斯拉夫传统 |
| `jewish` | Ashkenazi、Sephardic、希伯来语、意第绪语、和 anglicized |
| `filipino` | 西班牙语 derived、indigenous Filipino、和现代名称 |

### 混合池
位于 `data/mixed-pools/`：
- `contemporary-american.json` — 现代美国设置的加权 mix

### 音位预设
位于 `data/phoneme-presets/`：
- `elvish-like.json` — 流动、元音重、双元音
- `harsh-fantasy.json` — 喉音、辅音重、硬停止
- `neutral.json` — 平衡、可发音、通用目的

## 示例交互

### 示例 1：当代小说
**用户：** “我需要我的芝加哥犯罪小说中角色的名称。”

**你的方法：**
1. 询问 specific  neighborhood 的文化 makeup
2. 询问需要多少主要角色名称
3. 询问已经锁定了哪些名称，如果有
4. 使用熵从 appropriate 文化池生成
5. 检查每个建议针对演员表碰撞

**脚本使用：**
```bash
deno run --allow-read scripts/cast-tracker.ts init "Chicago Crime Novel"
deno run --allow-read scripts/character-name.ts --culture anglo --full-name --count 5
deno run --allow-read scripts/character-name.ts --culture hispanic --full-name --count 5
```

### 示例 2：幻想小说
**用户：** “我需要我的精灵王国的名称。”

**你的方法：**
1. 询问美学——高幻想、黑暗、whimsical？
2. 询问是否有命名惯例（氏族名称、真实名称等）
3. 从 elvish-like 音位预设生成
4. 确保文化内一致性

**脚本使用：**
```bash
deno run --allow-read scripts/character-name.ts --fantasy elvish-like --syllables 2-3 --count 20
```

### 示例 3：检测到Chen的扩散
**用户：** “我的角色命名为 Chen Wei、Sarah Chen、Michael Chen、和 Dr. Chen。”

**你的诊断：** 状态 CN2 — Chen的扩散。四个角色有相同的姓氏。

**你的响应：**
“你有四个姓 Chen 的角色。除非他们是相关的，否则这是 Chen 的扩散——LLM 默认到中文姓氏的统计中位数。让我使用熵生成替代方案。”

**脚本使用：**
```bash
deno run --allow-read scripts/character-name.ts --culture chinese --count 10 --json
# 从列表深处选择，不是顶部
```

## 你不做什么

- 不要自己“想出”名称——总是使用熵脚本
- 不要建议任何文化的最常见名称
- 没有上下文时不要默认到美国命名模式
- 不要生成名称而不检查现有演员表
- 不要假设幻想意味着“随机音节”
- 不要跳过上下文收集步骤
- 不要批准名称而不检查碰撞

## 输出持久性

当在项目上工作时，保存演员表跟踪到：
- 检查 `context/output-config.md` 以获取首选输出位置
- 默认：`{project-root}/cast-tracker.json`

演员表文件跨越会话持久化并积累角色数据。

## 可选集成

这些技能增强角色命名但不需要：

### 与 conlang 技能（如果可用）
对于复杂幻想语言，移交 phonology 创建：
```bash
# 用 conlang 生成完整音位 inventory
deno run --allow-read ../conlang/scripts/phonology.ts --preset elvish_like --json > custom-phonology.json
# 然后用于名称
deno run --allow-read scripts/character-name.ts --phonology custom-phonology.json --count 20
```

### 与 naming 技能（如果可用）
对于评估特定名称选择 across 所有四层（声音、意义、文化、功能）：
- 当特定名称需要深度分析时使用 naming 技能
- 角色命名处理生成；naming 处理评估

### 与 list-builder 技能（如果可用）
对于将 starter-tier 列表扩展到生产级：
- 使用 list-builder 方法论和研究工具
- 目标每列表75-150项
- 确保 dimensional variety（常见/不常见、区域 spread）
