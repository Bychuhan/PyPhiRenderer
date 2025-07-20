from __future__ import annotations
from const import *
from func import *
from dxsound import *
import math
import random
import data

SPEED_EVENT_H: float = 0.6 * WINDOW_HEIGHT
NOTE_POS_X: float = 0.05625 * WINDOW_WIDTH

NOTE_SOUNDS: tuple[directSound] = (
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\tap.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\drag.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\tap.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\flick.wav"),
)

NOTE_TEXTURES: tuple[Texture] = (
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\tap.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\drag.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\hold.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\flick.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdhead.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdend.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\tapHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\dragHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\flickHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdheadHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdendHL.png"),
)

HIT_TEXTURES: tuple[Texture] = tuple(Texture.from_path(f"{RESOURCE_PATH}\\textures\\hits\\{i + 1}.png") for i in range(30))

NOTE_REMOVE_MAX: float = 2 * WINDOW_HEIGHT # 好吧我也不知道剔除的英文是什么 :(

_note_times: list[float] = []
_note_hl_times: list[float] = []

def to_real_time(tick: float, bpm: float) -> float:
    return 1.875 / bpm * tick

def linear(time: float, st: float, et: float, s: float, e: float) -> float:
    return s + (e - s) * ((time - st) / (et - st))

particle_easing = lambda x: 9 * x / (8.3 * x + 1)
particle_size_easing = lambda x: (((0.2078 * x - 1.6524) * x + 1.6399) * x + 0.4988)

def init_event(event: list[dict], bpm: float, evtype: int) -> None:
    for i in event:
        i["startTime"] = to_real_time(i["startTime"], bpm)
        i["endTime"] = to_real_time(i["endTime"], bpm)
        if evtype == 0:
            i["start"] *= WINDOW_WIDTH
            i["end"] *= WINDOW_WIDTH
            i["start2"] *= WINDOW_HEIGHT
            i["end2"] *= WINDOW_HEIGHT
        if evtype == 3:
            i["value"] *= SPEED_EVENT_H
            i["fp"] = i["value"] * (i["endTime"] - i["startTime"])
    if evtype == 3:
        for i in enumerate(event):
            if i[0] == 0:
                i[1]["lastFp"] = 0
            else:
                i[1]["lastFp"] = event[i[0]-1]["lastFp"] + event[i[0]-1]["fp"]
    event = [i for i in event if i["startTime"] != i["endTime"]]

def get_note_floor_position(time: float, speedevents: list[dict]) -> float:
    for i in speedevents:
        if time < i["endTime"]:
            return i["lastFp"] + (time - i["startTime"]) * i["value"]
    return 0.

def init_notes(notes: list[dict], bpm: float, speedevents: list[dict]) -> None:
    for i in notes:
        i["time"] = to_real_time(i["time"], bpm)
        i["holdTime"] = to_real_time(i["holdTime"], bpm)
        i["endTime"] = i["time"] + i["holdTime"]
        i["floorPosition"] = get_note_floor_position(i["time"], speedevents)
        i["positionX"] *= NOTE_POS_X
        i["isHL"] = False
        if i["time"] in _note_times and not i["time"] in _note_hl_times:
            _note_hl_times.append(i["time"])
        _note_times.append(i["time"])

