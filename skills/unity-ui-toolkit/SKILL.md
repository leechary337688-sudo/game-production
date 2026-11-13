---
名称: unity-ui-toolkit
描述: 用于运行时UI开发的Unity UI Toolkit技能，包含USS样式设计、UXML模板和自定义可视化元素。
允许使用的工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity UI Toolkit 技能

用于Unity运行时和编辑器界面的UI Toolkit开发。

## 概述

此技能提供了使用Unity的UI Toolkit构建用户界面的能力，包括UXML模板、USS样式设计和自定义可视化元素。

## 能力

### UXML 模板
- 创建UXML文档结构
- 定义可复用的模板
- 实现数据绑定
- 处理模板继承

### USS 样式设计
- 编写USS样式表
- 实现响应式布局
- 创建主题变体
- 处理悬停/聚焦状态

### 可视化元素
- 构建自定义可视化元素
- 实现操作器
- 处理输入事件
- 创建动画

### 数据绑定
- 绑定到数据源
- 实现MVVM模式
- 处理列表视图和集合
- 创建响应式UI

## 先决条件

- Unity 2021.3+
- UI Toolkit 包（内置）

## 使用模式

### UXML 模板

```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
    <ui:VisualElement class="container">
        <ui:Label name="health-label" text="生命值: 100" />
        <ui:ProgressBar name="health-bar" value="100" />
        <ui:Button name="heal-button" text="治疗" />
    </ui:VisualElement>
</ui:UXML>
```

### USS 样式表

```css
.container {
    flex-direction: column;
    padding: 10px;
    background-color: rgba(0, 0, 0, 0.8);
}

#health-bar {
    height: 20px;
    margin: 5px 0;
}

#heal-button:hover {
    background-color: #4CAF50;
}
```

### C# 绑定

```csharp
public class HealthUI : MonoBehaviour
{
    [SerializeField] private UIDocument uiDocument;
    private ProgressBar healthBar;

    void Start()
    {
        var root = uiDocument.rootVisualElement;
        healthBar = root.Q<ProgressBar>("health-bar");
        root.Q<Button>("heal-button").clicked += OnHealClicked;
    }

    void OnHealClicked() { /* 处理治疗逻辑 */ }
}
```

## 最佳实践

1. 使用USS进行样式设计，而非内联样式
2. 创建可复用的UXML模板
3. 实现适当的事件处理
4. 跨分辨率测试
5. 使用UI Builder进行可视化编辑

## 参考

- [UI Toolkit 文档](https://docs.unity3d.com/Manual/UIElements.html)
