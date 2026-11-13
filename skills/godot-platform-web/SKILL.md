---
名称：godot-platform-web
描述："为web/浏览器平台（HTML5导出）设计的专家蓝图，涵盖WebGL/WebGPU渲染、自定义加载屏幕、JavaScriptBridge集成、LocalStorage保存和大小优化。在导出到Web或实现浏览器特定功能时使用。关键词：web、HTML5、WebGL、WebGPU、JavaScriptBridge、localStorage、canvas、浏览器API。"
---

# 平台：Web

浏览器API集成、LocalStorage持久化和大小优化定义了Web部署。

## 可用脚本

### [web_bridge_sync.gd](scripts/web_bridge_sync.gd)
用于浏览器API集成（持久化、分析）的JavaScriptBridge助手专家。

## 在Web开发中绝不要做的事

- **绝不要使用FileAccess进行保存** — 在Web上使用`FileAccess.open("user://save.dat")`？浏览器沙盒会阻止文件系统。使用JavaScriptBridge + localStorage。
- **绝不要忘记加载屏幕** — 20MB的wasm下载搭配默认加载屏幕 = 用户关闭标签页。必须自定义index.html，添加进度条和品牌资源。
- **绝不要使用线程** — 在Web上使用`Thread.new()`？不支持。使用`await`进行异步操作，或通过`await get_tree().process_frame`将工作分散到多帧中。
- **绝不要忽略HTTPS要求** — 地理位置、麦克风、摄像头API要求HTTPS。本地`http://` = API被阻止。使用`localhost`或HTTPS。
- **绝不要超过50MB的构建大小** — 100MB的WebAssembly = 用户在加载期间愤怒退出。压缩纹理（ETC2/ASTC），排除未使用的资源。
- **绝不要硬编码窗口大小** — 在Web上使用`get_viewport().size = Vector2(1920, 1080)`？会破坏移动浏览器。使用`get_window().size_changed` + 响应式UI。

---

```html
<!-- index.html自定义加载 -->
<div id="loading-screen">
    <div class="progress-bar">
        <div id="progress" style="width: 0%"></div>
    </div>
    <p id="status-text">加载中...</p>
</div>

<script>
const engine = new Engine(CONFIG);
engine.startGame({
    onProgress: function(current, total) {
        const percent = Math.floor((current / total) * 100);
        document.getElementById('progress').style.width = percent + '%';
        document.getElementById('status-text').innerText = `加载 ${percent}%`;
    }
}).then(() => {
    document.getElementById('loading-screen').style.display = 'none';
});
</script>
```

## 浏览器集成

```gdscript
# 检查是否在浏览器中运行
if OS.has_feature("web"):
    # Web特定代码
    JavaScriptBridge.eval("console.log('在浏览器中运行')")
```

## LocalStorage保存

```gdscript
func save_to_browser() -> void:
    if not OS.has_feature("web"):
        return
    
    var data := JSON.stringify(get_save_data())
    JavaScriptBridge.eval("localStorage.setItem('savegame', '%s')" % data)

func load_from_browser() -> Dictionary:
    if not OS.has_feature("web"):
        return {}
    
    var data_str := JavaScriptBridge.eval("localStorage.getItem('savegame')")
    if data_str:
        return JSON.parse_string(data_str)
    return {}
```

## 大小优化

```ini
# 最小化构建大小
[渲染]
纹理/vram_compression/import_s3tc_bptc=false
纹理/vram_compression/import_etc2_astc=true

# 排除不必要的导出
[export_preset]
exclude_filter="*.md,*.txt,docs/*"
```

## 性能

- **目标60 FPS** 在中端浏览器上
- **限制godot-particles** - WebGL有较低限制
- **减少绘制调用**
- **避免大纹理**

## 最佳实践

1. **加载屏幕** - 用户期望反馈
2. **文件大小** - 保持低于50MB
3. **移动Web** - 在手机上测试
4. **HTTPS** - 许多API要求

## 参考
- 相关：`godot-export-builds`、`godot-platform-mobile`

### 相关
- 主技能：[godot-master](../godot-master/SKILL.md)
