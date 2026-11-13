---
name: godot-genre-rhythm
description: "节奏游戏的专家蓝图，包括音频同步（BPM指挥器、使用AudioServer.get_time_since_last_mix的延迟补偿）、音符高速公路（滚动速度、时间窗口）、判断系统（完美/优秀/好/差/错过）、带连击乘数的评分、输入处理（基于车道、长按音符检测）和图表/节拍图加载。基于DDR/osu!/Beat Saber研究。触发关键词：rhythm_game, audio_sync, timing_judgment, note_highway, combo_system, BPM_conductor, latency_compensation。"
---

# 类型：节奏

节奏游戏的专家蓝图，强调音频视觉同步和流程状态。

## 绝不能做

- **绝不能跳过延迟补偿** — 使用 `AudioServer.get_time_since_last_mix()` 同步视觉与音频。忽略此点会导致不同步。
- **绝不能使用 `_process` 进行输入** — 使用 `_input()` 以获得精确时间。依赖帧的输入会导致音符错过。
- **绝不能忘记偏移校准** — 音频硬件延迟各异（10-200毫秒）。提供玩家可调整的偏移设置。
- **绝不能对低难度设置严格时间窗口** — 完美：25毫秒，优秀：50毫秒适用于专家。初学者需要100-150毫秒窗口。
- **绝不能将输入与音频分离** — 输入时间必须引用 MusicConductor.song_position，而不是帧时间。帧率下降不应导致错过。
---

## 可用脚本

> **必须**：在实现相应模式前阅读适当脚本。

### [conductor_sync.gd](scripts/conductor_sync.gd)
带AudioServer延迟补偿的BPM指挥器。发出 beat_hit/measure_hit 信号以进行音频同步的游戏逻辑。

### [rhythm_chart_parser.gd](scripts/rhythm_chart_parser.gd)
带时间排序音符的JSON图表加载器。提供优化的 get_notes_in_range() 以在高速公路上高效查询音符。

---

## 核心循环

`音乐播放 → 音符出现 → 玩家输入 → 时间判断 → 评分/反馈 → 连击构建`

## 技能链

`godot-project-foundations`, `godot-input-handling`, `sound-manager`, `animation`, `ui-framework`

---

## 音频同步

**最关键方面** - 音符必须与音频完美对齐。

### 音乐时间系统

```gdscript
class_name MusicConductor
extends Node

signal beat(beat_number: int)
signal measure(measure_number: int)

@export var bpm := 120.0
@export var music: AudioStream

var seconds_per_beat: float
var song_position: float = 0.0  # 以秒为单位
var song_position_in_beats: float = 0.0
var last_reported_beat: int = 0

@onready var audio_player: AudioStreamPlayer

func _ready() -> void:
    seconds_per_beat = 60.0 / bpm
    audio_player.stream = music

func _process(_delta: float) -> void:
    # 使用延迟补偿获取精确音频位置
    song_position = audio_player.get_playback_position() + AudioServer.get_time_since_last_mix()
    
    # 转换为节拍
    song_position_in_beats = song_position / seconds_per_beat
    
    # 发出节拍信号
    var current_beat := int(song_position_in_beats)
    if current_beat > last_reported_beat:
        beat.emit(current_beat)
        if current_beat % 4 == 0:
            measure.emit(current_beat / 4)
        last_reported_beat = current_beat

func start_song() -> void:
    audio_player.play()
    song_position = 0.0
    last_reported_beat = 0

func beats_to_seconds(beats: float) -> float:
    return beats * seconds_per_beat

func seconds_to_beats(secs: float) -> float:
    return secs / seconds_per_beat
```

---

## 音符系统

### 音符数据结构

```gdscript
class_name NoteData
extends Resource

@export var beat_time: float  # 何时击中（以节拍为单位）
@export var lane: int  # 哪个输入车道（0-3对应4键，等）
@export var note_type: NoteType
@export var hold_duration: float = 0.0  # 用于长按音符（以节拍为单位）

enum NoteType { TAP, HOLD, SLIDE, FLICK }
```

### 图表/节拍图加载

