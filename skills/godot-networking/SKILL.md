---
名称: godot-networking
描述: Godot引擎的高级网络API、RPC和点对点网络多人游戏技能。
允许工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Godot网络技能

用于Godot引擎的多人网络功能。

## 概述

本技能提供了使用Godot网络系统实现多人游戏的能力。

## 功能

- 配置多人网络对等体
- 实现远程过程调用（RPC）
- 处理同步
- 管理对等体连接

## 使用模式

```gdscript
@rpc("any_peer", "call_local", "reliable")
func sync_position(pos: Vector2):
    position = pos
```

## 参考

- [Godot网络文档](https://docs.godotengine.org/en/stable/tutorials/networking/)
