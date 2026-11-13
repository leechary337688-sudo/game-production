---
名称: 算法艺术生成
描述: |
  使用p5.js、随机种子、流场和粒子系统创建算法艺术。当需要生成生成艺术、探索计算美学或构建互动艺术可视化时使用。
  自动激活时讨论：“生成艺术”、“算法艺术”、“p5.js可视化”、“计算美学”。
---

# 算法艺术生成

## 何时使用此技能

使用此技能时：
- 用代码创建生成艺术
- 构建互动可视化
- 探索计算美学
- 生成独特的艺术模式
- 使用种子创建可复现的艺术
- 实现粒子系统
- 设计流场可视化

## 工作原理

此技能引导Claude通过结构化过程：

1. **哲学创建** - 生成计算美学运动
2. **算法设计** - 创建独特的生成艺术算法
3. **技术实现** - 使用p5.js构建自包含的HTML
4. **互动功能** - 添加种子导航和参数控制

## 核心概念

### 算法哲学
- 计算美学运动
- 涌现行为和数学美感
- 过程优于最终输出
- “活算法，非静态图像”

### 技术组件
- **p5.js框架** - JavaScript创意编码库
- **随机种子** - 可复现的随机生成
- **参数变化** - 互动参数控制
- **流场** - 基于矢量场的运动
- **粒子系统** - 动态粒子行为

## 快速入门

### 基本生成艺术

```javascript
// 随机种子生成器
let seed = 12345;
function seededRandom() {
  seed = (seed * 9301 + 49297) % 233280;
  return seed / 233280;
}

function setup() {
  createCanvas(800, 800);
  background(20);

  // 创建生成模式
  for (let i = 0; i < 1000; i++) {
    let x = seededRandom() * width;
    let y = seededRandom() * height;
    let size = seededRandom() * 50;

    fill(255, 100);
    noStroke();
    circle(x, y, size);
  }
}
```

