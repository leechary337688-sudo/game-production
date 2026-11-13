---
名称: unity-development
描述: Unity引擎集成技能，用于项目设置、C#脚本编写、场景管理、预制体创建和编辑器自动化。使LLM能够通过MCP服务器与Unity编辑器交互，进行资产操作、脚本生成和自动化工作流。
允许工具: Read, Grep, Write, Bash, Edit, Glob, WebFetch
---

# Unity开发技能

全面的Unity引擎开发集成，用于AI辅助游戏创建、编辑器自动化和项目管理。

## 概述

此技能提供与Unity项目交互的能力，包括C#脚本编写、场景操作、预制体管理和构建自动化。当可用时，它利用Unity MCP生态系统进行直接编辑器集成。

## 能力

### 项目管理
- 创建和配置Unity项目
- 管理项目设置（玩家设置、质量设置等）
- 通过包管理器配置包依赖
- 为代码组织设置程序集定义

### C#脚本编写
- 生成具有适当生命周期方法的MonoBehaviour脚本
- 创建用于数据驱动设计的ScriptableObjects
- 实现接口（ISerializationCallbackReceiver等）
- 编写自定义编辑器脚本和PropertyDrawers
- 使用Unity测试框架生成单元测试

### 场景管理
- 以编程方式创建和修改场景
- 实例化和配置游戏对象
- 设置场景层次结构和父子关系
- 配置灯光、摄像机和后期处理

### 预制体系统
- 创建和修改预制体资产
- 处理预制体变体和覆盖
- 生成带有修改的预制体实例
- 管理嵌套预制体

### 资产管道
- 导入和配置资产（纹理、模型、音频）
- 设置资产包和可寻址资产
- 为优化配置导入设置
- 生成占位符资产

### 构建系统
- 为多个平台配置构建设置
- 创建用于自动化的构建脚本
- 设置CI/CD构建管道
- 管理平台特定配置

## 先决条件

### Unity安装
- 推荐Unity 2021.3 LTS或更高版本
- 安装Unity编辑器及所需模块

### MCP服务器（推荐）
用于直接Unity编辑器集成：

```json
{
  "mcpServers": {
    "unity": {
      "command": "npx",
      "args": ["-y", "unity-mcp"],
      "env": {
        "UNITY_PROJECT_PATH": "/path/to/unity/project"
      }
    }
  }
}
```

替代MCP服务器：
- `unity-mcp` (CoplayDev) - 官方Unity MCP桥接
- `Unity-MCP` (IvanMurzak) - 编辑器与运行时支持
- `mcp-unity` (CoderGamester) - Cursor/Claude Code集成

## 使用模式

### 创建MonoBehaviour脚本

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [Header("移动设置")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;

    [Header("地面检测")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundRadius = 0.2f;
    [SerializeField] private LayerMask groundLayer;

    private Rigidbody2D rb;
    private bool isGrounded;

    private void Awake()
    {
        rb = GetComponent<Rigidbody2D>();
    }

    private void Update()
    {
        isGrounded = Physics2D.OverlapCircle(groundCheck.position, groundRadius, groundLayer);
        HandleInput();
    }

    private void FixedUpdate()
    {
        HandleMovement();
    }

    private void HandleInput()
    {
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.AddForce(Vector2.up * jumpForce, ForceMode2D.Impulse);
        }
    }

    private void HandleMovement()
    {
        float horizontal = Input.GetAxisRaw("Horizontal");
        rb.velocity = new Vector2(horizontal * moveSpeed, rb.velocity.y);
    }
}
```

### 创建ScriptableObject

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "NewEnemyData", menuName = "Game/Enemy Data")]
public class EnemyData : ScriptableObject
{
    [Header("基础信息")]
    public string enemyName;
    public Sprite icon;

    [Header("属性")]
    public int maxHealth = 100;
    public float moveSpeed = 3f;
    public int damage = 10;

    [Header("战斗")]
    public float attackRange = 2f;
    public float attackCooldown = 1.5f;

    [Header("奖励")]
    public int experienceReward = 50;
    public GameObject[] lootDrops;
}
```

### 编辑器脚本示例

```csharp
using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(EnemyData))]
public class EnemyDataEditor : Editor
{
    public override void OnInspectorGUI()
    {
        EnemyData enemyData = (EnemyData)target;

        EditorGUILayout.BeginHorizontal();
        if (enemyData.icon != null)
        {
            GUILayout.Box(enemyData.icon.texture, GUILayout.Width(64), GUILayout.Height(64));
        }
        EditorGUILayout.BeginVertical();
        EditorGUILayout.LabelField(enemyData.enemyName, EditorStyles.boldLabel);
        EditorGUILayout.LabelField($"HP: {enemyData.maxHealth} | 伤害: {enemyData.damage}");
        EditorGUILayout.EndVertical();
        EditorGUILayout.EndHorizontal();

        EditorGUILayout.Space();
        DrawDefaultInspector();
    }
}
```

## 与Babysitter SDK集成

### 任务定义示例

```javascript
const unityScriptTask = defineTask({
  name: 'unity-script-generation',
  description: '生成Unity C#脚本',

  inputs: {
    scriptType: { type: 'string', required: true }, // MonoBehaviour, ScriptableObject, Editor
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
      title: `生成Unity脚本: ${inputs.className}`,
      skill: {
        name: 'unity-development',
        context: {
          operation: 'generate_script',
          scriptType: inputs.scriptType,
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

### 可用MCP工具（通过unity-mcp）

| 工具 | 描述 |
|------|-------------|
| `unity_create_gameobject` | 在场景中创建新游戏对象 |
| `unity_modify_component` | 在游戏对象上添加/修改组件 |
| `unity_create_script` | 生成并附加C#脚本 |
| `unity_build` | 触发Unity构建 |
| `unity_run_tests` | 执行Unity测试框架测试 |
| `unity_import_asset` | 导入和配置资产 |
| `unity_scene_hierarchy` | 查询场景结构 |
| `unity_project_settings` | 读取/修改项目设置 |

### 配置

```json
{
  "mcpServers": {
    "unity": {
      "command": "uvx",
      "args": ["unity-mcp"],
      "env": {
        "UNITY_PROJECT_PATH": "C:/Projects/MyGame",
        "UNITY_VERSION": "2022.3.20f1"
      }
    }
  }
}
```

## 最佳实践

1. **程序集定义**：使用.asmdef文件组织代码以加快编译速度
2. **序列化**：使用[SerializeField]在检查器中公开字段，同时保持字段私有
3. **空值检查**：始终在Awake/Start中验证组件引用
4. **对象池**：避免频繁生成对象的运行时实例化
5. **协程**：用于基于时间的操作，避免重逻辑
6. **事件**：使用UnityEvent或C#事件进行解耦通信

## 平台考虑

| 平台 | 关键考虑因素 |
|----------|-------------------|
| PC/Mac | 内存限制较少，完整着色器支持 |
| 移动端 | 纹理压缩、绘制调用批处理、热限制 |
| 主机 | 认证要求、内存预算、TCR合规性 |
| WebGL | 无线程、内存有限、着色器限制 |

## 参考资料

- [Unity文档](https://docs.unity3d.com/)
- [Unity MCP (CoplayDev)](https://github.com/CoplayDev/unity-mcp)
- [Unity-MCP (IvanMurzak)](https://github.com/IvanMurzak/Unity-MCP)
- [mcp-unity (CoderGamester)](https://github.com/CoderGamester/mcp-unity)
- [Unity学习](https://learn.unity.com/)
- [Unity最佳实践](https://unity.com/how-to)