class JudgeLine:
    def __init__(self, data: dict) -> None:
        self.bpm = data["bpm"]
        self.move_event: list[dict] = data["judgeLineMoveEvents"]
        self.rotate_event: list[dict] = data["judgeLineRotateEvents"]
        self.alpha_event: list[dict] = data["judgeLineDisappearEvents"]
        self.speed_event: list[dict] = data["speedEvents"]
        self.above_notes: list[dict] = data["notesAbove"]
        self.below_notes: list[dict] = data["notesBelow"]
        self.notes: list[dict] = []
        self.note_objs: list[list[Note]] = []
        self.hold_objs: list[Note] = []
        self.hits: list[Hit] = []
        self.x: float = WINDOW_WIDTH/2
        self.y: float = WINDOW_HEIGHT/2
        self.r: float = 0
        self.a: float = 0
        self.current_fp: float = 0
        self.preload()

    def sort_notes(self, notes: list[Note]) -> list[list[Note]]:
        __speeds: dict[float, list[Note]] = {}
        for i in notes:
            if not i.speed in __speeds:
                __speeds[i.speed] = []
            __speeds[i.speed].append(i)
        __temp_notes: list[list[Note]] = [__speeds[k] for k in __speeds]
        for notelist in __temp_notes:
            notelist.sort(key = lambda x: x.floor_position)
        return __temp_notes

    def preload(self) -> None:
        init_event(self.move_event, self.bpm, 0)
        init_event(self.rotate_event, self.bpm, 1)
        init_event(self.alpha_event, self.bpm, 2)
        init_event(self.speed_event, self.bpm, 3)
        [i.update({"above" : 1}) for i in self.above_notes]
        [i.update({"above" : -1}) for i in self.below_notes]
        self.notes = self.above_notes + self.below_notes
        init_notes(self.notes, self.bpm, self.speed_event)
        self.note_objs = [Note(i) for i in self.notes if i["type"] != 3]
        self.hold_objs = [Note(i) for i in self.notes if i["type"] == 3]
        self.note_objs = self.sort_notes(self.note_objs)
        self.hold_objs.sort(key = lambda x: x.floor_position)

    def load_note(self):pass # 此函数无用，等待rpe_objs重构后一并删除

    def load_note_hl(self):
        for speed in self.note_objs:
            for note in speed:
                if note.time in _note_hl_times:
                    note.is_hl = True
        for note in self.hold_objs:
            if note.time in _note_hl_times:
                note.is_hl = True
                note.yscale = HOLD_HL_YSCALE
                note.scale = HOLD_HL_SCALE

    def update_note(self, time: float):
        for speed in self.note_objs.copy():
            for note in speed.copy():
                if note.update(time, self.x, self.y, self.r, self.current_fp, self.bpm):
                    self.hits.append(Hit(note.x, note.y, note.time))
                    speed.remove(note)
                if note.now_fp * note.speed > NOTE_REMOVE_MAX:
                    break

    def update_hold(self, time: float):
        for note in self.hold_objs.copy():
            if note.update(time, self.x, self.y, self.r, self.current_fp, self.bpm):
                self.hold_objs.remove(note)
            if note.summon_hit:
                self.hits.append(Hit(note.x, note.y, note.summon_hit_time))
                note.summon_hit = False
            if note.now_fp > NOTE_REMOVE_MAX:
                break

    def update_hit(self, time):
        for i in self.hits:
            if i.update(time):
                self.hits.remove(i)

    def update_event(self, time: float, event: list[dict], evtype: int) -> float:
        nowevent: dict = event[0]
        if time < nowevent["endTime"]:
            if evtype == 3:
                v = nowevent["lastFp"] + nowevent["value"] * (time - nowevent["startTime"])
            else:
                v = linear(time, nowevent["startTime"], nowevent["endTime"], nowevent["start"], nowevent["end"])
            if evtype == 0:
                v2 = linear(time, nowevent["startTime"], nowevent["endTime"], nowevent["start2"], nowevent["end2"])
                return v, v2
            else:
                return v
        else:
            event.pop(0)
            return self.update_event(time, event, evtype)

    def update(self, time: float) -> None:
        self.x, self.y = self.update_event(time, self.move_event, 0)
        self.r = self.update_event(time, self.rotate_event, 1)
        self.a = self.update_event(time, self.alpha_event, 2)
        self.current_fp = self.update_event(time, self.speed_event, 3)

    def draw(self) -> None:
        if self.a > 0:
            draw_rect(self.x, self.y, LINE_WIDTH, LINE_HEIGHT, self.r, self.a, (0.5, 0.5), LINE_COLOR)

