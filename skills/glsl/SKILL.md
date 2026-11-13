---
名称: glsl
描述: 用于JARVIS全息效果的GLSL着色器编程
模型: sonnet
风险级别: 低
版本: 1.1.0
---

# GLSL着色器编程技能

> **文件组织**：此技能使用拆分结构。有关高级着色器模式，请参阅 `references/`。

## 1. 概述

此技能提供GLSL着色器专业知识，用于在JARVIS AI助手HUD中创建全息视觉效果。它专注于实时渲染的高效GPU编程。

**风险级别**：低 - GPU端代码攻击面有限，但可能导致性能问题

**主要用例**：
- 带扫描线的全息面板效果
- 动画能量场和粒子系统
- 自定义渲染的数据可视化
- 后处理效果（辉光、故障、色差）

## 2. 核心职责

### 2.1 基本原则

1. **测试驱动开发优先**：在实现前编写视觉回归测试和着色器单元测试
2. **性能意识**：分析GPU性能，针对60 FPS目标进行优化
3. **精度重要**：为性能使用适当的精度限定符
4. **避免分支**：最小化着色器中的条件判断以提高GPU效率
5. **优化数学运算**：使用内置函数，避免昂贵操作
6. **统一变量安全**：在发送到GPU前验证统一变量输入
7. **循环边界**：始终使用常量循环边界以防止GPU挂起
8. **内存访问**：优化纹理查找和变量插值

## 3. 实施工作流程（测试驱动开发）

### 3.1 步骤1：先编写失败测试

```typescript
// tests/shaders/holographic-panel.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { WebGLTestContext, captureFramebuffer, compareImages } from '../utils/webgl-test'

describe('HolographicPanelShader', () => {
  let ctx: WebGLTestContext

  beforeEach(() => {
    ctx = new WebGLTestContext(256, 256)
  })

  // 单元测试：着色器编译
  it('should compile without errors', () => {
    const shader = ctx.compileShader(holoFragSource, ctx.gl.FRAGMENT_SHADER)
    expect(shader).not.toBeNull()
    expect(ctx.getShaderErrors()).toEqual([])
  })

  // 单元测试：统一变量可访问
  it('should have required uniforms', () => {
    const program = ctx.createProgram(vertSource, holoFragSource)
    expect(ctx.getUniformLocation(program, 'uTime')).not.toBeNull()
    expect(ctx.getUniformLocation(program, 'uColor')).not.toBeNull()
    expect(ctx.getUniformLocation(program, 'uOpacity')).not.toBeNull()
  })

  // 视觉回归测试
  it('should render scanlines correctly', async () => {
    ctx.renderShader(holoFragSource, { uTime: 0, uColor: [0, 0.5, 1], uOpacity: 1 })
    const result = captureFramebuffer(ctx)
    const baseline = await loadBaseline('holographic-scanlines.png')
    expect(compareImages(result, baseline, { threshold: 0.01 })).toBeLessThan(0.01)
  })

  // 边界情况测试
  it('should handle extreme UV values', () => {
    const testCases = [
      { uv: [0, 0], expected: 'no crash' },
      { uv: [1, 1], expected: 'no crash' },
      { uv: [0.5, 0.5], expected: 'no crash' }
    ]
    testCases.forEach(({ uv }) => {
      expect(() => ctx.renderAtUV(holoFragSource, uv)).not.toThrow()
    })
  })
})
```

### 3.2 步骤2：实施最小通过代码

```glsl
// 从通过测试的最小着色器开始
#version 300 es
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform float uOpacity;

in vec2 vUv;
out vec4 fragColor;

void main() {
  // 通过编译测试的最小实现
  fragColor = vec4(uColor, uOpacity);
}
```

### 3.3 步骤3：重构为完整实现

```glsl
// 测试通过后扩展为完整实现
void main() {
  vec2 uv = vUv;
  float scanline = sin(uv.y * 100.0) * 0.1 + 0.9;
  float pulse = sin(uTime * 2.0) * 0.1 + 0.9;
  vec3 color = uColor * scanline * pulse;
  fragColor = vec4(color, uOpacity);
}
```

### 3.4 步骤4：运行完整验证

```bash
# 运行所有着色器测试
npm run test:shaders

# 视觉回归测试
npm run test:visual -- --update-snapshots  # 仅首次运行
npm run test:visual

# 性能基准测试
npm run bench:shaders

# 跨浏览器编译检查
npm run test:webgl-compat
```

## 4. 技术栈与版本

### 4.1 GLSL版本

| 版本 | 上下文 | 特性 |
|---------|---------|----------|
| GLSL ES 3.00 | WebGL 2.0 | 现代特性，更好精度 |
| GLSL ES 1.00 | WebGL 1.0 | 遗留支持 |

### 4.2 着色器设置

```glsl
#version 300 es
precision highp float;
precision highp int;

// WebGL 2.0着色器头部
```

## 5. 性能模式

