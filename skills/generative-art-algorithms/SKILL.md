---
名称: 生成式艺术算法
描述: 使用数学模式、噪声函数、粒子系统和程序生成创建算法和生成式艺术。涵盖流场、L-系统、分形和创意编程基础。触发条件：生成式艺术、算法艺术、创意编程、程序生成或数学可视化请求。
许可证: MIT
---

# 生成式艺术算法

通过代码、数学和涌现创造艺术。

## 核心理念

### 生成式艺术原则

1. **规则创造涌现** - 简单规则产生复杂结果
2. **可控随机性** - 种子随机以实现可重复性
3. **参数探索** - 相同算法，无限变体
4. **意外之喜** - 错误作为特性

### 创意编码循环

```
想法 → 算法 → 参数 → 渲染 → 评估 → 迭代
   ↑                                                   │
   └───────────────────────────────────────────────────┘
```

---

## 噪声函数

### Perlin/Simplex 噪声

平滑、连续的随机值，完美用于有机运动。

```javascript
// p5.js 示例
function draw() {
  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      let n = noise(x * 0.01, y * 0.01, frameCount * 0.01);
      stroke(n * 255);
      point(x, y);
    }
  }
}
```

### 噪声参数

| 参数 | 效果 |
|-----------|--------|
| 比例 (频率) | 噪声的缩放级别（越小 = 更多细节） |
| 八度 | 细节层 |
| 振幅 | 值的高度 |
| 时间偏移 | 在噪声空间中动画 |

### 噪声应用

- 地形生成
- 纹理合成
- 有机运动
- 流场
- 云/烟雾效果

---

## 流场

### 基本流场

```javascript
// 从噪声生成每个网格点的角度
function setup() {
  createCanvas(800, 800);
  
  let resolution = 20;
  let cols = width / resolution;
  let rows = height / resolution;
  
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      let angle = noise(x * 0.1, y * 0.1) * TWO_PI * 2;
      
      // 绘制向量
      push();
      translate(x * resolution, y * resolution);
      rotate(angle);
      stroke(0);
      line(0, 0, resolution * 0.8, 0);
      pop();
    }
  }
}
```

### 流场中的粒子

```javascript
class Particle {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(0, 0);
    this.acc = createVector(0, 0);
    this.maxSpeed = 2;
    this.prevPos = this.pos.copy();
  }
  
  follow(flowField, resolution) {
    let x = floor(this.pos.x / resolution);
    let y = floor(this.pos.y / resolution);
    let index = x + y * floor(width / resolution);
    let force = flowField[index];
    this.applyForce(force);
  }
  
  applyForce(force) {
    this.acc.add(force);
  }
  
  update() {
    this.vel.add(this.acc);
    this.vel.limit(this.maxSpeed);
    this.prevPos = this.pos.copy();
    this.pos.add(this.vel);
    this.acc.mult(0);
  }
  
  edges() {
    if (this.pos.x > width) { this.pos.x = 0; this.prevPos.x = 0; }
    if (this.pos.x < 0) { this.pos.x = width; this.prevPos.x = width; }
    if (this.pos.y > width) { this.pos.y = 0; this.prevPos.y = 0; }
    if (this.pos.y < 0) { this.pos.y = height; this.prevPos.y = height; }
  }
  
  show() {
    stroke(0, 10);
    strokeWeight(1);
    line(this.pos.x, this.pos.y, this.prevPos.x, this.prevPos.y);
  }
}
```

---

## L-系统

### 语法结构

```
公理: 起始字符串
规则: 替换规则
角度: 转向角度
迭代: 递归深度
```

### 经典 L-系统

**分形树**:
```
公理: F
规则: F → FF+[+F-F-F]-[-F+F+F]
角度: 25°
```

**科赫雪花**:
```
公理: F
规则: F → F+F--F+F
角度: 60°
```

**谢尔宾斯基三角形**:
```
公理: F-G-G
规则: F → F-G+F+G-F, G → GG
角度: 120°
```

### L-系统渲染

```javascript
// 将字符串解释为绘图命令
function render(sentence) {
  for (let char of sentence) {
    switch(char) {
      case 'F':
        line(0, 0, 0, -len);
        translate(0, -len);
        break;
      case '+':
        rotate(angle);
        break;
      case '-':
        rotate(-angle);
        break;
      case '[':
        push();
        break;
      case ']':
        pop();
        break;
    }
  }
}
```

---

## 分形

### 曼德博集

```javascript
function mandelbrot(x, y, maxIter) {
  let real = x;
  let imag = y;
  
  for (let i = 0; i < maxIter; i++) {
    let tempReal = real * real - imag * imag + x;
    imag = 2 * real * imag + y;
    real = tempReal;
    
    if (real * real + imag * imag > 4) {
      return i;
    }
  }
  return maxIter;
}
```

### 朱利亚集

相同迭代，不同起始点：
```javascript
function julia(x, y, cx, cy, maxIter) {
  let real = x;
  let imag = y;
  
  for (let i = 0; i < maxIter; i++) {
    let tempReal = real * real - imag * imag + cx;
    imag = 2 * real * imag + cy;
    real = tempReal;
    
    if (real * real + imag * imag > 4) {
      return i;
    }
  }
  return maxIter;
}
```

### 递归细分