class Note:
    def __init__(self, data: dict) -> None:
        self.type: int = data["type"]
        self.time: float = data["time"]
        self.x_position: float = data["positionX"]
        self.end_time: float = data["endTime"]
        self.hold_time: float = data["holdTime"]
        self.hold_speed: float = data["speed"] if self.type == 3 else 1
        self.speed: float = 1 if self.type == 3 else data["speed"]
        self.floor_position: float = data["floorPosition"]
        self.is_hl: bool = data["isHL"]
        self.above: int = data["above"]
        self.now_fp: float = self.floor_position
        self.real_fp: float = self.floor_position * self.speed * self.above
        self.length: float = SPEED_EVENT_H * self.hold_time * self.hold_speed * self.above
        self.start_length: float = self.length
        self.is_click: bool = False
        self.summon_hit: bool = False
        self.summon_hit_time: float = 0
        self.timer: float = float("inf")
        self.judge_end_time: float = max(self.time, self.end_time - 0.2)
        self.is_add_combo: bool = False
        self.x: float = 0
        self.y: float = 0
        self.end_x: float = 0
        self.end_y: float = 0
        self.r: float = 0
        self.yscale: float = HOLD_YSCALE
        self.scale: float = NOTE_SCALE

    def get_position(self, linex: float, liney: float, liner: float, notex: float, notey: float) -> float:
        __temp_x: float = linex
        __temp_y: float = liney
        if notex != 0:
            __temp_r: float = math.radians(liner)
            __temp_x += math.cos(__temp_r) * notex
            __temp_y += math.sin(__temp_r) * notex
        if notey != 0:
            __temp_r: float = math.radians(liner + 90)
            __temp_x += math.cos(__temp_r) * notey
            __temp_y += math.sin(__temp_r) * notey
        return __temp_x, __temp_y, liner

    def add_combo(self) -> None:
        data.judges.combo += 1
        data.judges.perfect += 1
        self.is_add_combo = True

    def update(self, time: float, line_x: float, line_y: float, line_r: float, current_fp: float, bpm: float) -> None:
        self.now_fp = self.floor_position - current_fp
        self.real_fp = self.now_fp * self.speed * self.above
        if time >= self.time:
            if not self.is_click:
                NOTE_SOUNDS[self.type - 1].play()
                self.timer = self.time + 30 / bpm
                self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                self.x, self.y, self.r = self.get_position(line_x, line_y, line_r, self.x_position, 0)
                self.summon_hit = True
                self.summon_hit_time = self.time
                self.is_click = True
            if self.type == 3 and not time >= self.end_time:
                self.length = linear(time, self.time, self.end_time, self.start_length, 0)
                self.x, self.y, self.r = self.get_position(line_x, line_y, line_r, self.x_position, 0)
                self.endx, self.endy, self.r = self.get_position(line_x, line_y, line_r, self.x_position, self.length)
                if time >= self.timer:
                    self.summon_hit = True
                    self.summon_hit_time = self.timer
                    self.timer += 30 / bpm
                    self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                if time >= self.judge_end_time and not self.is_add_combo:
                    self.add_combo()
            else:
                if not self.is_add_combo:
                    self.add_combo()
                return True
        else:
            self.x, self.y, self.r = self.get_position(line_x, line_y, line_r, self.x_position, self.real_fp)
            if self.now_fp < -0.01:
                return
            if self.type == 3:
                self.endx, self.endy, self.r = self.get_position(line_x, line_y, line_r, self.x_position, self.real_fp + self.length)

        if self.now_fp * self.speed > NOTE_REMOVE_MAX:
            return
        if self.hold_speed == 0 and self.type == 3:
            return

        self.draw()

    def draw(self) -> None:
        if self.type == 3:
            draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], self.x, self.y, self.scale, self.yscale * self.length, self.r, 1, (0.5, 0))
            if not self.is_click:
                draw_texture(NOTE_TEXTURES[4 + self.is_hl * 6], self.x, self.y, self.scale, self.scale * self.above, self.r, 1, (0.5, 1))
            draw_texture(NOTE_TEXTURES[5 + self.is_hl * 6], self.endx, self.endy, NOTE_SCALE, NOTE_SCALE * self.above, self.r, 1, (0.5, 0))
        else:
            draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], self.x, self.y, NOTE_SCALE, NOTE_SCALE, self.r, 1, (0.5, 0.5))

class Hit:
    def __init__(self, x: float, y: float, startTime: float) -> None:
        self.x: float = x
        self.y: float = y
        self.start_time: float = startTime
        self.now_time: float = self.start_time
        self.progress: float = 0.
        self.hit_i: int = 0
        self.rot: float = tuple(math.radians(random.uniform(0, 360)) for i in range(4))
        self.distance: float = tuple(random.uniform(135, 165) * WIDTH_SCALE for i in range(4))

    def update(self, time: float) -> None:
        self.now_time = time - self.start_time
        if self.now_time > 0.545 or self.now_time < 0:
            return True
        self.progress = self.now_time / 0.5
        self.hit_i = max(min(math.floor(self.progress * 29), 29), 0)
        self.draw()

    def draw(self) -> None:
        if self.progress <= 1:
            draw_texture(HIT_TEXTURES[self.hit_i], self.x, self.y, HIT_SCALE, HIT_SCALE, 0, 1, (0.5, 0.5), HIT_COLOR)
        n: int = 0
        for r, d in zip(self.rot, self.distance):
            p = self.progress - n * 0.03
            if p >= 0 and p <= 1:
                px = self.x + math.cos(r) * d * particle_easing(p)
                py = self.y + math.sin(r) * d * particle_easing(p)
                a = 1 - p
                size = PARTICLE_SIZE * particle_size_easing(p)
                draw_rect(px, py, size, size, 0, a, (0.5, 0.5), PARTICLE_COLOR)
            n += 1