### 5.1 避免分支 - 使用Mix/Step

```glsl
// ❌ 错误 - GPU分支分歧
vec3 getColor(float value) {
  if (value < 0.3) {
    return vec3(1.0, 0.0, 0.0);  // 红色
  } else if (value < 0.7) {
    return vec3(1.0, 1.0, 0.0);  // 黄色
  } else {
    return vec3(0.0, 1.0, 0.0);  // 绿色
  }
}

// ✅ 正确 - 使用mix/step无分支
vec3 getColor(float value) {
  vec3 red = vec3(1.0, 0.0, 0.0);
  vec3 yellow = vec3(1.0, 1.0, 0.0);
  vec3 green = vec3(0.0, 1.0, 0.0);

  vec3 color = mix(red, yellow, smoothstep(0.3, 0.31, value));
  color = mix(color, green, smoothstep(0.7, 0.71, value));
  return color;
}
```

### 5.2 纹理图集 - 减少绘制调用

```glsl
// ❌ 错误 - 多个纹理绑定
uniform sampler2D uIcon1;
uniform sampler2D uIcon2;
uniform sampler2D uIcon3;

vec4 getIcon(int id) {
  if (id == 0) return texture(uIcon1, vUv);
  if (id == 1) return texture(uIcon2, vUv);
  return texture(uIcon3, vUv);
}

// ✅ 正确 - 单个图集纹理
uniform sampler2D uIconAtlas;
uniform vec4 uAtlasOffsets[3];  // 每个图标的[x, y, 宽度, 高度]

vec4 getIcon(int id) {
  vec4 offset = uAtlasOffsets[id];
  vec2 atlasUV = offset.xy + vUv * offset.zw;
  return texture(uIconAtlas, atlasUV);
}
```

### 5.3 细节级别（LOD） - 基于距离的质量

```glsl
// ❌ 错误 - 无论距离相同质量
const int NOISE_OCTAVES = 8;

float noise(vec3 p) {
  float result = 0.0;
  for (int i = 0; i < NOISE_OCTAVES; i++) {
    result += snoise(p * pow(2.0, float(i)));
  }
  return result;
}

// ✅ 正确 - 基于距离减少八度
uniform float uCameraDistance;

float noise(vec3 p) {
  // 远离时更少八度（细节不可见）
  int octaves = int(mix(2.0, 8.0, 1.0 - smoothstep(10.0, 100.0, uCameraDistance)));
  float result = 0.0;
  for (int i = 0; i < 8; i++) {
    if (i >= octaves) break;
    result += snoise(p * pow(2.0, float(i)));
  }
  return result;
}
```

### 5.4 统一变量批处理 - 最小化CPU-GPU传输

```glsl
// ❌ 错误 - 许多单独的统一变量
uniform float uPosX;
uniform float uPosY;
uniform float uPosZ;
uniform float uRotX;
uniform float uRotY;
uniform float uRotZ;
uniform float uScaleX;
uniform float uScaleY;
uniform float uScaleZ;

// ✅ 正确 - 打包成向量/矩阵
uniform vec3 uPosition;
uniform vec3 uRotation;
uniform vec3 uScale;
// 或更好：
uniform mat4 uTransform;
```

### 5.5 精度优化 - 使用适当精度

```glsl
// ❌ 错误 - 所有高精度（浪费GPU周期）
precision highp float;

highp vec3 color;
highp float alpha;
highp vec2 uv;

// ✅ 正确 - 匹配数据需求的精度
precision highp float;  // 计算的默认

mediump vec3 color;     // 0-1范围，中精度足够
mediump float alpha;    // 0-1范围
highp vec2 uv;          // 需要纹理坐标精度
lowp int flags;         // 类布尔值
```

### 5.6 缓存纹理查找

```glsl
// ❌ 错误 - 冗余纹理提取
void main() {
  vec3 diffuse = texture(uTexture, vUv).rgb;
  // ... 一些代码 ...
  float alpha = texture(uTexture, vUv).a;  // 相同查找！
  // ... 更多代码 ...
  vec3 doubled = texture(uTexture, vUv).rgb * 2.0;  // 再次！
}

// ✅ 正确 - 缓存结果
void main() {
  vec4 texSample = texture(uTexture, vUv);
  vec3 diffuse = texSample.rgb;
  float alpha = texSample.a;
  vec3 doubled = texSample.rgb * 2.0;
}
```

## 6. 实施模式

### 6.1 全息面板着色器

