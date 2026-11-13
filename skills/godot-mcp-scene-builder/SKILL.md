---
name: godot-mcp-scene-builder
description: "[MCP 包装器] 使用 Godot MCP 工具程序化创建/修改 Godot 场景。将 mcp_godot_create_scene、mcp_godot_add_node、mcp_godot_load_sprite 编排到智能体工作流中。当用户通过 MCP 请求场景生成/自动化时使用。关键词 MCP、场景自动化、程序化场景构建、节点层次结构。"
---

# MCP 场景构建器

用于从零构建场景的高级智能体接口，基于底层 Godot MCP 工具。

## MCP 场景构建中切勿做的事

- **切勿跳过设计阶段** — 不规划层次结构就直接跳转到 `mcp_godot_add_node` 会导致场景混乱。务必先起草节点树。
- **切勿在添加节点前假设场景存在** — 在不存在的场景上调用 `mcp_godot_add_node` 会导致错误。必须先调用 `mcp_godot_create_scene`。
- **切勿在 MCP 调用中使用绝对路径** — `texturePath="C:/Users/..."` 在其他机器上会失败。只使用 `res://` 路径。
- **切勿跳过验证步骤** — MCP 创建 .tscn 文件但不验证。务必调用 `mcp_godot_run_project` 或 `mcp_godot_launch_editor` 来验证无错误。
- **切勿添加 CollisionShape2D 而不设置形状** — MCP 添加节点但 `shape` 属性默认为空。必须手动设置，否则场景会损坏。

---

## 可用脚本

### [scene_builder_manifest.gd](scripts/scene_builder_manifest.gd)
通过 MCP 进行声明式场景构建的资源定义。

## 可用 MCP 工具摘要
- `mcp_godot_create_scene`: 初始化一个 `.tscn` 文件。
- `mcp_godot_add_node`: 向现有场景添加节点。
- `mcp_godot_load_sprite`: 为 `Sprite2D` 节点分配纹理。
- `mcp_godot_run_project`: 启动 Godot 编辑器以验证结果。

## 工作流：构建场景

当被要求“创建场景”、“制作角色”或“设置关卡”时：

1. **设计阶段**：
   - 确定根节点类型（例如，`CharacterBody2D`、`Node3D`、`Control`）。
   - 起草节点层次结构（例如，根 -> Sprite2D、CollisionShape2D）。

2. **执行阶段（MCP 管道）**：
   - **步骤 1**：调用 `mcp_godot_create_scene` 创建文件。
   - **步骤 2**：依次为每个子节点调用 `mcp_godot_add_node`。
   - **步骤 3**（可选）：如果需要精灵，调用 `mcp_godot_load_sprite`。
   - **步骤 4**：（关键验证）调用 `mcp_godot_run_project` 或 `mcp_godot_launch_editor`。

3. **优化阶段**：
   - 在附加脚本时应用 `godot-gdscript-mastery` 标准。

## 示例：创建一个基本的 2D 玩家

**提示**：“创建一个带有精灵和碰撞的 2D 玩家场景。”

**计划**：
1. `mcp_godot_create_scene(scenePath="player.tscn", rootNodeType="CharacterBody2D")`
2. `mcp_godot_add_node(scenePath="player.tscn", nodeType="Sprite2D", nodeName="Skin", parentNodePath=".")`
3. `mcp_godot_add_node(scenePath="player.tscn", nodeType="CollisionShape2D", nodeName="Hitbox", parentNodePath=".")`
4. `mcp_godot_load_sprite(scenePath="player.tscn", nodePath="Skin", texturePath="res://icon.svg")`

## 验证
智能体必须验证场景在编辑器中打开时无错误。

## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
