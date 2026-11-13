---
名称: godot-testing-patterns
描述: "使用GUT（Godot单元测试）进行测试模式的专家蓝图，集成测试、模拟/存根模式、异步测试和验证技术。覆盖断言模式、信号测试和CI/CD集成。适用于实现测试或验证游戏逻辑。关键词GUT、单元测试、集成测试、断言、模拟、存根、GutTest、watch_signals、TDD。"
---

# 测试模式

GUT框架、断言模式、模拟和异步测试定义自动化验证。

## 可用脚本

### [integration_test_base.gd](scripts/integration_test_base.gd)
GUT集成测试的基类，带有自动清理和场景助手。

### [headless_test_runner.gd](scripts/headless_test_runner.gd)
专家级无头测试运行器，用于CI/CD，具有JUnit XML输出和退出码处理。

## 测试中永不做的事

- **永不测试实现细节** — `assert_eq(player._internal_state, 5)`? 私有变量 = 脆弱测试。测试公共行为，而不是内部。
- **永不测试之间共享状态** — 测试1修改全局变量，测试2假设干净状态？不稳定测试。使用`before_each()`进行新鲜设置。
- **永不使用sleep()进行定时** — `await get_tree().create_timer(1.0).timeout` 在测试中？慢 + 不可靠。使用GUT的`wait_seconds()`或手动帧步进。
- **永不在after_each()中跳过清理** — 测试生成100个节点，不释放？内存泄漏 + 慢测试套件。总是在`after_each()`中释放节点。
- **永不测试随机性而不设置种子** — `randi()`在测试中 = 非确定性失败。使用`seed(12345)`进行可重复测试。
- **永不忘记监视信号** — `assert_signal_emitted(obj, "died")` 没有 `watch_signals`? 静默失败。必须先调用`watch_signals(obj)`。

---

### 安装

1. 从AssetLib下载："GUT - Godot Unit Test"
2. 在项目设置 → 插件中启用
3. 创建 `res://test/` 目录

### 基本测试

```gdscript
# test/test_player.gd
extends GutTest

var player: CharacterBody2D

func before_each() -> void:
    player = preload("res://entities/player/player.tscn").instantiate()
    add_child(player)

func after_each() -> void:
    player.queue_free()

func test_initial_health() -> void:
    assert_eq(player.health, 100, "玩家应该以100生命值开始")

func test_take_damage() -> void:
    player.take_damage(25)
    assert_eq(player.health, 75, "受到25伤害后生命值应为75")

func test_cannot_have_negative_health() -> void:
    player.take_damage(200)
    assert_gte(player.health, 0, "生命值不应低于0")
```

### 运行测试

```gdscript
# 通过编辑器中的GUT面板
# 或命令行：
# godot --headless -s addons/gut/gut_cmdln.gd
```

## 断言模式

```gdscript
# 相等
assert_eq(actual, expected, "消息")
assert_ne(actual, not_expected, "消息")

# 比较
assert_gt(value, min_value, "应该大于")
assert_lt(value, max_value, "应该小于")
assert_gte(value, min_value, "应该>=最小")
assert_lte(value, max_value, "应该<=最大")

# 布尔
assert_true(condition, "应该为真")
assert_false(condition, "应该为假")

# 空
assert_not_null(object, "应该存在")
assert_null(object, "应该为空")

# 数组
assert_has(array, element, "应该包含元素")
assert_does_not_have(array, element, "不应该包含")

# 信号
watch_signals(object)
assert_signal_emitted(object, "signal_name")
```

## 测试信号

```gdscript
func test_death_signal() -> void:
    watch_signals(player)
    
    player.take_damage(100)
    
    assert_signal_emitted(player, "died")
    assert_signal_emitted_with_parameters(player, "died", [player])
```

## 测试异步

```gdscript
func test_delayed_action() -> void:
    player.start_ability()
    
    # 等待计时器
    await wait_seconds(1.0)
    
    assert_true(player.ability_active, "延迟后能力应该激活")
```

## 模拟/存根模式

```gdscript
# 双重（模拟）模式
func test_with_mock() -> void:
    var mock_enemy := double(Enemy).new()
    stub(mock_enemy, "get_damage").to_return(50)
    
    player.collide_with(mock_enemy)
    
    assert_eq(player.health, 50, "应该承受模拟伤害")
```

## 集成测试

```gdscript
# test/test_combat_system.gd
extends GutTest

func test_player_kills_enemy() -> void:
    var level := preload("res://levels/test_arena.tscn").instantiate()
    add_child(level)
    
    var player := level.get_node("Player")
    var enemy := level.get_node("Enemy")
    
    # 模拟战斗
    for i in range(5):
        player.attack(enemy)
        await wait_frames(1)
    
    assert_true(enemy.is_dead, "敌人应该死亡")
    assert_gt(player.score, 0, "玩家应该有分数")
    
    level.queue_free()
```

## 手动测试清单

```markdown
## 游戏玩法
- [ ] 玩家可以向所有方向移动
- [ ] 跳跃高度感觉正确
- [ ] 敌人对玩家有反应
- [ ] 伤害数字正确

## UI
- [ ] 所有按钮工作
- [ ] 文本可读
- [ ] 在不同分辨率下响应

## 音频
- [ ] 音乐播放
- [ ] SFX正确触发
- [ ] 音量平衡

## 性能
- [ ] 保持60 FPS
- [ ] 无卡顿
- [ ] 内存稳定
```

## 验证助手

```gdscript
# validation.gd（用于运行时检查）
class_name Validation

static func assert_valid_health(health: int) -> void:
    assert(health >= 0 and health <= 100, "无效生命值: %d" % health)

static func assert_valid_position(pos: Vector2, bounds: Rect2) -> void:
    assert(bounds.has_point(pos), "位置超出边界: %s" % pos)
```

## 测试组织

```
test/
├── unit/
│   ├── test_player.gd
│   ├── test_enemy.gd
│   └── test_inventory.gd
├── integration/
│   ├── test_combat.gd
│   └── test_save_load.gd
└── fixtures/
    ├── test_level.tscn
    └── mock_data.tres
```

## 最佳实践

### 1. 测试边缘情况

```gdscript
func test_edge_cases() -> void:
    player.take_damage(0)  # 零伤害
    assert_eq(player.health, 100)
    
    player.take_damage(-10)  # 负数（治疗？）
    assert_eq(player.health, 100)  # 不应改变
```

### 2. 隔离测试

```gdscript
# 每个测试应该独立
func before_each() -> void:
    # 为每个测试进行新鲜设置
    player = create_fresh_player()
```

### 3. 先测试关键路径

```
优先级：
1. 核心游戏玩法（移动、战斗）
2. 保存/加载系统
3. 关卡转换
4. UI交互
```

## 参考
- [GUT 文档](https://github.com/bitwes/Gut)


### 相关
- Master Skill: [godot-master](../godot-master/SKILL.md)
