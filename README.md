# game-production

游戏生产（Game Production）相关的 AI Agent Skills 合集，按「游戏开发 / 三维与游戏」方向整理，可直接复制到支持 Skills 的 Agent 中使用。

## 数据来源

全部技能来自 **SkillsBot**（<https://www.skillsbot.cn>）的公开检索：

- 分类：`游戏开发`、`三维与游戏`（含 Blender建模、Maya动画、Unity开发、Unreal Engine、游戏策划、角色设计、场景建模、动作捕捉、游戏测试）
- 关键词搜索：游戏、游戏开发、游戏设计、游戏策划、游戏测试、游戏运营、Unity、Unreal、Godot、Blender、Maya、3D、像素、关卡、战斗、数值、玩法、玩家、RPG、动画、音效、角色设计、独立游戏 等
- 收录范围：仅保留 **Unity / Unreal / Godot / Blender** 相关技能，以及 **游戏设计、数值、剧情、美术管线** 这几类；已剔除医疗、养老、销售、逆向/黑客等无关内容，重复技能按名称合并
- 抓取时间：2026-11-13T00:18:14Z

## 仓库结构

```
skills/<技能名>/SKILL.md   技能正文（从 SkillsBot 公开详情接口获取）
skills/<技能名>/meta.json  分类、安装量、原始项目、来源链接
catalog/*.md               按分类整理的技能索引
index.json                 机器可读索引
scripts/sync.py            重新检索并同步（复现本仓库）
```

## 分类统计

| 分类 | 技能数 | 索引 |
|---|---|---|
| 游戏开发 | 135 | [catalog/游戏开发.md](catalog/游戏开发.md) |
| Unity开发 | 20 | [catalog/Unity开发.md](catalog/Unity开发.md) |
| Unreal Engine | 16 | [catalog/Unreal Engine.md](catalog/Unreal Engine.md) |
| Blender建模 | 1 | [catalog/Blender建模.md](catalog/Blender建模.md) |
| Maya动画 | 7 | [catalog/Maya动画.md](catalog/Maya动画.md) |
| 角色设计 | 1 | [catalog/角色设计.md](catalog/角色设计.md) |
| 动作捕捉 | 1 | [catalog/动作捕捉.md](catalog/动作捕捉.md) |
| 游戏策划 | 3 | [catalog/游戏策划.md](catalog/游戏策划.md) |
| 游戏设计 | 1 | [catalog/游戏设计.md](catalog/游戏设计.md) |
| 游戏美术与叙事 | 4 | [catalog/游戏美术与叙事.md](catalog/游戏美术与叙事.md) |
| 游戏测试 | 1 | [catalog/游戏测试.md](catalog/游戏测试.md) |
| **合计** | **190** | |

## 安装量最高的技能

| # | 技能 | 分类 | 安装量 |
|---|---|---|---|
| 1 | [Godot大师技能](skills/godot-master/) | 游戏开发 | 91 |
| 2 | [游戏机制设计师](skills/game-mechanics-designer/) | 游戏策划 | 44 |
| 3 | [游戏设计](skills/game-design/) | 游戏开发 | 28 |
| 4 | [Blender集成技能](skills/blender-integration/) | Blender建模 | 20 |
| 5 | [Unity开发技能](skills/unity-development/) | 游戏开发 | 19 |
| 6 | [Godot引擎开发技能](skills/godot-development/) | 游戏开发 | 19 |
| 7 | [Godot卡牌游戏开发蓝图](skills/godot-genre-card-game/) | 游戏开发 | 16 |
| 8 | [游戏艺术](skills/game-art/) | 游戏策划 | 15 |
| 9 | [虚幻蓝图](skills/unreal-blueprint/) | Unreal Engine | 15 |
| 10 | [分镜故事板生成器](skills/storyboard-generator/) | 游戏美术与叙事 | 15 |
| 11 | [游戏引擎资源](skills/game-engine-resources/) | 游戏开发 | 11 |
| 12 | [Godot粒子系统技能](skills/godot-particles/) | 游戏开发 | 11 |
| 13 | [虚幻引擎C++编程](skills/unreal-cpp/) | Unreal Engine | 11 |
| 14 | [Godot实时战略游戏开发蓝图](skills/godot-genre-rts/) | 游戏开发 | 9 |
| 15 | [UnityUI界面开发工具包](skills/unity-ui-toolkit/) | Unity开发 | 9 |

## 使用方式

技能目录遵循常见的 Agent Skills 约定（`SKILL.md` + YAML frontmatter）。

```bash
# 方式一：整个目录拷进你的 Agent 技能目录
git clone https://github.com/leechary337688-sudo/game-production.git
cp -r game-production/skills/* ~/.claude/skills/

# 方式二：只取需要的技能
cp -r game-production/skills/godot-master ~/.claude/skills/
```

## 说明与限制

- SkillsBot 的技能正文为其中文译文，原始技能来自开源社区；每个技能的来源、原始项目名和安装量记录在 `skills/<技能名>/meta.json`。
- 同一技能在 SkillsBot 上可能有重复条目，已按 `en_name` 合并，被合并的条目 id 记录在 `meta.json` 的 `merged_ids` 中（若存在）。
- 本仓库只收录**正文（SKILL.md）**。部分技能在 SkillsBot 上还有附带资源文件，需要在 SkillsBot 登录后下载完整包（下载有次数限制）。
- 技能正文的版权归原作者；本仓库仅做检索整理，便于游戏项目直接取用。仓库自身的索引、脚本以 MIT 协议提供。
