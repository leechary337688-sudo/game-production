---
name: godot-shaders-basics
description: "着色器编程专家蓝图（视觉特效、后期处理、材质定制）使用Godot类似GLSL的着色器语言。覆盖canvas_item（2D）、spatial（3D）、uniforms、内置变量和性能。在实现自定义效果或风格化渲染时使用。关键词：着色器、GLSL、片段、顶点、canvas_item、spatial、uniform、UV、COLOR、ALBEDO、后期处理。"
---

# 着色器基础

片段/顶点着色器、uniforms和内置变量定义了自定义视觉特效。

## 可用脚本

### [vfx_port_shader.gdshader](scripts/vfx_port_shader.gdshader)
带有参数验证和常见效果模式的专家着色器模板。

### [shader_parameter_animator.gd](scripts/shader_parameter_animator.gd)
无需AnimationPlayer的运行时着色器uniform动画 - 用于动态效果。

## 着色器中绝对不要做的事

- **绝对不要在fragment()中使用昂贵操作** — 在每个像素上使用`pow()`、`sqrt()`、`sin()`？1920x1080 = 每帧2百万次调用 = 卡顿。预计算或使用纹理查找。
- **绝对不要忘记归一化向量** — 使用`reflect(direction, normal)`时不归一化？错误的反射 + 渲染伪影。总是归一化方向向量。
- **绝对不要使用if/else进行分支** — GPU讨厌分支（SIMD架构）。使用`mix()`、`step()`、`smoothstep()`进行条件逻辑。
- **绝对不要修改UV而不进行边界检查** — `UV.x += 10.0`超出0-1范围？纹理采样中断。使用`fract()`或`clamp()`。
- **绝对不要不使用delta的TIME** — `COLOR.a = sin(TIME)`在不同帧率下以可变速度运行。使用`TIME * speed_factor`实现一致的动画。
- **绝对不要忘记为颜色使用hint_source_color** — `uniform vec4 tint`没有提示？检查器显示原始浮点数。使用`uniform vec4 tint : source_color`用于颜色选择器。

---

```gdsl
shader_type canvas_item;

void fragment() {
    // 获取纹理颜色
    vec4 tex_color = texture(TEXTURE, UV);
    
    // 染红
    COLOR = tex_color * vec4(1.0, 0.5, 0.5, 1.0);
}
```

**应用到精灵：**
1. 选择Sprite2D节点
2. Material → New ShaderMaterial
3. Shader → New Shader
4. 粘贴代码

## 常见2D效果

### 溶解效果

```glsl
shader_type canvas_item;

uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform sampler2D noise_texture;

void fragment() {
    vec4 tex_color = texture(TEXTURE, UV);
    float noise = texture(noise_texture, UV).r;
    
    if (noise < dissolve_amount) {
        discard;  // 使像素透明
    }
    
    COLOR = tex_color;
}
```

### 波浪扭曲

```glsl
shader_type canvas_item;

uniform float wave_speed = 2.0;
uniform float wave_amount = 0.05;

void fragment() {
    vec2 uv = UV;
    uv.x += sin(uv.y * 10.0 + TIME * wave_speed) * wave_amount;
    
    COLOR = texture(TEXTURE, uv);
}
```

### 轮廓

```glsl
shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width = 2.0;

void fragment() {
    vec4 col = texture(TEXTURE, UV);
    vec2 pixel_size = TEXTURE_PIXEL_SIZE * outline_width;
    
    float alpha = col.a;
    alpha = max(alpha, texture(TEXTURE, UV + vec2(pixel_size.x, 0.0)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(-pixel_size.x, 0.0)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(0.0, pixel_size.y)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(0.0, -pixel_size.y)).a);
    
    COLOR = mix(outline_color, col, col.a);
    COLOR.a = alpha;
}
```

## 3D着色器

### 基本3D着色器

```glsl
shader_type spatial;

void fragment() {
    ALBEDO = vec3(1.0, 0.0, 0.0);  // 红色材质
}
```

### 卡通着色（Cel-Shading）

```glsl
shader_type spatial;

uniform vec3 base_color : source_color = vec3(1.0);
uniform int color_steps = 3;

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    float stepped = floor(NdotL * float(color_steps)) / float(color_steps);
    
    DIFFUSE_LIGHT = base_color * stepped;
}
```

## 屏幕空间效果

### 晕影

```glsl
shader_type canvas_item;

uniform float vignette_strength = 0.5;

void fragment() {
    vec4 color = texture(TEXTURE, UV);
    
    // 距离中心
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(UV, center);
    
    float vignette = 1.0 - dist * vignette_strength;
    
    COLOR = color * vignette;
}
```

## Uniforms（参数）

```glsl
// 浮点滑块
uniform float intensity : hint_range(0.0, 1.0) = 0.5;

// 颜色选择器
uniform vec4 tint_color : source_color = vec4(1.0);

// 纹理
uniform sampler2D noise_texture;

// 在代码中访问：
material.set_shader_parameter("intensity", 0.8)
```

## 内置变量

**2D（canvas_item）：**
- `UV` - 纹理坐标（0-1）
- `COLOR` - 输出颜色
- `TEXTURE` - 当前纹理
- `TIME` - 自开始的时间
- `SCREEN_UV` - 屏幕坐标

**3D（spatial）：**
- `ALBEDO` - 基色
- `NORMAL` - 表面法线
- `ROUGHNESS` - 表面粗糙度
- `METALLIC` - 金属值

## 最佳实践

### 1. 使用Uniforms进行调整

```glsl
// ✅ 好 - 可调整
uniform float speed = 1.0;

void fragment() {
    COLOR.r = sin(TIME * speed);
}

// ❌ 坏 - 硬编码
void fragment() {
    COLOR.r = sin(TIME * 2.5);
}
```

### 2. 优化性能

```glsl
// 避免在片段着色器中使用昂贵操作
// 尽可能预计算值
// 使用纹理进行复杂模式
```

### 3. 注释着色器

```glsl
// 水波效果
// 基于正弦波创建水平扭曲
uniform float wave_amplitude = 0.02;
```

## 参考
- [Godot文档：着色语言](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/shading_language.html)
- [Godot文档：你的第一个着色器](https://docs.godotengine.org/en/stable/tutorials/shaders/your_first_shader/your_first_2d_shader.html)


### 相关
- 大师技能：[godot-master](../godot-master/SKILL.md)
