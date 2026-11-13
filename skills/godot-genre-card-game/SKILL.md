---
name: godot-genre-card-game
description: "专家蓝图用于数字卡牌游戏（CCG/Deckbuilders），包括卡牌数据结构（基于资源）、牌库管理（抽牌/弃牌/重洗）、回合逻辑、手牌布局（弧形）、拖放UI、效果解析（命令模式）和视觉优化（Godot补间、着色器）。适用于CCG、deckbuilders或战术卡牌游戏。触发关键词：card_game, deck_manager, card_data, hand_layout, drag_drop_cards, effect_resolution, command_pattern, draw_pile, discard_pile。"
---

# 类型：卡牌游戏

数字卡牌游戏的专家蓝图，采用数据驱动设计和流畅的UI。

## 切勿操作

- **切勿在卡牌脚本中硬编码卡牌效果** — 使用命令模式或effect_script资源。使设计师无需代码即可创建卡牌。
- **切勿使用global_position进行手牌布局** — 手牌卡应使用相对于手牌容器的局部位置。global_position会因相机移动而失效。
- **切勿忘记将弃牌堆重洗入抽牌堆** — 当抽牌堆为空时，重洗弃牌堆。否则游戏会软锁。
- **切勿忽略z_index管理** — 拖动的卡牌必须具有最高的z_index。使用`move_to_front()`或设置`z_index = 999`。
- **切勿使用瞬时卡牌移动** — 没有补间动画的卡牌感觉糟糕。即使是0.2秒的补间也能大幅提升体验。
---

## 可用脚本

> **强制**：在实施相应模式前阅读适当脚本。

### [card_effect_resolution.gd](scripts/card_effect_resolution.gd)
用于卡牌效果解析的FILO堆栈。支持反应/反击卡牌（后进先出解析）、动画的视觉传递和多态效果分发。

---

## 核心循环
1.  **抽牌**：玩家从牌库抽牌到手牌。
2.  **评估**：玩家评估棋盘状态、法力/能量和卡牌选项。
3.  **出牌**：玩家出牌触发效果（伤害、增益、召唤）。
4.  **解析**：效果立即发生或进入堆栈。
5.  **弃牌/结束**：未使用的卡牌被弃置（roguelike风格）或保留（TCG风格），回合结束。

## 技能链

| 阶段 | 技能 | 目的 |
|-------|--------|---------|
| 1. 数据 | `resources`, `custom-resources` | 定义卡牌属性（成本、类型、效果） |
| 2. UI | `control-nodes`, `layout-containers` | 手牌布局、卡牌定位、工具提示 |
| 3. 输入 | `drag-and-drop`, `state-machines` | 拖动卡牌到目标、悬停 |
| 4. 逻辑 | `command-pattern`, `signals` | 执行卡牌效果、回合阶段 |
| 5. 优化 | `godot-tweening`, `shaders` | 抽牌动画、全息箔效果 |

## 架构概述

### 1. 卡牌数据（基于资源）
Godot资源非常适合卡牌数据。

```gdscript
# card_data.gd
extends Resource
class_name CardData

enum Type { ATTACK, SKILL, POWER }
enum Target { ENEMY, SELF, ALL_ENEMIES }

@export var id: String
@export var name: String
@export_multiline var description: String
@export var cost: int
@export var type: Type
@export var target_type: Target
@export var icon: Texture2D
@export var effect_script: Script # 每张卡牌的自定义逻辑
```

### 2. 牌库管理器
处理牌堆：抽牌堆、手牌、弃牌堆、消耗堆。

```gdscript
# deck_manager.gd
var draw_pile: Array[CardData] = []
var hand: Array[CardData] = []
var discard_pile: Array[CardData] = []

func draw_cards(amount: int) -> void:
    for i in amount:
        if draw_pile.is_empty():
            reshuffle_discard()
            
        if draw_pile.is_empty(): 
            break # 没有剩余卡牌
            
        var card = draw_pile.pop_back()
        hand.append(card)
        card_drawn.emit(card)

func reshuffle_discard() -> void:
    draw_pile.append_array(discard_pile)
    discard_pile.clear()
    draw_pile.shuffle()
```

### 3. 卡牌视觉（UI）
代表手牌中卡牌的交互节点。

```gdscript
# card_ui.gd
extends Control

var card_data: CardData
var start_pos: Vector2
var is_dragging: bool = false

func _gui_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            start_drag()
        else:
            end_drag()

func _process(delta: float) -> void:
    if is_dragging:
        global_position = get_global_mouse_position() - size / 2
    else:
        # 悬停效果或返回到手牌位置
        pass
```

## 关键机制实现

### 效果解析（命令模式）
将卡牌的“出牌”与其“效果”解耦。

```gdscript
func play_card(card: CardData, target: Node) -> void:
    if current_energy < card.cost:
        show_error("能量不足")
        return
        
    current_energy -= card.cost
    
    # 执行效果
    var effect = card.effect_script.new()
    effect.execute(target)
    
    move_to_discard(card)
```

### 手牌布局（弧形）
手牌通常形成弧形。使用数学公式（贝塞尔曲线或圆形）基于`index`和`total_cards`定位。

```gdscript
func update_hand_visuals() -> void:
    var center_x = screen_width / 2
    var radius = 1000.0
    var angle_step = 5.0
    
    for i in hand_visuals.size():
        var card = hand_visuals[i]
        var angle = deg_to_rad((i - hand_visuals.size() / 2.0) * angle_step)
        var target_pos = Vector2(
            center_x + sin(angle) * radius,
            screen_height + cos(angle) * radius
        )
        card.target_rotation = angle
        card.target_position = target_pos
```

## 常见陷阱

1.  **复杂性过载**：关键词过多。**修复**：坚持3-5个核心关键词（例如，嘲讽、毒药、护盾），并缓慢扩展。
2.  **文本不可读**：卡牌上字体过小。**修复**：使用图标表示常见属性（伤害、格挡），并保持文本简短。
3.  **动画锁定**：等待慢动画完成后再出下一张牌。**修复**：允许排队操作或保持动画快速（< 0.3秒）。

## Godot特定提示

*   **MouseFilter**：要使拖放在与重叠UI中工作，需要仔细设置`mouse_filter`（Pass vs Stop）。
*   **Z-Index**：使用`z_index`或`CanvasLayer`确保拖动的卡牌始终位于最顶层。
*   **补间**：必不可少！使用补间调整位置、旋转和缩放，以实现“流畅”的Hearthstone/Slay the Spire感觉。


## 参考
- 大师技能：[godot-master](../godot-master/SKILL.md)
