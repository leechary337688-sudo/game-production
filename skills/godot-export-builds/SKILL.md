---
name: godot-export-builds
description: "多平台导出的专家模式，包括导出模板（Windows/Linux/macOS/Android/iOS/Web）、命令行导出（无头模式）、平台特定设置（代码签名、公证、Android SDK）、功能标志（OS.has_feature）、CI/CD 管道（GitHub Actions）和构建优化（大小减少、调试剥离）。用于发布准备或自动化部署。触发关键词：export_preset、export_template、headless_export、platform_specific、feature_flag、CI_CD、build_optimization、codesign、Android_SDK。"
---

# 导出与构建

为跨平台构建和分发Godot游戏提供专家指导。

## 永不操作

- **永远不要在目标平台上测试前导出** — "在我的机器上工作"不意味着在Windows/Linux/Android上工作。尽早并频繁测试。
- **永远不要使用调试构建进行发布** — 调试构建大5-10倍且更慢。始终使用 --export-release 进行生产导出。
- **永远不要在导出中硬编码文件路径** — 使用 `res://` 和 `user://` 路径。绝对路径（`C:/Users/...`）在其他机器上会破坏。
- **永远不要在macOS上跳过代码签名** — 未签名的macOS应用触发Gatekeeper警告。用户不会运行你的游戏。
- **永远不要在导出中包含仅编辑器文件** — 通过导出过滤器排除 `.md`、`docs/*`、`.git`。减少构建大小20-50%。
---

## 可用脚本

> **必读**: 在实现相应模式前阅读适当脚本。

### [version_manager.gd](scripts/version_manager.gd)
AutoLoad用于管理游戏版本、构建哈希和窗口标题。

### [headless_build.sh](scripts/headless_build.sh)
CI/CD 无头导出脚本。自动化版本注入、godot --headless --export-release、代码签名和butler部署。

---

## 导出模板

**通过编辑器安装：**
编辑器 → 管理导出模板 → 下载

## 基本导出设置

### 创建导出预设

1. 项目 → 导出
2. 添加预设（Windows、Linux等）
3. 配置设置
4. 导出项目

### Windows 导出

```ini
# 导出设置
# 格式：.exe（单个文件）或 .pck + .exe
# 图标：.ico 文件
# 包含：*.import、*.tres、*.tscn
```

### Web 导出

```ini
# 设置：
# 导出类型：常规或 GDExtension
# 线程支持：用于 SharedArrayBuffer
# VRAM 压缩：优化大小
```

## 导出预设文件

```ini
# export_presets.cfg

[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
runnable=true
export_path="builds/windows/game.exe"

[preset.0.options]
binary_format/64_bits=true
application/icon="res://icon.ico"
```

## 命令行导出

```powershell
# 从命令行导出
godot --headless --export-release "Windows Desktop" builds/game.exe

# 导出调试构建
godot --headless --export-debug "Windows Desktop" builds/game_debug.exe

# 仅 PCK（用于修补）
godot --headless --export-pack "Windows Desktop" builds/game.pck
```

## 平台特定

### Android

```ini
# 要求：
# - Android SDK
# - OpenJDK 17
# - 调试密钥库

# 编辑器设置：
# 导出 → Android → SDK 路径
# 导出 → Android → 密钥库
```

### iOS

```ini
# 要求：
# - 带 Xcode 的 macOS
# - Apple 开发者账户
# - 配置文件

# 导出创建 .xcodeproj
# 在 Xcode 中为 App Store 构建
```

### macOS

```ini
# 设置：
# 代码签名：Developer ID 证书
# 公证：分发必需
# 架构：通用（Intel + ARM）
```

## 功能标志

```gdscript
# 运行时检查平台
if OS.get_name() == "Windows":
    # Windows 特定代码
    pass

if OS.has_feature("web"):
    # Web 构建
    pass

if OS.has_feature("mobile"):
    # Android 或 iOS
    pass
```

## 导出的项目设置

```ini
# project.godot

[application]
config/name="我的游戏"
config/version="1.0.0"
run/main_scene="res://scenes/main.tscn"
config/icon="res://icon.svg"

[rendering]
# 为目标平台优化
textures/vram_compression/import_etc2_astc=true  # 移动设备
```

## 构建优化

### 减少构建大小

```gdscript
# 移除未使用的导入
# 项目设置 → 编辑器 → 导入默认值

# 排除仅编辑器文件
# 在导出预设中：排除过滤器
*.md
*.txt
docs/*
```

### 剥离调试符号

```ini
# 导出预设选项：
# 调试 → 调试：关闭
# 二进制格式 → 架构：仅64位
```

## 使用 GitHub Actions 的 CI/CD

```yaml
# .github/workflows/export.yml
name: 导出 Godot 游戏

on:
  push:
    tags: ['v*']

jobs:
  export:
    runs-on: ubuntu-latest
    container:
      image: barichello/godot-ci:4.2.1
    
    steps:
      - uses: actions/checkout@v4
      
      - name: 导出 Windows
        run: |
          mkdir -p builds/windows
          godot --headless --export-release "Windows Desktop" builds/windows/game.exe
      
      - name: 上传 Artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-build
          path: builds/windows/
```

## 版本管理

```gdscript
# version.gd（AutoLoad）
extends Node

const VERSION := "1.0.0"
const BUILD := "2024.02.06"

func get_version_string() -> String:
    return "v" + VERSION + " (" + BUILD + ")"
```

## 最佳实践

### 1. 尽早测试导出

```
早期导出到所有目标平台
快速捕获平台特定问题
```

### 2. 使用 .gdignore

```
# 从导出中排除文件夹
# 在文件夹中创建 .gdignore
```

### 3. 分离调试/发布

```
调试：保留日志、开发工具
发布：剥离调试、优化大小
```

## 参考
- [Godot 文档：导出](https://docs.godotengine.org/en/stable/tutorials/export/index.html)


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
