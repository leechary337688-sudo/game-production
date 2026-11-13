---
name: godot-ui-theming
description: "使用主题资源、StyleBoxes、自定义字体和主题覆盖实现一致 UI 视觉样式的专家蓝图。覆盖 StyleBoxFlat/Texture、主题继承、动态主题切换和字体变体。适用于实现一致 UI 样式或支持多主题的场景。关键词：主题、StyleBox、StyleBoxFlat、add_theme_override、字体、主题继承、暗黑模式。"
---

# UI 主题化

主题资源、StyleBox 样式、字体管理和覆盖系统定义一致的 UI 视觉标识。

## 可用脚本

### [global_theme_manager.gd](scripts/global_theme_manager.gd)
具有动态切换、主题变体和回退处理的专家主题管理器。

### [ui_scale_manager.gd](scripts/ui_scale_manager.gd)
运行时主题切换和 DPI/分辨率缩放管理。

## UI 主题化中切勿做

- **切勿在 _ready() 中为许多节点创建 StyleBox** — 100 个按钮 × `StyleBoxFlat.new()` 在 `_ready()` 中？100 个重复对象。在主题资源中创建一次，通过继承重用。
- **切勿忘记主题继承** — 子 Control 有自定义主题？父主题被忽略。在根 Control 上设置 `theme`，子节点自动继承除非覆盖。
- **切勿在 StyleBox 中硬编码颜色** — `style.bg_color = Color(0.2, 0.3, 0.5)`？难以维护。在主题中定义颜色，通过 `theme.get_color("primary", "Button")` 引用。
- **切勿使用 add_theme_override 处理全局样式** — 在 50 个节点上调用 `add_theme_*_override()`？脆弱。在主题资源中定义以实现自动传播。
- **切勿跳过 corner_radius_all 快捷方式** — 单独设置 4 个角半径？冗长。使用 `corner_radius_all = 5` 获得统一角（仅限 StyleBoxFlat）。
- **切勿在渲染期间修改主题** — 在 `_draw()` 或 `_process()` 中更改主题？持续重新布局 = 性能下降。仅在初始化或用户操作时加载主题。

---

1. 项目设置 → **GUI → 主题**
2. 创建新主题资源
3. 分配给根 Control 节点
4. 所有子节点继承主题

## StyleBox 模式

```gdscript
# 为按钮创建 StyleBoxFlat
var style := StyleBoxFlat.new()
style.bg_color = Color.DARK_BLUE
style.corner_radius_top_left = 5
style.corner_radius_top_right = 5
style.corner_radius_bottom_left = 5
style.corner_radius_bottom_right = 5

# 应用到按钮
$Button.add_theme_stylebox_override("normal", style)
```

## 字体加载

```gdscript
# 加载自定义字体
var font := load("res://fonts/my_font.ttf")
$Label.add_theme_font_override("font", font)
$Label.add_theme_font_size_override("font_size", 24)
```

## 参考
- [Godot Docs: GUI Theming](https://docs.godotengine.org/en/stable/tutorials/ui/gui_skinning.html)


### 相关
- 主技能: [godot-master](../godot-master/SKILL.md)
