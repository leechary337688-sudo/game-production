---
name: godot-mcp-setup
description: "[前提条件] 安装和配置 Godot MCP 服务器，通过 Model Context Protocol 实现程序化场景操作。仅在用户明确请求基于 MCP 的场景构建或自动化时使用。不适用于手动 Godot 工作流。关键词 MCP, Model Context Protocol, 场景自动化, npx, claude_desktop_config."
---

# Godot MCP 设置

使 AI 代理能够安装和配置 Godot MCP (Model Context Protocol) 服务器，用于程序化场景管理。

## 何时使用此技能

**仅在以下情况使用：**
- 用户明确请求基于 MCP 的场景构建
- 用户希望程序化创建或修改场景
- 用户询问场景自动化工具

**除非满足条件，否则不要建议：**
- 用户对 MCP 功能表示兴趣
- 替代手动方法不足够

## 可用脚本

### [mcp_config_generator.gd](scripts/mcp_config_generator.gd)
工具脚本，用于生成 Claude Desktop 配置 JSON，适用于 Godot MCP。

## MCP 设置中绝对不要做的事

- **绝对不要为简单场景编辑建议 MCP** — MCP 适用于自动化或批量操作。单节点添加？使用手动编辑器。MCP 开销（配置+重启）浪费时间。
- **绝对不要跳过 JSON 语法验证** — 在 `claude_desktop_config.json` 中的无效 JSON 会导致 MCP 静默失败。保存前务必使用 `ConvertFrom-Json` 验证。
- **绝对不要忘记提醒用户重启 Claude Desktop** — MCP 更改需要完全重启应用，不仅仅是新对话。这是用户最常见的错误。
- **绝对不要未经用户许可使用全局 npm 安装** — `npm install -g` 修改系统。除非用户特别要求全局，否则始终优先使用 `npx`（按需）。
- **绝对不要假设 Node.js 已安装** — 在尝试 npx 之前检查 `node --version`。缺少 Node 会导致晦涩的“命令未找到”错误。

---

## 安装工作流程

### 步骤 1：检查 MCP 是否已安装

**对于 PowerShell (Windows)：**
```powershell
# 检查 Godot MCP 服务器是否已配置
$mcpConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
if (Test-Path $mcpConfigPath) {
    $config = Get-Content $mcpConfigPath | ConvertFrom-Json
    if ($config.mcpServers.godot) {
        Write-Host "Godot MCP 服务器已配置。"
    }
}
```

### 步骤 2：安装 Godot MCP 服务器

**安装命令 (npx)：**
```powershell
# 全局安装
npm install -g @modelcontextprotocol/server-godot

# 或使用 npx 进行按需执行
npx @modelcontextprotocol/server-godot
```

### 步骤 3：配置 Claude Desktop

MCP 服务器必须在 Claude Desktop 的配置文件中注册。

**配置文件位置：**
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**示例配置：**
```json
{
  "mcpServers": {
    "godot": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-godot"]
    }
  }
}
```

### 步骤 4：重启 Claude Desktop

配置后，用户必须重启 Claude Desktop 以使 MCP 更改生效。

## 验证

安装后，通过检查 `mcp_godot_*` 工具是否可访问来验证 MCP 工具可用。

## 常见问题

**问题**: MCP 服务器在重启后未出现
- **解决方案**: 验证 `claude_desktop_config.json` 中的 JSON 语法
- **解决方案**: 检查 Node.js 和 npm 是否已安装

**问题**: 安装过程中出现权限错误
- **解决方案**: 在 Windows 上以管理员身份运行 PowerShell

## 参考
- Godot MCP 服务器: [GitHub 仓库](https://github.com/modelcontextprotocol/servers/tree/main/src/godot)
- MCP 协议: [官方文档](https://modelcontextprotocol.io/)


### 相关
- 主技能: [godot-master](../godot-master/SKILL.md)
