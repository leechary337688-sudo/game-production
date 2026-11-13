---
name: godot-skill-judge
description: "用于验证其他技能完整性和质量的元技能。自动检查SKILL.md的存在、脚本语法错误（通过Godot CLI）和元数据完整性。使用此技能验证整个技能库。触发关键词：验证、持续集成、质量保证、语法检查、元数据检查。"
---

# 技能法官

质量的守护者。

## 职责

1. **存在性检查**：确保每个技能文件夹有`SKILL.md`。
2. **元数据验证**：确保`SKILL.md`有有效的YAML frontmatter，包含`name`和`description`。
3. **脚本验证**：扫描所有`.gd`文件并检查基本解析错误。
4. **Godot 4兼容性**：扫描被禁止的Godot 3关键词（如`move_and_slide(vec)`、`rotation_degrees`向量使用错误等）。

## 可用脚本

### [skill_validator.gd](scripts/skill_validator.gd)
核心验证引擎。可以作为EditorScript或通过CLI运行。

## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
