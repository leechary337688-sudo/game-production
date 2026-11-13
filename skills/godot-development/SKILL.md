---
name: godot-development
description: Godot引擎集成技能，用于GDScript/C#开发、场景组合、节点管理和编辑器自动化。使LLM能够通过MCP服务器与Godot编辑器交互，进行资源操作、脚本生成和自动化工作流。
allowed-tools: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Godot开发技能

全面的Godot引擎开发集成，用于AI辅助游戏创建、编辑器自动化和项目管理。

## 概述

此技能提供与Godot项目交互的能力，包括GDScript和C#开发、场景操作、节点管理和导出自动化。当可用时，它利用Godot MCP生态系统进行直接编辑器集成。

## 能力

### 项目管理
- 创建和配置Godot项目
- 管理项目设置（project.godot）
- 配置导出预设
- 设置自动加载和单例

### GDScript开发
- 生成扩展Node、Node2D、Node3D等的脚本
- 为数据驱动设计创建自定义资源
- 实现信号和信号连接
- 编写用于编辑器功能的工具脚本
- 使用GUT或gdUnit4生成单元测试

### C#开发（Godot Mono）
- 使用适当的Godot绑定生成C#脚本
- 在C#中创建自定义资源
- 为节点脚本实现部分类
- 与.NET库交互

### 场景组合
- 以编程方式创建和修改场景
- 实例化和配置节点
- 设置节点层次结构和所有权
- 配置场景继承

### 资源系统
- 创建自定义资源类型
- 生成数据资源
- 管理资源路径和加载
- 配置资源导入

### 导出系统
- 为多个平台配置导出预设
- 为自动化创建导出脚本
- 设置CI/CD导出流水线
- 管理平台特定配置

## 先决条件

### Godot安装
- 推荐Godot 4.0或更高版本
- 安装Godot编辑器并包含所需的导出模板

### MCP服务器（推荐）
用于直接Godot编辑器集成：

```json
{
  "mcpServers": {
    "godot": {
      "command": "npx",
      "args": ["-y", "godot-mcp"],
      "env": {
        "GODOT_PROJECT_PATH": "/path/to/godot/project"
      }
    }
  }
}
```

替代MCP服务器：
- `Godot-MCP` (ee0pdt) - 全面的编辑器集成
- `godot-mcp` (Coding-Solo) - 项目启动和调试
- `GDAI MCP Server` - 带截图的脚本修复

## 使用模式

### 创建角色控制器（GDScript）

```gdscript
extends CharacterBody2D
class_name PlayerController

## 每秒移动速度（像素）
@export var move_speed: float = 200.0
## 跳跃速度
@export var jump_velocity: float = -400.0

## 来自项目设置的重力
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

## 玩家受到伤害时发出
signal damage_taken(amount: int)
## 玩家死亡时发出
signal died

var _is_alive: bool = true

func _physics_process(delta: float) -> void:
    if not _is_alive:
        return

    _apply_gravity(delta)
    _handle_jump()
    _handle_movement()
    move_and_slide()

func _apply_gravity(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta

func _handle_jump() -> void:
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

func _handle_movement() -> void:
    var direction := Input.get_axis("move_left", "move_right")
    if direction:
        velocity.x = direction * move_speed
    else:
        velocity.x = move_toward(velocity.x, 0, move_speed)

func take_damage(amount: int) -> void:
    damage_taken.emit(amount)

func die() -> void:
    _is_alive = false
    died.emit()
```

### 创建自定义资源（GDScript）

```gdscript
@tool
extends Resource
class_name EnemyData

## 敌人的显示名称
@export var enemy_name: String = "Enemy"
## 用于UI的敌人图标
@export var icon: Texture2D
## 最大生命值
@export var max_health: int = 100
## 移动速度
@export var move_speed: float = 100.0

@export_group("战斗")
## 每次攻击造成的伤害
@export var attack_damage: int = 10
## 攻击范围（像素）
@export var attack_range: float = 50.0
## 攻击之间的冷却时间
@export var attack_cooldown: float = 1.0

@export_group("奖励")
## 死亡时奖励的经验值
@export var exp_reward: int = 50
## 可能掉落的物品
@export var loot_table: Array[PackedScene]

## 获取每秒伤害潜力
func get_dps() -> float:
    return attack_damage / attack_cooldown
```

### 状态机模式（GDScript）

```gdscript
extends Node
class_name StateMachine

## 状态变化时发出
signal state_changed(old_state: State, new_state: State)

@export var initial_state: State

var current_state: State
var states: Dictionary = {}

func _ready() -> void:
    for child in get_children():
        if child is State:
            states[child.name.to_lower()] = child
            child.state_machine = self

    if initial_state:
        current_state = initial_state
        current_state.enter()

func _process(delta: float) -> void:
    if current_state:
        current_state.update(delta)

func _physics_process(delta: float) -> void:
    if current_state:
        current_state.physics_update(delta)

func _unhandled_input(event: InputEvent) -> void:
    if current_state:
        current_state.handle_input(event)

func transition_to(state_name: String) -> void:
    var new_state: State = states.get(state_name.to_lower())
    if new_state == null:
        push_warning("未找到状态 '%s'" % state_name)
        return

    if current_state:
        current_state.exit()

    var old_state := current_state
    current_state = new_state
    current_state.enter()
    state_changed.emit(old_state, new_state)
```

