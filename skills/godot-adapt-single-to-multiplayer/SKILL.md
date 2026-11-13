---
名称: Godot单机适配多玩家
描述: "专家模式，用于向单机游戏添加多玩家功能，包括客户端-服务器架构、权威服务器设计、MultiplayerSynchronizer、延迟补偿（客户端预测、服务器协调）、输入缓冲和防作弊措施。适用于改造多玩家、移植到在线游戏或设计网络游戏玩法。触发关键词: MultiplayerPeer, ENetMultiplayerPeer, SceneMultiplayer, MultiplayerSynchronizer, rpc, rpc_id, multiplayer_authority, client_prediction, server_reconciliation, lag_compensation, rollback."
---

# 适配：从单机到多玩家

专业指导，用于将多玩家功能改造到单机游戏中。

## 绝不这样做

- **绝不信任客户端输入** — 始终在服务器上验证。客户端可能发送虚假的位置/健康/库存数据。
- **绝不要使用 get_tree().get_nodes_in_group() 进行权限检查** — 在单个节点上使用 `is_multiplayer_authority()`。组迭代对网络身份不可靠。
- **绝不要忘记设置 multiplayer_authority** — 未分配权限的节点将导致不同步。服务器应拥有世界对象，客户端拥有其玩家。
- **绝不要在客户端和服务器上相同地运行物理** — 导致双倍速度移动。使用客户端预测与服务器协调或仅服务器物理。
- **绝不要每帧发送原始输入** — 在客户端缓冲输入，批量发送（每3-5帧）。减少带宽60-80%。

---

## 可用脚本

> **强制**：在实现相应模式前阅读适当脚本。

### [multiplayer_sync.gd](scripts/multiplayer_sync.gd)
延迟感知同步与MultiplayerSynchronizer。演示对等插值（插值到网络位置）和基于权限的更新逻辑。

### [rpc_bridge.gd](scripts/rpc_bridge.gd)
信号到RPC桥接模式。展示权限保护模式：客户端请求 → 服务器验证 → 服务器广播。防作弊必备。

---

## 架构模式

### 模式1：权威服务器（推荐）

```gdscript
# 服务器验证所有游戏逻辑
# 客户端发送输入 → 服务器处理 → 服务器广播状态

# 优点：安全，防止作弊
# 缺点：需要服务器托管，延迟影响游戏

# 适用于：竞技游戏、PvP、有经济系统的游戏
```

### 模式2：对等网络（锁步）

```gdscript
# 所有客户端运行相同的模拟
# 输入同步，确定性物理

# 优点：无需专用服务器
# 缺点：易受作弊影响，不同步常见

# 适用于：合作游戏、休闲游戏、小玩家数（2-4）
```

### 模式3：混合（权限转移）

```gdscript
# 主机充当服务器
# 权限可以在对等方之间转移

# 适用于：4-8玩家合作游戏、派对游戏
```

---

## 逐步迁移

### 步骤1：分离输入与逻辑

```gdscript
# ❌ 错误：输入直接修改状态（单机）
extends CharacterBody2D

func _physics_process(delta: float) -> void:
    var input := Input.get_vector("left", "right", "up", "down")
    velocity = input.normalized() * SPEED
    move_and_slide()

# ✅ 正确：输入 → 逻辑分离

extends CharacterBody2D

var current_input := Vector2.ZERO

func _physics_process(delta: float) -> void:
    # 仅当这是我们自己的玩家时读取输入
    if is_multiplayer_authority():
        current_input = Input.get_vector("left", "right", "up", "down")
        # 如果我们是客户端，发送输入到服务器
        if multiplayer.get_unique_id() != 1:  # 非服务器
            rpc_id(1, "receive_input", current_input)
    
    # 所有人处理移动（服务器 + 所有客户端）
    _process_movement(delta, current_input)

func _process_movement(delta: float, input: Vector2) -> void:
    velocity = input.normalized() * SPEED
    move_and_slide()

@rpc("any_peer", "call_remote", "unreliable")
func receive_input(input: Vector2) -> void:
    # 服务器接收客户端输入
    current_input = input
```

