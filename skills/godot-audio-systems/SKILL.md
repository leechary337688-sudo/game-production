---
名称: godot-audio-systems
描述: "Godot音频的专家模式，包括AudioStreamPlayer变体（2D位置、3D空间）、AudioBus混音架构、动态效果（混响、均衡器、压缩）、音频池化以提高性能、音乐过渡（交叉淡入淡出、BPM同步）以及程序化音频生成。用于音乐系统、音效、空间音频或音频反应式游戏玩法。触发关键词：AudioStreamPlayer、AudioStreamPlayer2D、AudioStreamPlayer3D、AudioBus、AudioServer、AudioEffect、music_crossfade、audio_pool、positional_audio、reverb、bus_volume。"
---

# 音频系统

Godot音频引擎和混音架构的专家指导。

## 绝不做的事

- **绝不為每个声音创建新的AudioStreamPlayer节点** — 导致内存膨胀和垃圾收集峰值。使用音频池化（复用播放器）或一次性辅助函数。
- **绝不使用线性值设置AudioServer总线音量** — `set_bus_volume_db()` 期望分贝值（-80 到 0）。使用 `linear_to_db()` 进行 0.0-1.0 转换。
- **绝不忘在音乐播放器上设置 `autoplay = false`** — 音乐默认在场景加载时自动播放。在切换场景时会导致音轨重叠。
- **绝不在没有衰减模型的情况下使用AudioStreamPlayer3D** — 默认衰减为无（无衰减）。设置 `attenuation_model` 为 ATTENUATION_INVERSE_DISTANCE，否则音频是全局的。
- **绝不播放AudioStreamPlayer而不先检查 `playing`** — 重新播放正在播放的声音会切断它。在播放前检查 `if not player.playing:`。

---

## 可用脚本

> **强制**：在实现相应模式之前阅读适当的脚本。

### [audio_manager.gd](scripts/audio_manager.gd)
AudioManager单例，带有声音池化（32个播放器池）、总线分配和交叉淡入淡出准备。防止节点泛滥和垃圾收集峰值。

### [audio_visualizer.gd](scripts/audio_visualizer.gd)
实时FFT频谱分析。捕获低/中/高频范围，以驱动视觉效果如灯光脉冲或着色器参数。

---

## AudioStreamPlayer变体

### AudioStreamPlayer（全局/UI）

```gdscript
# 无空间定位，音量处处相同
# 用于：音乐、UI声音、旁白

@onready var music := AudioStreamPlayer.new()

func _ready() -> void:
    music.stream = load("res://audio/music_main.ogg")
    music.volume_db = -10  # 更安静
    music.autoplay = false
    music.bus = "Music"  # 路由到音乐总线
    add_child(music)
    music.play()
```

### AudioStreamPlayer2D（位置音频）

```gdscript
# 基于与摄像头的距离进行2D声像控制
# 用于：2D游戏、俯视角音频提示

extends Area2D

@onready var footstep := AudioStreamPlayer2D.new()

func _ready() -> void:
    footstep.stream = load("res://audio/footstep.ogg")
    footstep.max_distance = 500  # 可听范围（像素）
    footstep.attenuation = 2.0  # 衰减曲线（越高 = 衰减越快）
    add_child(footstep)

func play_footstep() -> void:
    if not footstep.playing:
        footstep.play()
```

### AudioStreamPlayer3D（空间音频）

```gdscript
# 3D空间音频，带多普勒效应、混响发送
# 用于：3D游戏、逼真声音定位

extends Node3D

@onready var explosion := AudioStreamPlayer3D.new()

func _ready() -> void:
    explosion.stream = load("res://audio/explosion.ogg")
    explosion.unit_size = 10.0  # 声源大小
    explosion.max_distance = 100.0  # 范围
    explosion.attenuation_model = AudioStreamPlayer3D.ATTENUATION_INVERSE_DISTANCE
    explosion.doppler_tracking = AudioStreamPlayer3D.DOPPLER_TRACKING_PHYSICS_STEP
    add_child(explosion)
    
    explosion.play()
```

---

## AudioBus架构

### 总线设置（项目设置）

```
Master（始终存在）
  ├─ Music
  │   └─ 效果：压缩器、均衡器
  ├─ SFX
  │   └─ 效果：混响（用于环境）
  └─ Ambient
      └─ 效果：低通滤波器（模糊环境音）
```

### 音量控制（分贝）

```gdscript
# ❌ 错误：线性音量（不起作用）
AudioServer.set_bus_volume_db(music_bus_idx, 0.5)  # 错误！

# ✅ 正确：使用分贝
var music_bus := AudioServer.get_bus_index("Music")
AudioServer.set_bus_volume_db(music_bus, -10)  # -10 分贝（更安静）

# 转换线性（0.0-1.0）到分贝：
var linear_volume := 0.5  # 50%
var db := linear_to_db(linear_volume)  # 约 -6 分贝
AudioServer.set_bus_volume_db(music_bus, db)

# 转换分贝到线性：
var current_db := AudioServer.get_bus_volume_db(music_bus)
var linear := db_to_linear(current_db)
print("当前音量：%d%%" % int(linear * 100))
```