### 创建C#脚本（Godot Mono）

```csharp
using Godot;
using System;

public partial class PlayerController : CharacterBody2D
{
    [Export]
    public float MoveSpeed { get; set; } = 200.0f;

    [Export]
    public float JumpVelocity { get; set; } = -400.0f;

    [Signal]
    public delegate void DamageTakenEventHandler(int amount);

    [Signal]
    public delegate void DiedEventHandler();

    private float _gravity = ProjectSettings.GetSetting("physics/2d/default_gravity").AsSingle();
    private bool _isAlive = true;

    public override void _PhysicsProcess(double delta)
    {
        if (!_isAlive) return;

        Vector2 velocity = Velocity;

        // 应用重力
        if (!IsOnFloor())
        {
            velocity.Y += _gravity * (float)delta;
        }

        // 处理跳跃
        if (Input.IsActionJustPressed("jump") && IsOnFloor())
        {
            velocity.Y = JumpVelocity;
        }

        // 处理移动
        float direction = Input.GetAxis("move_left", "move_right");
        velocity.X = direction != 0 ? direction * MoveSpeed : Mathf.MoveToward(velocity.X, 0, MoveSpeed);

        Velocity = velocity;
        MoveAndSlide();
    }

    public void TakeDamage(int amount)
    {
        EmitSignal(SignalName.DamageTaken, amount);
    }

    public void Die()
    {
        _isAlive = false;
        EmitSignal(SignalName.Died);
    }
}
```

## 与Babysitter SDK集成

### 任务定义示例

```javascript
const godotScriptTask = defineTask({
  name: 'godot-script-generation',
  description: '生成Godot脚本',

  inputs: {
    language: { type: 'string', required: true }, // gdscript, csharp
    baseClass: { type: 'string', required: true },
    className: { type: 'string', required: true },
    features: { type: 'array', required: true },
    outputPath: { type: 'string', required: true }
  },

  outputs: {
    scriptPath: { type: 'string' },
    success: { type: 'boolean' }
  },

  async run(inputs, taskCtx) {
    return {
      kind: 'skill',
      title: `生成Godot脚本: ${inputs.className}`,
      skill: {
        name: 'godot-development',
        context: {
          operation: 'generate_script',
          language: inputs.language,
          baseClass: inputs.baseClass,
          className: inputs.className,
          features: inputs.features,
          outputPath: inputs.outputPath
        }
      },
      io: {
        inputJsonPath: `tasks/${taskCtx.effectId}/input.json`,
        outputJsonPath: `tasks/${taskCtx.effectId}/result.json`
      }
    };
  }
});
```

## MCP服务器集成

### 可用MCP工具（通过godot-mcp）

| 工具 | 描述 |
|------|-------------|
| `godot_create_node` | 在场景中创建节点 |
| `godot_modify_node` | 修改节点属性 |
| `godot_create_script` | 生成并附加脚本 |
| `godot_run_project` | 在编辑器中启动项目 |
| `godot_run_scene` | 运行特定场景 |
| `godot_export` | 为目标平台导出 |
| `godot_get_scene_tree` | 查询场景结构 |
| `godot_read_errors` | 获取编辑器错误输出 |
| `godot_screenshot` | 捕获视口截图 |

### 配置

```json
{
  "mcpServers": {
    "godot": {
      "command": "python",
      "args": ["-m", "godot_mcp"],
      "env": {
        "GODOT_PROJECT_PATH": "/path/to/godot/project",
        "GODOT_EXECUTABLE": "/path/to/godot"
      }
    }
  }
}
```

## 最佳实践

1. **使用静态类型**：始终使用类型提示以获得更好的性能和自动完成
2. **信号优于直接调用**：使用信号实现节点之间的松耦合
3. **资源预加载**：对频繁使用的资源使用preload()
4. **场景继承**：对变体使用继承场景
5. **自动加载**：谨慎使用，优先考虑依赖注入
6. **@tool脚本**：标记需要在编辑器中运行的脚本

## 平台考虑

| 平台 | 关键考虑因素 |
|----------|-------------------|
| PC/Mac/Linux | 完整功能支持 |
| 移动端 | 触摸输入、简化着色器、导出模板 |
| Web | 无线程、WASM限制 |
| 游戏主机 | 需要第三方发布合作伙伴 |

## 参考

- [Godot文档](https://docs.godotengine.org/)
- [Godot-MCP (ee0pdt)](https://github.com/ee0pdt/Godot-MCP)
- [godot-mcp (Coding-Solo)](https://github.com/Coding-Solo/godot-mcp)
- [GDAI MCP Server](https://gdaimcp.com/)
- [GDScript风格指南](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)
- [Godot最佳实践](https://docs.godotengine.org/en/stable/tutorials/best_practices/)