```javascript
function subdivide(x, y, w, h, depth) {
  if (depth === 0 || w < 2 || h < 2) {
    rect(x, y, w, h);
    return;
  }
  
  let splitH = random() > 0.5;
  
  if (splitH) {
    let split = random(0.3, 0.7) * w;
    subdivide(x, y, split, h, depth - 1);
    subdivide(x + split, y, w - split, h, depth - 1);
  } else {
    let split = random(0.3, 0.7) * h;
    subdivide(x, y, w, split, depth - 1);
    subdivide(x, y + split, w, h - split, depth - 1);
  }
}
```

---

## 粒子系统

### 基本粒子

```javascript
class Particle {
  constructor(x, y) {
    this.pos = createVector(x, y);
    this.vel = p5.Vector.random2D().mult(random(1, 3));
    this.acc = createVector(0, 0);
    this.lifespan = 255;
    this.size = random(5, 15);
  }
  
  applyForce(force) {
    this.acc.add(force);
  }
  
  update() {
    this.vel.add(this.acc);
    this.pos.add(this.vel);
    this.acc.mult(0);
    this.lifespan -= 2;
  }
  
  isDead() {
    return this.lifespan <= 0;
  }
  
  show() {
    noStroke();
    fill(255, this.lifespan);
    ellipse(this.pos.x, this.pos.y, this.size);
  }
}
```

### 力

```javascript
// 重力
let gravity = createVector(0, 0.1);
particle.applyForce(gravity);

// 吸引到点
function attract(target, particle, strength) {
  let force = p5.Vector.sub(target, particle.pos);
  let distance = constrain(force.mag(), 5, 25);
  force.normalize();
  let magnitude = strength / (distance * distance);
  force.mult(magnitude);
  return force;
}

// 排斥
function repel(target, particle, strength) {
  return attract(target, particle, -strength);
}
```

---

## 颜色算法

### 调色板生成

```javascript
// 互补色
function complementary(hue) {
  return [(hue + 180) % 360];
}

// 三色
function triadic(hue) {
  return [(hue + 120) % 360, (hue + 240) % 360];
}

// 类似色
function analogous(hue, spread = 30) {
  return [(hue - spread + 360) % 360, (hue + spread) % 360];
}

// 分割互补色
function splitComplementary(hue) {
  return [(hue + 150) % 360, (hue + 210) % 360];
}
```

### 颜色插值

```javascript
// 在颜色之间插值
function lerpColor(c1, c2, t) {
  colorMode(HSB);
  return color(
    lerp(hue(c1), hue(c2), t),
    lerp(saturation(c1), saturation(c2), t),
    lerp(brightness(c1), brightness(c2), t)
  );
}

// 从噪声生成调色板
function noiseColor(t, palette) {
  let n = noise(t) * (palette.length - 1);
  let i = floor(n);
  let f = n - i;
  return lerpColor(palette[i], palette[i + 1], f);
}
```

---

## 模式算法

### Truchet 瓷砖

```javascript
function truchetTile(x, y, size, type) {
  push();
  translate(x, y);
  
  if (type === 0) {
    arc(0, 0, size, size, 0, HALF_PI);
    arc(size, size, size, size, PI, PI + HALF_PI);
  } else {
    arc(size, 0, size, size, HALF_PI, PI);
    arc(0, size, size, size, PI + HALF_PI, TWO_PI);
  }
  
  pop();
}
```

### Voronoi

```javascript
// 通过距离检查实现简单 Voronoi
function voronoi(points) {
  for (let x = 0; x < width; x++) {
    for (let y = 0; y < height; y++) {
      let closest = 0;
      let minDist = Infinity;
      
      for (let i = 0; i < points.length; i++) {
        let d = dist(x, y, points[i].x, points[i].y);
        if (d < minDist) {
          minDist = d;
          closest = i;
        }
      }
      
      stroke(points[closest].color);
      point(x, y);
    }
  }
}
```

---

## 种子随机性

```javascript
// 使用种子实现可重复性
let seed = 12345;
randomSeed(seed);
noiseSeed(seed);

// 或从字符串生成
function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash = hash & hash;
  }
  return hash;
}

randomSeed(hashCode("我的艺术作品-2024"));
```

---

## 创意编码工具

| 工具 | 语言 | 最适合 |
|------|----------|----------|
| p5.js | JavaScript | 初学者，网络 |
| Processing | Java | 桌面，打印 |
| Three.js | JavaScript | 3D，WebGL |
| TouchDesigner | 视觉 | 实时，音频视频 |
| Hydra | JavaScript | 实时视觉 |
| Shadertoy | GLSL | GPU 着色器 |
| Nannou | Rust | 性能 |

---

---

## 相关技能

### 互补技能（一起使用）
- **[algorithmic-art](../algorithmic-art/)** - 创建交互式 p5.js 生成式艺术的完整工作流
- **[canvas-design](../canvas-design/)** - 用于自定义渲染的 Canvas API 模式
- **[theme-factory](../theme-factory/)** - 设计颜色调色板和视觉主题

### 替代技能（类似目的）
- **[three-js-interactive-builder](../three-js-interactive-builder/)** - 用于 Three.js 的 3D 生成式艺术

### 先修技能（先学习）
- 无需先修 - 包含基础创意编程模式

---

## 参考资料

- `references/noise-recipes.md` - 噪声函数模式
- `references/color-palettes.md` - 精选颜色方案
- `references/shader-patterns.md` - GLSL 代码片段
