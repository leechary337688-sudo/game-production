---
name: godot-ui-rich-text
description: "专家蓝图，用于RichTextLabel和BBCode格式化（加粗、斜体、颜色、图片、可点击链接）和自定义效果。涵盖元标签、RichTextEffect着色器和动态内容。用于实现对话系统或格式化文本。关键词：RichTextLabel, BBCode, [b], [color], [url], meta_clicked, RichTextEffect, 对话。"
---

# 富文本与BBCode

BBCode标签、元可点击链接和RichTextEffect着色器定义了格式化文本系统。

## 可用脚本

### [custom_bbcode_effect.gd](scripts/custom_bbcode_effect.gd)
专家自定义RichTextEffect示例（波浪、彩虹、抖动、打字机效果）。

### [rich_text_animator.gd](scripts/rich_text_animator.gd)
BBCode文本的打字机效果，支持自定义事件标签和暂停。

## 在富文本中切勿做的事情

- **切勿忘记bbcode_enabled** — `text = "[b]加粗[/b]"` 未设置 `bbcode_enabled = true`？显示字面括号。始终先启用BBCode。
- **切勿使用[img]而无res://路径** — `[img]icon.png[/img]` 使用相对路径？图像未找到。使用完整资源路径：`[img]res://assets/icon.png[/img]`。
- **切勿跳过换行符保留** — `text = "行1\n行2"` 渲染为 "行1行2"？BBCode吞掉换行符。使用 `[br]` 或带正确转义的 `\n`。
- **切勿使用[url]而无meta_clicked** — `[url=shop]购买[/url]` 未连接信号？点击无响应。必须连接 `meta_clicked` 信号。
- **切勿嵌套相同类型标签** — `[b][b]文本[/b][/b]`？行为未定义。嵌套不同标签：`[b][i]文本[/i][/b]`。
- **切勿使用[color]带无效格式** — `[color=redd]文本[/color]` 拼写错误？回退到白色或黑色。使用命名颜色或十六进制：`[color=#FF0000]` 以验证。

---

```gdscript
$RichTextLabel.bbcode_enabled = true
$RichTextLabel.text = "[b]加粗[/b] 和 [i]斜体[/i] 文本"
```

## 常见标签

```bbcode
[b]加粗[/b]
[i]斜体[/i]
[u]下划线[/u]
[color=red]红色文本[/color]
[color=#00FF00]绿色十六进制[/color]
[center]居中[/center]
[img]res://icon.png[/img]
[url=data]可点击链接[/url]
```

## 处理链接点击

```gdscript
func _ready() -> void:
    $RichTextLabel.meta_clicked.connect(_on_meta_clicked)

func _on_meta_clicked(meta: Variant) -> void:
    print("点击了：", meta)
```

## 参考
- [Godot 文档：RichTextLabel中的BBCode](https://docs.godotengine.org/en/stable/tutorials/ui/bbcode_in_richtextlabel.html)


### 相关
- 精通技能：[godot-master](../godot-master/SKILL.md)
