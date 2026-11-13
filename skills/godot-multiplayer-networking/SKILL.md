---
名称: godot-multiplayer-networking
描述: "使用Godot高级API的多人在线网络专家蓝图（Among Us, Brawlhalla, Terraria），涵盖RPCs、状态同步、权威服务器、客户端预测和大厅系统。在构建在线多人在线游戏、LAN合作或网络游戏时使用。关键词：多人在线、RPC、ENetMultiplayerPeer、MultiplayerSynchronizer、权威、客户端预测、回滚。"
---

# 多人在线网络编程

权威服务器、客户端预测和状态同步定义了健壮的多人在线。

## 可用脚本

### [server_authoritative_controller.gd](scripts/server_authoritative_controller.gd)
高级玩家控制器，具有客户端预测、服务器协调和插值。

### [client_prediction_synchronizer.gd](scripts/client_prediction_synchronizer.gd)
专家级客户端预测与服务器协调模式。

## 多人在线网络编程中绝不要做的事

- **绝不要在没有服务器验证的情况下信任客户端输入** — 客户端发送“造成9999伤害”的RPC？作弊。服务器必须验证动作：`if not multiplayer.is_server(): return`。
- **绝不要使用 `@rpc("any_peer")` 进行游戏动作** — 任何对等体都可以调用 = 作弊向量。对于伤害/生成，使用 `@rpc("authority")`。只有聊天/装饰品使用 `any_peer`。
- **绝不要使用可靠RPCs进行位置更新** — 每秒60次位置更新使用 `"reliable"` = 带宽爆炸 + 延迟。对于频繁、非关键数据，使用 `"unreliable"`。
- **绝不要忘记设置多人在线权威** — 客户端和服务器都处理输入？不同步。调用 `set_multiplayer_authority(peer_id)` 并检查 `is_multiplayer_authority()`。
- **绝不要同步每个变量** — MultiplayerSynchronizer同步50个属性 = 带宽浪费。只同步其他客户端需要的状态（跳过动画帧、本地UI状态）。
- **绝不要在 `peer.create_server()` 上阻塞** — ENet是异步的。在服务器准备好之前调用 `multiplayer.multiplayer_peer = peer` = 崩溃。等待 `peer_connected` 信号。
- **绝不要忘记为远程玩家插值** — 传送远程玩家（直接位置分配）= 抖动。使用 `lerp()` 在接收位置之间平滑。

---

**权威服务器模型：**
- 服务器验证所有游戏状态
- 客户端发送输入，接收状态
- 防止作弊

**对等网络：**
- 直接玩家连接
- 适用于小玩家数量
- 无需专用服务器

## 基本设置

### 创建多人在线对等体

```gdscript
extends Node

var peer := ENetMultiplayerPeer.new()

func host_game(port: int = 7777) -> void:
    peer.create_server(port, 4)  # 最多4个玩家
    multiplayer.multiplayer_peer = peer
    print("服务器已启动在端口 ", port)

func join_game(ip: String, port: int = 7777) -> void:
    peer.create_client(ip, port)
    multiplayer.multiplayer_peer = peer
    print("正在连接到 ", ip)
```

### 连接信号

```gdscript
func _ready() -> void:
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    multiplayer.connected_to_server.connect(_on_connected)
    multiplayer.connection_failed.connect(_on_connection_failed)

func _on_peer_connected(id: int) -> void:
    print("玩家已连接: ", id)

func _on_peer_disconnected(id: int) -> void:
    print("玩家已断开连接: ", id)

func _on_connected() -> void:
    print("已连接到服务器！")

func _on_connection_failed() -> void:
    print("连接失败")
```

## 远程过程调用（RPCs）

### 基本RPC

```gdscript
extends CharacterBody2D

# 在所有对等体上调用
@rpc("any_peer", "call_local")
func take_damage(amount: int) -> void:
    health -= amount
    if health <= 0:
        die()

# 用法：在特定对等体上调用
take_damage.rpc_id(1, 50)  # 在服务器（ID 1）上调用
take_damage.rpc(50)  # 在所有对等体上调用
```

### RPC模式