### 步骤2：设置多玩家权限

```gdscript
# server_setup.gd
extends Node

const PORT = 7777
const MAX_PLAYERS = 4

func host_game() -> void:
    var peer := ENetMultiplayerPeer.new()
    peer.create_server(PORT, MAX_PLAYERS)
    multiplayer.multiplayer_peer = peer
    
    multiplayer.peer_connected.connect(_on_player_connected)
    multiplayer.peer_disconnected.connect(_on_player_disconnected)
    
    print("服务器在端口 %d 上启动" % PORT)

func join_game(ip: String) -> void:
    var peer := ENetMultiplayerPeer.new()
    peer.create_client(ip, PORT)
    multiplayer.multiplayer_peer = peer
    
    print("连接到 %s:%d" % [ip, PORT])

func _on_player_connected(id: int) -> void:
    print("玩家 %d 连接" % id)
    spawn_player(id)

func _on_player_disconnected(id: int) -> void:
    print("玩家 %d 断开连接" % id)
    despawn_player(id)

func spawn_player(id: int) -> void:
    var player := preload("res://player.tscn").instantiate()
    player.name = str(id)  # 关键：名称必须唯一且匹配对等ID
    player.set_multiplayer_authority(id)  # 客户端拥有自己的玩家
    get_node("/root/World").add_child(player, true)  # true：复制到所有对等方
```

### 步骤3：添加MultiplayerSynchronizer

```gdscript
# 场景结构：
# Player (CharacterBody2D)
#   ├─ Sprite2D
#   ├─ CollisionShape2D
#   └─ MultiplayerSynchronizer

# MultiplayerSynchronizer 设置（在编辑器中）：
# - 根路径："../"  （指向Player节点）
# - 复制间隔：0.05  （20Hz 更新）
# - 公共可见性：true
# - 同步属性：
#     - position
#     - rotation
#     - velocity （可选，用于插值）

# 无需代码！MultiplayerSynchronizer 自动同步属性
```

---

## 客户端预测与服务器协调

### 问题：延迟使游戏感觉不响应

```gdscript
# 无预测：
# 1. 客户端按下 W
# 2. 输入发送到服务器
# 3. 服务器处理（50ms后）
# 4. 服务器发回位置
# 5. 客户端看到移动（100ms RTT）
# 结果：输入和视觉反馈之间有100ms延迟
```

### 解决方案：客户端侧预测

```gdscript
# player_controller.gd
extends CharacterBody2D

var input_buffer: Array = []
var server_state := {"position": Vector2.ZERO, "tick": 0}

func _physics_process(delta: float) -> void:
    if is_multiplayer_authority():
        var input := Input.get_vector("left", "right", "up", "down")
        
        # 客户端立即预测移动
        var tick := Engine.get_physics_frames()
        input_buffer.append({"input": input, "tick": tick})
        process_movement(input)
        
        # 发送输入到服务器
        if multiplayer.get_unique_id() != 1:
            rpc_id(1, "server_receive_input", input, tick)
    
    else:
        # 其他玩家：仅显示同步位置（无预测）
        pass

@rpc("any_peer", "call_remote", "unreliable")
func server_receive_input(input: Vector2, client_tick: int) -> void:
    # 服务器处理输入
    process_movement(input)
    
    # 发送权威状态回
    rpc_id(multiplayer.get_remote_sender_id(), "client_receive_state", position, client_tick)

@rpc("authority", "call_remote", "unreliable")
func client_receive_state(server_pos: Vector2, server_tick: int) -> void:
    # 协调：检查预测是否正确
    var error := position.distance_to(server_pos)
    
    if error > 5.0:  # 校正阈值
        # 跳转到服务器位置
        position = server_pos
        
        # 重播 server_tick 后发生的输入
        for buffered_input in input_buffer:
            if buffered_input.tick > server_tick:
                process_movement(buffered_input.input)
    
    # 清理旧输入
    input_buffer = input_buffer.filter(func(i): return i.tick > server_tick)

func process_movement(input: Vector2) -> void:
    velocity = input.normalized() * SPEED
    move_and_slide()
```