```gdscript
class_name ChartLoader
extends Node

func load_chart(chart_path: String) -> Array[NoteData]:
    var notes: Array[NoteData] = []
    var file := FileAccess.open(chart_path, FileAccess.READ)
    
    while not file.eof_reached():
        var line := file.get_line()
        if line.is_empty() or line.begins_with("#"):
            continue
        
        var parts := line.split(",")
        var note := NoteData.new()
        note.beat_time = float(parts[0])
        note.lane = int(parts[1])
        note.note_type = NoteType.get(parts[2]) if parts.size() > 2 else NoteType.TAP
        note.hold_duration = float(parts[3]) if parts.size() > 3 else 0.0
        notes.append(note)
    
    notes.sort_custom(func(a, b): return a.beat_time < b.beat_time)
    return notes
```

---

## 音符高速公路/接收器

```gdscript
class_name NoteHighway
extends Control

@export var scroll_speed := 500.0  # 每秒像素
@export var hit_position_y := 100.0  # 从底部起
@export var note_scene: PackedScene
@export var look_ahead_beats := 4.0

var active_notes: Array[NoteVisual] = []
var chart: Array[NoteData]
var next_note_index: int = 0

func _process(_delta: float) -> void:
    spawn_upcoming_notes()
    update_note_positions()

func spawn_upcoming_notes() -> void:
    var look_ahead_time := MusicConductor.song_position_in_beats + look_ahead_beats
    
    while next_note_index < chart.size():
        var note_data := chart[next_note_index]
        if note_data.beat_time > look_ahead_time:
            break
        
        var note_visual := note_scene.instantiate() as NoteVisual
        note_visual.setup(note_data)
        note_visual.position.x = get_lane_x(note_data.lane)
        add_child(note_visual)
        active_notes.append(note_visual)
        next_note_index += 1

func update_note_positions() -> void:
    for note in active_notes:
        var beats_until_hit := note.data.beat_time - MusicConductor.song_position_in_beats
        var seconds_until_hit := MusicConductor.beats_to_seconds(beats_until_hit)
        
        # 音符从顶部向下滚动
        note.position.y = (size.y - hit_position_y) - (seconds_until_hit * scroll_speed)
        
        # 如果过远则移除
        if note.position.y > size.y + 100:
            if not note.was_hit:
                register_miss(note.data)
            note.queue_free()
            active_notes.erase(note)
```

---

## 时间判断

```gdscript
class_name JudgmentSystem
extends Node

signal note_judged(judgment: Judgment, note: NoteData)

enum Judgment { PERFECT, GREAT, GOOD, BAD, MISS }

# 时间窗口以毫秒为单位（围绕击中时间对称）
const WINDOWS := {
    Judgment.PERFECT: 25.0,
    Judgment.GREAT: 50.0,
    Judgment.GOOD: 100.0,
    Judgment.BAD: 150.0
}

func judge_input(input_time: float, note_time: float) -> Judgment:
    var difference := abs(input_time - note_time) * 1000.0  # 毫秒
    
    if difference <= WINDOWS[Judgment.PERFECT]:
        return Judgment.PERFECT
    elif difference <= WINDOWS[Judgment.GREAT]:
        return Judgment.GREAT
    elif difference <= WINDOWS[Judgment.GOOD]:
        return Judgment.GOOD
    elif difference <= WINDOWS[Judgment.BAD]:
        return Judgment.BAD
    else:
        return Judgment.MISS

func get_timing_offset(input_time: float, note_time: float) -> float:
    # 正数 = 晚，负数 = 早
    return (input_time - note_time) * 1000.0
```

---

## 评分系统

