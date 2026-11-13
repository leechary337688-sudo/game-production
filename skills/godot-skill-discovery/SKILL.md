---
name: godot-skill-discovery
description: "GDSkills 技能发现和索引系统的专家蓝图。使 AI 代理能通过主题/关键词找到相关技能。在构建技能库或实现搜索功能时使用。关键词：技能发现、索引、搜索、元数据、技能注册表。"
---

# 技能发现

技能索引、元数据解析和搜索定义了高效技能库导航。

## 可用脚本

### [skill_index_generator.gd](scripts/skill_index_generator.gd)
专家技能索引器，解析 SKILL.md 文件并生成可搜索的元数据。

## 技能发现中永远不要做的事

- **永远不要依赖文件名进行技能标识** — `filesystem-advanced.md` vs `SKILL.md`？使用前置元数据中的 `name` 字段作为真相来源，而非文件名。
- **永远不要跳过关键词提取** — 没有关键词的技能？无法通过搜索发现。必须从描述中提取或维护关键词列表。
- **永远不要缓存而不失效** — 技能索引已缓存，SKILL.md 更新？结果过时。在文件修改或版本变化时使缓存失效。
- **永远不要使用无排名的全文搜索** — 搜索100个技能中的“input”？返回所有结果。使用TF-IDF或关键词加权进行相关性排序。
- **永远不要忘记处理缺失的前置元数据** — 没有 `---` 分隔符的格式错误的SKILL.md？解析器崩溃。解析前验证YAML前置元数据。

---

## 技能元数据格式

```yaml
---
name: skill-name
description: 专家蓝图，包括[功能]。在[场景]时使用。关键词 主题、动作、领域。
---
```

## 索引模式

```gdscript
# skill_indexer.gd
class_name SkillIndexer
extends RefCounted

var skill_registry: Dictionary = {}

func index_skills(skills_dir: String) -> void:
    var dir := DirAccess.open(skills_dir)
    if not dir:
        return
    
    dir.list_dir_begin()
    var file_name := dir.get_next()
    
    while file_name != "":
        if dir.current_is_dir():
            var skill_path := skills_dir.path_join(file_name).path_join("SKILL.md")
            if FileAccess.file_exists(skill_path):
                index_skill(skill_path)
        file_name = dir.get_next()

func index_skill(path: String) -> void:
    var file := FileAccess.open(path, FileAccess.READ)
    if not file:
        return
    
    var content := file.get_as_text()
    var metadata := parse_frontmatter(content)
    
    if metadata.has("name"):
        skill_registry[metadata.name] = {
            "path": path,
            "description": metadata.get("description", ""),
            "keywords": extract_keywords(metadata.get("description", ""))
        }

func parse_frontmatter(content: String) -> Dictionary:
    var lines := content.split("\n")
    if lines[0].strip_edges() != "---":
        return {}
    
    var frontmatter_lines: Array[String] = []
    for i in range(1, lines.size()):
        if lines[i].strip_edges() == "---":
            break
        frontmatter_lines.append(lines[i])
    
    var metadata := {}
    for line in frontmatter_lines:
        var parts := line.split(":", true, 1)
        if parts.size() == 2:
            metadata[parts[0].strip_edges()] = parts[1].strip_edges()
    
    return metadata

func search_skills(query: String) -> Array[Dictionary]:
    var results: Array[Dictionary] = []
    var query_lower := query.to_lower()
    
    for skill_name in skill_registry:
        var skill_data := skill_registry[skill_name]
        var relevance := 0.0
        
        # 检查名称匹配
        if skill_name.to_lower().contains(query_lower):
            relevance += 10.0
        
        # 检查描述匹配
        if skill_data.description.to_lower().contains(query_lower):
            relevance += 5.0
        
        # 检查关键词匹配
        for keyword in skill_data.keywords:
            if keyword.to_lower() == query_lower:
                relevance += 20.0  # 精确关键词匹配
            elif keyword.to_lower().contains(query_lower):
                relevance += 3.0
        
        if relevance > 0:
            results.append({
                "name": skill_name,
                "relevance": relevance,
                "data": skill_data
            })
    
    # 按相关性排序
    results.sort_custom(func(a, b): return a.relevance > b.relevance)
    return results

func extract_keywords(description: String) -> Array[String]:
    var keywords: Array[String] = []
    
    # 从“关键词 X, Y, Z”模式提取
    var keyword_marker := "Keywords "
    var keyword_index := description.find(keyword_marker)
    if keyword_index != -1:
        var keyword_section := description.substr(keyword_index + keyword_marker.length())
        var parts := keyword_section.split(".", true, 1)
        var keyword_str := parts[0] if parts.size() > 0 else keyword_section
        
        for word in keyword_str.split(","):
            keywords.append(word.strip_edges())
    
    return keywords
```

## 最佳实践

1. **版本化技能索引** — 在元数据中包含技能版本以进行兼容性检查
2. **积极缓存** — 在索引构建时解析 SKILL.md，缓存结果以快速搜索
3. **支持模糊匹配** — 允许搜索中的拼写错误（例如，Levenshtein距离）
4. **分类分组** — 按类别组织技能以便浏览（2D、3D、类型等）

## 参考
- 相关：`godot-project-foundations`、`godot-gdscript-mastery`

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