---

## 延迟补偿技术

### 插值（其他玩家平滑）

```gdscript
# 其他玩家由于丢包/抖动显得卡顿
# 解决方案：在接收状态间插值

extends CharacterBody2D

var position_buffer: Array = []
const BUFFER_SIZE = 3  # 存储最后3个位置

func _ready() -> void:
    if not is_multiplayer_authority():
        # 禁用本地物理，使用插值
        set_physics_process(false)

func _process(delta: float) -> void:
    if not is_multiplayer_authority() and position_buffer.size() >= 2:
        # 在缓冲位置间插值
        var from := position_buffer[0]
        var to := position_buffer[1]
        var t := 0.2  # 插值速度
        
        position = position.lerp(to, t)
        
        if position.distance_to(to) < 1.0:
            position_buffer.pop_front()

# 由 MultiplayerSynchronizer 在位置更新时调用
func _on_position_synced(new_pos: Vector2) -> void:
    position_buffer.append(new_pos)
    if position_buffer.size() > BUFFER_SIZE:
        position_buffer.pop_front()
```

---

## 防作弊措施

### 服务器侧验证

```gdscript
# server_validator.gd
extends Node

const MAX_SPEED = 300.0
const MAX_TELEPORT_DISTANCE = 50.0

@rpc("any_peer", "call_remote", "reliable")
func request_move(new_position: Vector2) -> void:
    var sender_id := multiplayer.get_remote_sender_id()
    var player := get_node("/root/World/" + str(sender_id))
    
    # 验证移动
    var distance := player.position.distance_to(new_position)
    var delta := get_physics_process_delta_time()
    var max_allowed := MAX_SPEED * delta
    
    if distance > max_allowed:
        push_warning("玩家 %d 传送了 %f 单位（最大：%f）" % [sender_id, distance, max_allowed])
        # 拒绝移动，强制服务器位置
        rpc_id(sender_id, "force_position", player.position)
        return
    
    # 接受移动
    player.position = new_position

@rpc("authority", "call_remote", "reliable")
func force_position(server_position: Vector2) -> void:
    position = server_position
```

---

## 带宽优化

### 输入缓冲

```gdscript
# ❌ 错误：每帧发送输入（60包/秒）
func _physics_process(delta: float) -> void:
    var input := get_input()
    rpc_id(1, "receive_input", input)

# ✅ 正确：每第3帧发送（20包/秒）
var input_timer := 0.0
const INPUT_SEND_RATE = 0.05  # 20 Hz

func _physics_process(delta: float) -> void:
    input_timer += delta
    if input_timer >= INPUT_SEND_RATE:
        var input := get_input()
        rpc_id(1, "receive_input", input)
        input_timer = 0.0
```

---

## 本地测试多玩家

```gdscript
# 启动多个实例进行测试
# 从命令行运行：

# Windows：
# 服务器：Godot.exe --path . res://main.tscn -- --server
# 客户端1：Godot.exe --path . res://main.tscn -- --client
# 客户端2：Godot.exe --path . res://main.tscn -- --client

# 在代码中解析参数：
func _ready() -> void:
    var args := OS.get_cmdline_args()
    if "--server" in args:
        host_game()
    elif "--client" in args:
        join_game("127.0.0.1")
```

---

## 决策树：哪种架构？

| 因素 | 权威服务器 | P2P锁步 |
|------|------------|---------|
| 玩家数 | 8-100+ | 2-4 |
| 防作弊 | 关键 | 不重要 |
| 服务器托管 | 可用 | 不可用 |
| 游戏类型 | PvP, 竞技 | 合作, 休闲 |
| 延迟容忍度 | 中（预测帮助） | 低（不同步） |
| 开发复杂度 | 高 | 中 |


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