```gdscript
class_name RhythmScoring
extends Node

signal score_changed(new_score: int)
signal combo_changed(new_combo: int)
signal combo_broken

const JUDGMENT_SCORES := {
    Judgment.PERFECT: 100,
    Judgment.GREAT: 75,
    Judgment.GOOD: 50,
    Judgment.BAD: 25,
    Judgment.MISS: 0
}

const COMBO_MULTIPLIER_THRESHOLDS := {
    10: 1.5,
    25: 2.0,
    50: 2.5,
    100: 3.0
}

var score: int = 0
var combo: int = 0
var max_combo: int = 0

func register_judgment(judgment: Judgment) -> void:
    if judgment == Judgment.MISS:
        if combo > 0:
            combo_broken.emit()
        combo = 0
    else:
        combo += 1
        max_combo = max(max_combo, combo)
    
    var base_score := JUDGMENT_SCORES[judgment]
    var multiplier := get_combo_multiplier()
    var earned := int(base_score * multiplier)
    
    score += earned
    score_changed.emit(score)
    combo_changed.emit(combo)

func get_combo_multiplier() -> float:
    var mult := 1.0
    for threshold in COMBO_MULTIPLIER_THRESHOLDS:
        if combo >= threshold:
            mult = COMBO_MULTIPLIER_THRESHOLDS[threshold]
    return mult
```

---

## 输入处理

```gdscript
class_name RhythmInput
extends Node

@export var lane_actions: Array[StringName] = [
    &"lane_0", &"lane_1", &"lane_2", &"lane_3"
]

var held_notes: Dictionary = {}  # lane: NoteData 用于长按音符

func _input(event: InputEvent) -> void:
    for i in lane_actions.size():
        if event.is_action_pressed(lane_actions[i]):
            process_lane_press(i)
        elif event.is_action_released(lane_actions[i]):
            process_lane_release(i)

func process_lane_press(lane: int) -> void:
    var current_time := MusicConductor.song_position
    var closest_note := find_closest_note_in_lane(lane, current_time)
    
    if closest_note:
        var note_time := MusicConductor.beats_to_seconds(closest_note.beat_time)
        var judgment := JudgmentSystem.judge_input(current_time, note_time)
        
        if judgment != Judgment.MISS:
            hit_note(closest_note, judgment)
            if closest_note.note_type == NoteType.HOLD:
                held_notes[lane] = closest_note

func process_lane_release(lane: int) -> void:
    if held_notes.has(lane):
        var hold_note := held_notes[lane]
        var hold_end_time := hold_note.beat_time + hold_note.hold_duration
        var current_beat := MusicConductor.song_position_in_beats
        
        # 检查是否在正确时间释放
        if abs(current_beat - hold_end_time) < 0.25:  # 四分之一节拍容差
            complete_hold_note(hold_note)
        else:
            drop_hold_note(hold_note)
        
        held_notes.erase(lane)
```

---

## 视觉反馈

```gdscript
func show_judgment_splash(judgment: Judgment, position: Vector2) -> void:
    var splash := judgment_sprites[judgment].instantiate()
    splash.position = position
    add_child(splash)
    
    var tween := create_tween()
    tween.tween_property(splash, "scale", Vector2(1.2, 1.2), 0.1)
    tween.tween_property(splash, "scale", Vector2(1.0, 1.0), 0.1)
    tween.tween_property(splash, "modulate:a", 0.0, 0.3)
    tween.tween_callback(splash.queue_free)

func pulse_receptor(lane: int, judgment: Judgment) -> void:
    var receptor := lane_receptors[lane]
    receptor.modulate = judgment_colors[judgment]
    
    var tween := create_tween()
    tween.tween_property(receptor, "modulate", Color.WHITE, 0.15)
```

---

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 音频不同步 | 使用 `AudioServer.get_time_since_last_mix()` 延迟补偿 |
| 不公平判断 | 低难度下使用宽松窗口，偏移校准 |
| 音符视觉堆积 | 调整滚动速度或生成时间 |
| 长按音符不流畅 | 单独渲染长按主体和尾部 |
| 帧率下降导致错过 | 将输入与帧率解耦 |

---

## Godot特定提示

1. **音频延迟**：使用 `AudioServer` 和自定义偏移进行校准
2. **输入轮询**：使用 `_input` 而非 `_process` 以获得精确时间
3. **着色器**：使用UV滚动处理音符高速公路
4. **粒子**：使用 `GPUParticles2D` 处理击中效果


## 参考
- 主技能：[godot-master](../godot-master/SKILL.md)
