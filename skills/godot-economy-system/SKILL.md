---
名称: godot-economy-system
描述: "游戏经济的专家模式，包括货币管理（多货币、钱包系统）、商店系统（买入/卖出价格、库存限制）、动态定价（供需）、掉落表（加权掉落、稀有度等级）和经济平衡（通货膨胀控制、货币汇流）。适用于RPG、交易游戏或资源管理系统。触发关键词：EconomyManager, currency, shop_item, loot_table, dynamic_pricing, buy_sell_spread, currency_sink, inflation, item_rarity。"
---

# 经济系统

设计平衡的游戏经济的专家指导，包括货币、商店和掉落。

## 绝不这样做

- **绝不要使用 `int` 表示货币** — 对于小金额使用 `int`，但对于大型经济使用 `float` 或自定义 BigInt。整数溢出会破坏经济（最大21亿）。
- **绝不要忘记买入/卖出价格差** — 卖出价格与买入价格相同会创建无限金钱循环。卖出价格应为买入价格的30-50%。
- **绝不要跳过货币汇流** — 没有汇流（修理、税收、消耗品），经济会膨胀。玩家囤积无限财富。
- **绝不要使用客户端货币验证** — 客户端计算“我有1000金币”。服务器验证所有交易，否则会发生漏洞利用。
- **绝不要硬编码掉落几率** — 使用资源或JSON用于掉落表。设计者需要迭代而无需代码更改。
---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [loot_table_weighted.gd](scripts/loot_table_weighted.gd)
使用累积概率的加权掉落表。基于资源的设计允许设计者通过检查器进行迭代而无需代码更改。

---

## 货币管理器

```gdscript
# economy_manager.gd (AutoLoad)
extends Node

signal currency_changed(old_amount: int, new_amount: int)

var gold: int = 0

func add_currency(amount: int) -> void:
    var old := gold
    gold += amount
    currency_changed.emit(old, gold)

func spend_currency(amount: int) -> bool:
    if gold < amount:
        return false
    
    var old := gold
    gold -= amount
    currency_changed.emit(old, gold)
    return true

func has_currency(amount: int) -> bool:
    return gold >= amount
```

## 商店系统

```gdscript
# shop_item.gd
class_name ShopItem
extends Resource

@export var item: Item
@export var buy_price: int
@export var sell_price: int
@export var stock: int = -1  # -1 = 无限

func can_buy() -> bool:
    return stock != 0
```

```gdscript
# shop.gd
class_name Shop
extends Resource

@export var shop_name: String
@export var items: Array[ShopItem] = []

func buy_item(shop_item: ShopItem, inventory: Inventory) -> bool:
    if not shop_item.can_buy():
        return false
    
    if not EconomyManager.has_currency(shop_item.buy_price):
        return false
    
    if not EconomyManager.spend_currency(shop_item.buy_price):
        return false
    
    inventory.add_item(shop_item.item, 1)
    
    if shop_item.stock > 0:
        shop_item.stock -= 1
    
    return true

func sell_item(item: Item, inventory: Inventory) -> bool:
    # 查找匹配的商店物品以获取卖出价格
    var shop_item := get_shop_item_for(item)
    if not shop_item:
        return false
    
    if not inventory.has_item(item, 1):
        return false
    
    inventory.remove_item(item, 1)
    EconomyManager.add_currency(shop_item.sell_price)
    return true

func get_shop_item_for(item: Item) -> ShopItem:
    for shop_item in items:
        if shop_item.item == item:
            return shop_item
    return null
```

## 定价公式

```gdscript
func calculate_sell_price(buy_price: int, markup: float = 0.5) -> int:
    # 以买入价格的50%卖出
    return int(buy_price * markup)

func calculate_dynamic_price(base_price: int, demand: float) -> int:
    # 价格随需求增加
    return int(base_price * (1.0 + demand))
```

## 掉落表

```gdscript
# loot_table.gd
class_name LootTable
extends Resource

@export var drops: Array[LootDrop] = []

func roll_loot() -> Array[Item]:
    var items: Array[Item] = []
    
    for drop in drops:
        if randf() < drop.chance:
            items.append(drop.item)
    
    return items
```

```gdscript
# loot_drop.gd
class_name LootDrop
extends Resource

@export var item: Item
@export var chance: float = 0.5
@export var min_amount: int = 1
@export var max_amount: int = 1
```

## 最佳实践

1. **平衡** - 仔细测试经济
2. **汇流** - 提供金钱汇流（修理等）
3. **通货膨胀** - 控制金钱生成

## 参考
- 相关：`godot-inventory-system`, `godot-save-load-systems`


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
