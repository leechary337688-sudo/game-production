---
name: 游戏UI状态管理
description: 游戏界面模式 - 健康条、经验条、法力条。在构建RPG/复古游戏UI组件时应用，具有状态驱动的视觉效果。
---

## 游戏UI状态管理

创建具有状态驱动的视觉效果的类似游戏界面，用于健康、经验、法力和其他游戏指标。

### 进度条模式

基于Progress组件构建游戏特定变体：

```tsx
import { Progress } from "@/components/ui/8bit/progress";

function HealthBar({ value = 100, ...props }: BitProgressProps) {
  return (
    <Progress
      {...props}
      value={value}
      variant="retro"
      progressBg="bg-red-500"
    />
  );
}

function ManaBar({ value = 100, ...props }: BitProgressProps) {
  return (
    <Progress
      {...props}
      value={value}
      variant="retro"
      progressBg="bg-blue-500"
    />
  );
}

function XpBar({ value = 0, ...props }: BitProgressProps) {
  return (
    <Progress
      {...props}
      value={value}
      variant="retro"
      progressBg="bg-yellow-500"
    />
  );
}
```

### 升级通知

当达到阈值时显示动画消息：

```tsx
function XpBar({
  value,
  levelUpMessage = "LEVEL UP!",
  ...props
}: XpBarProps) {
  const isLevelUp = value === 100;

  return (
    <div className="relative">
      <Progress
        {...props}
        value={value}
        progressBg="bg-yellow-500"
        className={cn(isLevelUp && "animate-pulse")}
      />

      {isLevelUp && (
        <div
          className={cn(
            "retro",
            "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2",
            "text-[0.625rem] text-black",
            "pointer-events-none whitespace-nowrap z-10",
            "drop-shadow-[1px_1px_0_#fff] [text-shadow:1px_1px_0_#fff,-1px_-1px_0_#fff,1px_-1px_0_#fff,-1px_1px_0_#fff]",
            "animate-[blink_0.5s_step-end_infinite]"
          )}
        >
          {levelUpMessage}
        </div>
      )}
    </div>
  );
}
```

### 条件动画

使用条件类进行游戏状态反馈：

```tsx
<div
  className={cn(
    "transition-colors duration-300",
    health <= 25 ? "animate-pulse bg-red-500/20" : "bg-green-500",
    health > 25 && health <= 50 && "bg-yellow-500/20"
  )}
/>
```

### 敌人健康显示

战斗场景的紧凑显示：

```tsx
function EnemyHealth({ health, maxHealth }: EnemyHealthProps) {
  const percentage = (health / maxHealth) * 100;

  return (
    <div className="retro text-xs">
      <div className="flex justify-between mb-1">
        <span>ENEMY</span>
        <span>{health}/{maxHealth}</span>
      </div>
      <HealthBar value={percentage} className="h-2" />
    </div>
  );
}
```

### 关键原则

1. **基础组件** - 扩展Progress，不要重新实现
2. **颜色编码** - 红色（健康）、蓝色（法力）、黄色（经验）、绿色（耐力）
3. **复古文本** - 使用`.retro`类用于像素字体数字
4. **状态动画** - 使用`animate-pulse`、`animate-blink`进行反馈
5. **文本阴影** - 白色文本阴影以提高彩色背景上的可读性
6. **紧凑尺寸** - 游戏UI使用较小文本（text-xs, text-[0.625rem]）

### 参考组件

- `components/ui/8bit/health-bar.tsx` - 健康条实现
- `components/ui/8bit/xp-bar.tsx` - 经验条带有升级通知
- `components/ui/8bit/mana-bar.tsx` - 法力条实现