```gdscript
# 只有服务器可以调用，在所有客户端上运行
@rpc("authority", "call_remote")
func server_spawn_enemy(pos: Vector2) -> void:
    pass

# 任何对等体都可以调用，本地也运行
@rpc("any_peer", "call_local")
func player_chat(message: String) -> void:
    pass

# 可靠（类似TCP） vs 不可靠（类似UDP）
@rpc("any_peer", "call_local", "reliable")
func important_event() -> void:
    pass

@rpc("any_peer", "call_local", "unreliable")
func position_update(pos: Vector2) -> void:
    pass
```

## MultiplayerSpawner

```gdscript
# 添加MultiplayerSpawner节点
# 设置生成路径和场景

extends Node

@onready var spawner := $MultiplayerSpawner

func _ready() -> void:
    spawner.spawn_function = spawn_player

func spawn_player(data: Variant) -> Node:
    var player := preload("res://player.tscn").instantiate()
    player.name = str(data)  # 使用对等体ID作为名称
    return player
```

## MultiplayerSynchronizer

```gdscript
# 添加到同步节点
# 设置要同步的属性

# 场景结构：
# Player (CharacterBody2D)
#   ├─ MultiplayerSynchronizer
#   │    └─ 复制配置：
#   │         - 位置 (同步)
#   │         - 速度 (同步)
#   │         - 生命值 (同步)
#   └─ Sprite2D
```

## 大厅系统

```gdscript
# lobby_manager.gd (自动加载)
extends Node

signal player_joined(id: int, info: Dictionary)
signal player_left(id: int)

var players: Dictionary = {}

func _ready() -> void:
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)

func _on_peer_connected(id: int) -> void:
    # 请求玩家信息
    request_player_info.rpc_id(id)

func _on_peer_disconnected(id: int) -> void:
    players.erase(id)
    player_left.emit(id)

@rpc("any_peer", "reliable")
func request_player_info() -> void:
    var sender_id := multiplayer.get_remote_sender_id()
    receive_player_info.rpc_id(sender_id, {
        "name": PlayerSettings.player_name,
        "color": PlayerSettings.player_color
    })

@rpc("any_peer", "reliable")
func receive_player_info(info: Dictionary) -> void:
    var sender_id := multiplayer.get_remote_sender_id()
    players[sender_id] = info
    player_joined.emit(sender_id, info)
```

## 状态同步

```gdscript
extends CharacterBody2D

var puppet_position: Vector2
var puppet_velocity: Vector2

func _physics_process(delta: float) -> void:
    if is_multiplayer_authority():
        # 本地玩家：处理输入
        _handle_input(delta)
        move_and_slide()
        
        # 发送位置给其他玩家
        sync_position.rpc(global_position, velocity)
    else:
        # 远程玩家：插值
        global_position = global_position.lerp(puppet_position, 10.0 * delta)

@rpc("any_peer", "unreliable")
func sync_position(pos: Vector2, vel: Vector2) -> void:
    puppet_position = pos
    puppet_velocity = vel
```

## 权威

```gdscript
# 检查谁拥有这个节点
func _ready() -> void:
    # 设置权威给拥有者对等体
    set_multiplayer_authority(peer_id)

func _process(delta: float) -> void:
    if not is_multiplayer_authority():
        return  # 如果不是拥有者，跳过
    
    # 只有权威处理这个
```

## 最佳实践

### 1. 在服务器上验证

```gdscript
@rpc("any_peer", "call_local")
func player_action(action: String) -> void:
    if not multiplayer.is_server():
        return  # 只有服务器验证
    
    var sender := multiplayer.get_remote_sender_id()
    if not _is_valid_action(sender, action):
        return
    
    _apply_action.rpc(sender, action)
```

### 2. 使用不可靠更新进行频繁更新

```gdscript
# 位置：不可靠（频繁）
@rpc("any_peer", "unreliable")
func sync_position(pos: Vector2) -> void:
    pass

# 伤害：可靠（重要）
@rpc("authority", "reliable")
func apply_damage(amount: int) -> void:
    pass
```

### 3. 插值实现平滑移动

```gdscript
var target_position: Vector2

func _process(delta: float) -> void:
    if not is_multiplayer_authority():
        position = position.lerp(target_position, 15.0 * delta)
```

## 参考
- [Godot 文档：高级多人在线](https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html)

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
