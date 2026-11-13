---
名称: godot-project-foundations
描述: "Godot 4项目组织的专家蓝图（基于特征的基础文件夹、命名约定、版本控制）。强制执行snake_case文件、PascalCase节点、%SceneUniqueNames和.gitignore最佳实践。用于启动新项目或重构结构。关键词：项目组织，命名约定，snake_case，PascalCase，特征基础，.gitignore，.gdignore。"
---

# 项目基础

基于特征的组织、一致的命名和版本控制卫生定义了专业的Godot项目。

## 可用脚本

> **强制 - 对于新项目**：在搭建脚手架之前，阅读 [`project_bootstrapper.gd`](scripts/project_bootstrapper.gd) - 自动生成特征文件夹和.gitignore。

### [project_bootstrapper.gd](scripts/project_bootstrapper.gd)
专家项目脚手架工具，用于自动生成特征文件夹和.gitignore。

### [scene_naming_validator.gd](scripts/scene_naming_validator.gd)
扫描整个项目以查找snake_case/PascalCase违规。在PR之前运行。

### [dependency_auditor.gd](scripts/dependency_auditor.gd)
检测循环场景依赖和耦合问题。对于超过50个场景的项目至关重要。

### [feature_scaffolder.gd](scripts/feature_scaffolder.gd)
生成完整的特征文件夹，包括基础场景、脚本和子文件夹。

> **不要加载** dependency_auditor.gd，除非在故障排除加载错误或审计大型项目时。


## 在项目组织中绝不做的事

- **绝不按文件类型分组** — `/scripts`、`/sprites`、`/sounds`文件夹？维护噩梦。使用基于特征的：`/player`、`/enemies`、`/ui`。
- **绝不在文件中混合snake_case和PascalCase** — `PlayerController.gd` vs `player_controller.gd`？选择一个。官方标准：文件使用snake_case，节点使用PascalCase。
- **绝不忘记.gitignore** — 提交`.godot/`文件夹 = 100MB+膨胀 + 合并冲突。始终包括Godot特定的.gitignore。
- **绝不使用硬编码的get_node()路径** — `get_node("../../../Player/Sprite2D")`在场景重新父级化时会破坏。使用`%SceneUniqueNames`以获得稳定的引用。
- **绝不为原始资源跳过.gdignore** — 项目根目录中的设计源文件（`.psd`、`.blend`）= Godot导入它们。添加`.gdignore`以从导入过程中排除。

---

### 1. 命名约定
- **文件和文件夹**：始终使用`snake_case`。（例如：`player_controller.gd`、`main_menu.tscn`）。
    - *例外*：C#脚本应使用`PascalCase`以匹配类名。
- **节点名称**：始终使用`PascalCase`（例如：`PlayerSprite`、`CollisionShape2D`）。
- **唯一名称**：使用`%SceneUniqueNames`用于频繁访问的节点，以避免脆弱的`get_node()`路径。

### 2. 基于特征的组织
而不是按*类型*分组（例如：`/scripts`、`/sprites`），按*特征*分组（“什么”，而不是“如何”）。

**正确结构：**
```
/project.godot
/common/           # 全局资源、主题、共享脚本
/entities/
    /player/       # 与玩家相关的所有内容
        player.tscn
        player.gd
        player_sprite.png
    /enemy/
/ui/
    /main_menu/
/levels/
/addons/           # 第三方插件
```

### 3. 版本控制
- 始终包括一个为Godot定制的`.gitignore`（忽略`.godot/`文件夹和导入工件）。
- 在Godot不应扫描/导入的文件夹中使用`.gdignore`（例如：原始设计源文件）。

## 工作流程：搭建新项目

当被要求“设置项目”或“开始新游戏”时：

1. **初始化根目录**：确保`project.godot`存在。
2. **创建核心文件夹**：
   - `entities/`
   - `ui/`
   - `levels/`
   - `common/`
3. **设置Git**：创建一个全面的`.gitignore`。
4. **文档**：创建一个`README.md`解释基于特征的结构。

## 参考
- 官方文档：`tutorials/best_practices/project_organization.rst`
- 官方文档：`tutorials/best_practices/scene_organization.rst`


### 相关
- 精通技能：[godot-master](../godot-master/SKILL.md)