### 静音总线

```gdscript
func toggle_mute(bus_name: String) -> void:
    var bus_idx := AudioServer.get_bus_index(bus_name)
    var is_muted := AudioServer.is_bus_mute(bus_idx)
    AudioServer.set_bus_mute(bus_idx, not is_muted)
```

---

## 音频池化（性能优化）

### 问题：每帧创建播放器

```gdscript
# ❌ 错误：在60 FPS时每秒创建60个新节点
func play_footstep() -> void:
    var player := AudioStreamPlayer.new()
    add_child(player)
    player.stream = load("res://audio/footstep.ogg")
    player.finished.connect(player.queue_free)
    player.play()
    # 结果：1分钟内创建3600个节点！
```

### 解决方案：音频池

```gdscript
# audio_pool.gd（自动加载）
extends Node

const POOL_SIZE = 10
var pool: Array[AudioStreamPlayer] = []
var pool_index := 0

func _ready() -> void:
    # 预先创建播放器
    for i in range(POOL_SIZE):
        var player := AudioStreamPlayer.new()
        player.bus = "SFX"
        add_child(player)
        pool.append(player)

func play_sound(stream: AudioStream, volume_db := 0.0) -> void:
    var player := pool[pool_index]
    pool_index = (pool_index + 1) % POOL_SIZE  # 轮询
    
    # 如果仍在播放，停止先前的声音
    if player.playing:
        player.stop()
    
    player.stream = stream
    player.volume_db = volume_db
    player.play()

# 用法：
AudioPool.play_sound(load("res://audio/coin.ogg"), -5.0)
```

---

## 音乐过渡

### 音轨间交叉淡入淡出

```gdscript
# music_manager.gd（自动加载）
extends Node

@onready var track_a := AudioStreamPlayer.new()
@onready var track_b := AudioStreamPlayer.new()

var current_track: AudioStreamPlayer
var fade_duration := 2.0

func _ready() -> void:
    track_a.bus = "Music"
    track_b.bus = "Music"
    add_child(track_a)
    add_child(track_b)
    current_track = track_a

func crossfade_to(new_stream: AudioStream) -> void:
    var next_track := track_b if current_track == track_a else track_a
    
    # 从0分贝开始新音轨
    next_track.stream = new_stream
    next_track.volume_db = -80  # 静音
    next_track.play()
    
    # 淡出当前，淡入下一个
    var tween := create_tween().set_parallel(true)
    tween.tween_property(current_track, "volume_db", -80, fade_duration)
    tween.tween_property(next_track, "volume_db", 0, fade_duration)
    
    await tween.finished
    
    # 停止旧音轨
    current_track.stop()
    current_track = next_track
```

### BPM同步过渡

```gdscript
# 在节拍边界过渡
var bpm := 120.0  # 每分钟节拍数
var beat_duration := 60.0 / bpm  # 每个节拍0.5秒

func queue_transition_on_beat(new_stream: AudioStream) -> void:
    # 等待下一个节拍
    var current_time := current_track.get_playback_position()
    var time_to_next_beat := beat_duration - fmod(current_time, beat_duration)
    
    await get_tree().create_timer(time_to_next_beat).timeout
    crossfade_to(new_stream)
```

---

## 动态音频效果

### 运行时添加效果

```gdscript
# 向SFX总线添加混响
var sfx_bus := AudioServer.get_bus_index("SFX")
var reverb := AudioEffectReverb.new()
reverb.room_size = 0.8  # 大房间
reverb.damping = 0.5
reverb.wet = 0.3  # 30%效果，70%原始音
AudioServer.add_bus_effect(sfx_bus, reverb)
```

### 水下效果

```gdscript
func set_underwater(enabled: bool) -> void:
    var sfx_bus := AudioServer.get_bus_index("SFX")
    
    if enabled:
        # 添加低通滤波器（模糊声音）
        var lowpass := AudioEffectLowPassFilter.new()
        lowpass.cutoff_hz = 500  # 切掉500 Hz以上的频率
        AudioServer.add_bus_effect(sfx_bus, lowpass)
    else:
        # 移除所有效果
        for i in range(AudioServer.get_bus_effect_count(sfx_bus)):
            AudioServer.remove_bus_effect(sfx_bus, 0)
```

---

## 程序化音频

### 合成蜂鸣声

```gdscript
# 生成简单正弦波
func create_beep(frequency: float, duration: float) -> AudioStreamGenerator:
    var stream := AudioStreamGenerator.new()
    stream.mix_rate = 44100  # 采样率
    
    var playback := stream.instantiate_playback()
    
    var increment := frequency / stream.mix_rate
    var phase := 0.0
    
    for i in range(int(stream.mix_rate * duration)):
        var sample := sin(phase * TAU)
        playback.push_frame(Vector2(sample, sample))  # 立体声
        phase += increment
        phase = fmod(phase, 1.0)
    
    return stream

# 用法：
var beep_stream := create_beep(440.0, 0.1)  # 440 Hz（A4），0.1秒
$AudioStreamPlayer.stream = beep_stream
$AudioStreamPlayer.play()
```

