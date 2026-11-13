---
名称：godot-ui-containers
描述："专家蓝图，用于使用容器节点（HBoxContainer、VBoxContainer、GridContainer、MarginContainer、ScrollContainer）进行响应式UI布局。涵盖大小标志、锚点、分割容器和动态布局。在构建自适应界面或实现响应式菜单时使用。关键词：容器、HBoxContainer、VBoxContainer、GridContainer、size_flags、EXPAND_FILL、锚点、响应式。"
---

# UI 容器

容器自动布局、大小标志、锚点和分割比例定义了响应式UI系统。

## 可用脚本

### [responsive_layout_builder.gd](scripts/responsive_layout_builder.gd)
基于断点的响应式布局专家容器构建器。

### [responsive_grid.gd](scripts/responsive_grid.gd)
自动调整的GridContainer，根据可用宽度改变列数。对于响应式库存屏幕和调整窗口大小至关重要。

## 在UI容器中永远不要做的事

- **永远不要在容器中手动设置子节点位置/大小** — 在HBoxContainer中设置`child.position = Vector2(10, 10)`？容器在布局时会覆盖它。使用`custom_minimum_size`或边距代替。
- **永远不要忘记扩展的大小标志** — VBoxContainer中的子节点不扩展？默认是SHRINK。设置`size_flags_vertical = SIZE_EXPAND_FILL`以获取填充行为。
- **永远不要使用没有列数的GridContainer** — 默认`columns = 1`的`GridContainer`？垂直列表，错误的布局。始终设置`columns`属性到网格宽度。
- **永远不要嵌套太多容器** — 10层的HBox在VBox在HBox中？重新布局开销大且难以调试。扁平化或使用Control自定义布局。
- **永远不要跳过分离覆盖** — 默认4px分离？拥挤的UI。使用`add_theme_constant_override("separation", value)`覆盖以获得呼吸空间。
- **永远不要使用没有最小大小的ScrollContainer** — 没有`custom_minimum_size`的ScrollContainer？无限扩展，没有滚动。设置最小大小或使用锚点。

---

```gdscript
# VBoxContainer 示例
# 自动垂直堆叠子节点
# 子节点：
#   Button ("Play")
#   Button ("Settings")
#   Button ("Quit")

# 设置项之间的分离
$VBoxContainer.add_theme_constant_override("separation", 10)
```

## 响应式布局

```gdscript
# 使用锚点和大小标志
func _ready() -> void:
    # 扩展以填充父节点
    $MarginContainer.set_anchors_preset(Control.PRESET_FULL_RECT)
    
    # 添加边距
    $MarginContainer.add_theme_constant_override("margin_left", 20)
    $MarginContainer.add_theme_constant_override("margin_right", 20)
```

## 大小标志

```gdscript
# 控制子节点在容器中的扩展方式
button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
```

## 参考
- [Godot 文档：GUI 容器](https://docs.godotengine.org/en/stable/tutorials/ui/gui_containers.html)


### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