### 互动模板

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
  <style>
    body { margin: 0; background: #1a1a1a; font-family: system-ui; }
    #controls { position: absolute; top: 20px; left: 20px; color: white; }
    button { padding: 10px; margin: 5px; cursor: pointer; }
  </style>
</head>
<body>
  <div id="controls">
    <button onclick="prevSeed()">← 上一个</button>
    <span id="seed-display">种子: 0</span>
    <button onclick="nextSeed()">下一个 →</button>
  </div>

  <script>
    let currentSeed = 0;

    function setup() {
      createCanvas(windowWidth, windowHeight);
      regenerate();
    }

    function draw() {
      // 动画循环（如需要）
    }

    function regenerate() {
      randomSeed(currentSeed);
      background(20);
      // 您的生成算法在此处
    }

    function prevSeed() {
      currentSeed--;
      document.getElementById('seed-display').innerText = `种子: ${currentSeed}`;
      regenerate();
    }

    function nextSeed() {
      currentSeed++;
      document.getElementById('seed-display').innerText = `种子: ${currentSeed}`;
      regenerate();
    }
  </script>
</body>
</html>
```

## 高级模式

### 流场可视化

```javascript
let particles = [];
let flowField;

function setup() {
  createCanvas(800, 800);

  // 创建粒子系统
  for (let i = 0; i < 500; i++) {
    particles.push(new Particle());
  }

  // 生成流场
  flowField = generateFlowField();
}

function generateFlowField() {
  let field = [];
  let resolution = 20;

  for (let x = 0; x < width; x += resolution) {
    let row = [];
    for (let y = 0; y < height; y += resolution) {
      let angle = noise(x * 0.01, y * 0.01) * TWO_PI * 2;
      row.push(p5.Vector.fromAngle(angle));
    }
    field.push(row);
  }

  return field;
}

class Particle {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = createVector(0, 0);
    this.acc = createVector(0, 0);
  }

  update() {
    // 跟随流场
    let x = floor(this.pos.x / 20);
    let y = floor(this.pos.y / 20);
    let force = flowField[x][y];

    this.acc.add(force);
    this.vel.add(this.acc);
    this.pos.add(this.vel);
    this.acc.mult(0);

    // 边缘环绕
    if (this.pos.x > width) this.pos.x = 0;
    if (this.pos.x < 0) this.pos.x = width;
    if (this.pos.y > height) this.pos.y = 0;
    if (this.pos.y < 0) this.pos.y = height;
  }

  show() {
    stroke(255, 50);
    point(this.pos.x, this.pos.y);
  }
}
```

## 指导原则

1. **过程中的美** - 关注算法，不仅是结果
2. **种子可复现性** - 每个艺术作品应可通过种子复现
3. **参数控制** - 允许用户探索变化
4. **涌现行为** - 让复杂从简单规则中涌现
5. **数学美感** - 将美学基于计算过程

## 最佳实践

### 代码组织
- 保持算法模块化和可重用
- 使用类处理复杂行为
- 分离设置、更新和渲染逻辑
- 文档记录数学概念

### 性能
- 优化粒子数量以实现流畅动画
- 对大量粒子使用对象池
- 批量类似绘图操作
- 分析并优化瓶颈

### 用户体验
- 提供清晰的控件和反馈
- 显示种子号码以供复现
- 添加参数滑块进行探索
- 包括重置和导出功能

### 美学考虑
- 平衡复杂性和清晰度
- 有效使用色彩理论
- 考虑构图和负空间
- 跨不同种子测试

## 常见模式

### 基于噪声的地形
```javascript
function drawTerrain() {
  for (let x = 0; x < width; x += 5) {
    for (let y = 0; y < height; y += 5) {
      let n = noise(x * 0.01, y * 0.01);
      fill(n * 255);
      rect(x, y, 5, 5);
    }
  }
}
```

### 递归模式
```javascript
function fractalTree(x, y, len, angle) {
  if (len < 2) return;

  let x2 = x + cos(angle) * len;
  let y2 = y + sin(angle) * len;

  line(x, y, x2, y2);

  fractalTree(x2, y2, len * 0.67, angle - PI/6);
  fractalTree(x2, y2, len * 0.67, angle + PI/6);
}
```

### 基于代理的系统
```javascript
class Agent {
  constructor() {
    this.pos = createVector(random(width), random(height));
    this.vel = p5.Vector.random2D();
  }

  interact(others) {
    // 集群行为
    let separation = this.separate(others);
    let alignment = this.align(others);
    let cohesion = this.cohere(others);

    this.acc.add(separation);
    this.acc.add(alignment);
    this.acc.add(cohesion);
  }
}
```

## 输出格式

创建算法艺术时，总是提供：

1. **宣言** (Markdown) - 4-6段描述算法哲学
2. **互动HTML** - 单一自包含文件，包含：
   - 种子导航（上一个/下一个按钮）
   - 关键变量参数滑块
   - Anthropic品牌UI元素
   - 完整p5.js实现
3. **使用说明** - 如何探索变化和导出

## 资源

### 库与工具
- [p5.js参考](https://p5js.org/reference/)
- [The Coding Train](https://thecodingtrain.com/) - 教程
- [Processing](https://processing.org/) - 桌面替代品

### 灵感
- [OpenProcessing](https://openprocessing.org/) - 社区画廊
- [Generative Artistry](https://generativeartistry.com/) - 教程
- [Tyler Hobbs](https://tylerxhobbs.com/) - 专业生成艺术家

### 理论
- “The Nature of Code” by Daniel Shiffman
- “Generative Design” by Benedikt Groß
- “Form+Code” by Casey Reas

## 示例互动

**用户:** “创建受海浪启发的生成艺术”

**技能激活:**
1. 生成关于“流体动力学美学”的宣言
2. 使用Perlin噪声流场创建算法
3. 实现模拟水运动的粒子系统
4. 构建互动HTML，包含：
   - 波浪幅度滑块
   - 流速控制
   - 种子导航
   - 海洋色彩调色板
5. 输出宣言 + 互动艺术品

## 笔记

- 总是包括种子以供复现
- 创建自包含HTML文件
- 强调算法，不仅是视觉
- 通过参数鼓励探索
- 平衡美学美感与计算优雅