---

## 高级模式

### 音频闪避（对话时降低音乐）

```gdscript
# auto_duck.gd（在对话AudioStreamPlayer上）
extends AudioStreamPlayer

func _ready() -> void:
    playing.connect(_on_playing)
    finished.connect(_on_finished)

func _on_playing() -> void:
    # 闪避音乐到 -15 分贝
    var music_bus := AudioServer.get_bus_index("Music")
    var tween := create_tween()
    tween.tween_method(set_music_volume, 0.0, -15.0, 0.5)

func _on_finished() -> void:
    # 恢复音乐到 0 分贝
    var tween := create_tween()
    tween.tween_method(set_music_volume, -15.0, 0.0, 0.5)

func set_music_volume(db: float) -> void:
    var music_bus := AudioServer.get_bus_index("Music")
    AudioServer.set_bus_volume_db(music_bus, db)
```

### 随机化音高以增加变化

```gdscript
# 防止相同声音（脚步声、枪声）
func play_varied_sound(stream: AudioStream) -> void:
    $AudioStreamPlayer.stream = stream
    $AudioStreamPlayer.pitch_scale = randf_range(0.9, 1.1)  # ±10% 音高
    $AudioStreamPlayer.play()
```

### 分层音乐（自适应）

```gdscript
# 基于强度的音乐层（从安静开始，随着强度增加添加层）
# 示例：和平探索 → 战斗

@onready var layer_drums := $Music/Drums
@onready var layer_bass := $Music/Bass
@onready var layer_melody := $Music/Melody

var intensity := 0.0  # 0.0 = 平静，1.0 = 激烈

func _ready() -> void:
    # 同步启动所有层
    layer_drums.play()
    layer_bass.play()
    layer_melody.play()
    
    # 静音高强度层
    layer_bass.volume_db = -80
    layer_melody.volume_db = -80

func set_music_intensity(new_intensity: float) -> void:
    intensity = clamp(new_intensity, 0.0, 1.0)
    
    # 基于强度淡入层
    var tween := create_tween().set_parallel(true)
    
    # 层1（鼓）：始终可听
    tween.tween_property(layer_drums, "volume_db", 0, 1.0)
    
    # 层2（贝斯）：在33%强度时淡入
    var bass_db := -80 if intensity < 0.33 else lerp(-80.0, 0.0, (intensity - 0.33) / 0.67)
    tween.tween_property(layer_bass, "volume_db", bass_db, 1.0)
    
    # 层3（旋律）：在66%强度时淡入
    var melody_db := -80 if intensity < 0.66 else lerp(-80.0, 0.0, (intensity - 0.66) / 0.34)
    tween.tween_property(layer_melody, "volume_db", melody_db, 1.0)

# 用法（战斗系统）：
func _on_enemy_spotted() -> void:
    MusicManager.set_music_intensity(1.0)  # 全强度

func _on_all_enemies_defeated() -> void:
    MusicManager.set_music_intensity(0.0)  # 回到平静
```

---

## 性能优化

### 禁用远距离音频

```gdscript
# 不播放玩家听不到的声音
extends AudioStreamPlayer3D

func _process(delta: float) -> void:
    var listener := get_viewport().get_camera_3d()
    if not listener:
        return
    
    var distance := global_position.distance_to(listener.global_position)
    
    if distance > max_distance * 1.5:  # 1.5倍最大范围
        if playing:
            stop()
```

---

## 边缘情况

### 音频不播放

```gdscript
# 检查：
# 1. 流是否已分配？
if not $AudioStreamPlayer.stream:
    push_error("未分配音频流！")

# 2. 总线是否静音？
var bus_idx := AudioServer.get_bus_index($AudioStreamPlayer.bus)
if AudioServer.is_bus_mute(bus_idx):
    print("总线已静音！")

# 3. 音量是否太低？
if $AudioStreamPlayer.volume_db < -60:
    print("音量太安静（< -60 分贝）")
```

---

## 决策矩阵：选择哪个AudioStreamPlayer？

| 特性 | AudioStreamPlayer | AudioStreamPlayer2D | AudioStreamPlayer3D |
|---------|------------------|---------------------|---------------------|
| **空间性** | ❌ 全局 | ✅ 2D声像控制 | ✅ 3D定位 |
| **多普勒效应** | ❌ | ❌ | ✅ |
| **衰减** | ❌ | ✅ 基于距离 | ✅ 3D衰减 |
| **混响发送** | ❌ | ❌ | ✅ |
| **用于** | 音乐、UI | 2D游戏 | 3D游戏 |
| **性能** | 最快 | 中等 | 最慢 |


## 参考
- 掌握技能：[godot-master](../godot-master/SKILL.md)