```glsl
// shaders/holographic-panel.frag
#version 300 es
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform float uOpacity;
uniform vec2 uResolution;

in vec2 vUv;
out vec4 fragColor;

const int SCANLINE_COUNT = 50;

void main() {
  vec2 uv = vUv;

  // 扫描线效果
  float scanline = 0.0;
  for (int i = 0; i < SCANLINE_COUNT; i++) {
    float y = float(i) / float(SCANLINE_COUNT);
    scanline += smoothstep(0.0, 0.002, abs(uv.y - y));
  }
  scanline = 1.0 - scanline * 0.3;

  // 边缘辉光
  float edge = 1.0 - smoothstep(0.0, 0.05, min(
    min(uv.x, 1.0 - uv.x),
    min(uv.y, 1.0 - uv.y)
  ));

  // 动画脉冲
  float pulse = sin(uTime * 2.0) * 0.1 + 0.9;

  vec3 color = uColor * scanline * pulse;
  color += vec3(0.0, 0.5, 1.0) * edge * 0.5;

  fragColor = vec4(color, uOpacity);
}
```

### 6.2 能量场着色器

```glsl
// shaders/energy-field.frag
#version 300 es
precision highp float;

uniform float uTime;
uniform vec3 uColor;

in vec2 vUv;
in vec3 vNormal;
in vec3 vViewPosition;
out vec4 fragColor;

float snoise(vec3 v) {
  return fract(sin(dot(v, vec3(12.9898, 78.233, 45.543))) * 43758.5453);
}

void main() {
  vec3 viewDir = normalize(-vViewPosition);
  float fresnel = pow(1.0 - abs(dot(viewDir, vNormal)), 3.0);
  float noise = snoise(vec3(vUv * 5.0, uTime * 0.5));

  vec3 color = uColor * fresnel;
  color += uColor * noise * 0.2;
  float alpha = fresnel * 0.8 + noise * 0.1;

  fragColor = vec4(color, alpha);
}
```

### 6.3 数据可视化着色器

```glsl
// shaders/data-bar.frag
#version 300 es
precision highp float;

uniform float uValue;
uniform float uThreshold;
uniform vec3 uColorLow;
uniform vec3 uColorHigh;
uniform vec3 uColorWarning;

in vec2 vUv;
out vec4 fragColor;

void main() {
  float fill = step(vUv.x, uValue);
  vec3 color = mix(uColorLow, uColorHigh, uValue);
  color = mix(color, uColorWarning, step(uThreshold, uValue));
  float gradient = vUv.y * 0.3 + 0.7;
  fragColor = vec4(color * gradient * fill, fill);
}
```

## 7. 安全与性能标准

### 7.1 GPU安全

| 风险 | 缓解措施 |
|------|------------|
| 无限循环 | 始终使用常量循环边界 |
| GPU挂起 | 首先用小型数据集测试着色器 |
| 内存耗尽 | 限制纹理大小 |

### 7.2 循环安全模式

```glsl
// ❌ 错误 - 动态循环边界
for (int i = 0; i < int(uCount); i++) { }

// ✅ 正确 - 常量循环边界
const int MAX_ITERATIONS = 100;
for (int i = 0; i < MAX_ITERATIONS; i++) {
  if (i >= int(uCount)) break;
}
```

## 8. 常见错误与反模式

### 8.1 切勿：使用动态循环边界

```glsl
// ❌ 危险 - 可能导致GPU挂起
for (int i = 0; i < uniformValue; i++) { }

// ✅ 安全 - 常量边界带提前退出
const int MAX = 100;
for (int i = 0; i < MAX; i++) {
  if (i >= uniformValue) break;
}
```

### 8.2 切勿：除以零而不检查

```glsl
// ❌ 危险 - 除以零
float result = value / divisor;

// ✅ 安全 - 防止零除
float result = value / max(divisor, 0.0001);
```

## 9. 实施前检查清单

### 阶段1：编写代码前

- [ ] 编写着色器编译测试
- [ ] 编写统一变量可访问性测试
- [ ] 创建视觉回归测试基线图像
- [ ] 定义性能目标（FPS、绘制调用）
- [ ] 审查现有着色器以重用模式

### 阶段2：实施期间

- [ ] 所有循环有常量边界
- [ ] 无除以零可能
- [ ] 使用无分支模式（mix/step）
- [ ] 适当的精度限定符
- [ ] 纹理查找已缓存
- [ ] 统一变量批处理为向量/矩阵

### 阶段3：提交前

- [ ] 所有着色器测试通过：`npm run test:shaders`
- [ ] 视觉回归测试通过：`npm run test:visual`
- [ ] 性能基准测试符合目标：`npm run bench:shaders`
- [ ] 跨浏览器兼容性已验证
- [ ] 边界情况无伪影（UV 0,0 和 1,1）
- [ ] 平滑动画时间已验证

## 10. 总结

GLSL着色器为JARVIS HUD中的视觉效果提供动力：

1. **测试驱动开发优先**：先编写测试 - 编译、统一变量、视觉回归
2. **性能**：使用无分支模式、纹理图集、LOD、精度优化
3. **安全**：常量循环边界、防止除以零
4. **测试**：验证跨目标浏览器、基准测试GPU性能

**记住**：着色器在GPU上运行 - 单个坏着色器可能冻结整个系统。

---

**参考资料**：
- `references/advanced-patterns.md` - 复杂着色器技术
