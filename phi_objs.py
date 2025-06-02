from const import *
from func import *
from dxsound import *
import math
import random
import data

note_time_list = []
note_hl_time = []

NOTE_SOUNDS = (
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\tap.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\drag.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\tap.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\flick.wav")
)

NOTE_TEXTURES = (
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
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdendHL.png")
)

HIT_TEXTURES = tuple(Texture.from_path(f"{RESOURCE_PATH}\\textures\\hits\\{i + 1}.png") for i in range(30))

def to_real_time(tick, bpm):
    return 1.875 / bpm * tick

def linear(time, st, et, s, e):
    return s + (e - s) * ((time - st) / (et - st))

def get_floor_position(events, time):
    _fp = 0
    for i in events:
        if time < i["endTime"]:
            _fp += i["value"] * (time - i["startTime"])
            return _fp
        else:
            _fp += i["fp"]
    return _fp

def init_event(events, bpm):
    for i in events:
        i["startTime"] = to_real_time(i["startTime"], bpm)
        i["endTime"] = to_real_time(i["endTime"], bpm)

def init_move_event(events, bpm):
    init_event(events, bpm)
    for i in events:
        i["start"] = i["start"] * WINDOW_WIDTH
        i["end"] = i["end"] * WINDOW_WIDTH
        i["start2"] = i["start2"] * WINDOW_HEIGHT
        i["end2"] = i["end2"] * WINDOW_HEIGHT

def init_speed_event(events, bpm):
    init_event(events, bpm)
    for i in events:
        i["value"] = i["value"] * Y
        i["fp"] = i["value"] * (i["endTime"] - i["startTime"])

particle_easing = lambda x: 9 * x / (8.3 * x + 1)

class JudgeLine:
    def __init__(self, data: dict):
        self.bpm = data["bpm"]
        self.notes_above = data["notesAbove"]
        self.notes_below = data["notesBelow"]
        self.note_list = []
        self.move_events = data["judgeLineMoveEvents"]
        self.rotate_events = data["judgeLineRotateEvents"]
        self.alpha_events = data["judgeLineDisappearEvents"]
        self.speed_events = data["speedEvents"]
        self.hits = []
        self.x = 0
        self.y = 0
        self.r = 0
        self.a = 0
        self.fp = 0
        self.ufp = 0
        self.inote = True
        self.preload()

    def preload(self):
        self.move_events = [i for i in self.move_events if not i["startTime"] == i["endTime"]]
        self.rotate_events = [i for i in self.rotate_events if not i["startTime"] == i["endTime"]]
        self.alpha_events = [i for i in self.alpha_events if not i["startTime"] == i["endTime"]]
        self.speed_events = [i for i in self.speed_events if not i["startTime"] == i["endTime"]]
        init_move_event(self.move_events, self.bpm)
        init_event(self.rotate_events, self.bpm)
        init_event(self.alpha_events, self.bpm)
        init_speed_event(self.speed_events, self.bpm)
        ### revelation
        #for i in self.alpha_events:
        #    i['start'] = i['start'] * 0.8 + 0.2
        #    i['end'] = i['end'] * 0.8 + 0.2
        ###
        for i in self.notes_above:
            i["isAbove"] = 1
        for i in self.notes_below:
            i["isAbove"] = -1
        self.note_list = self.notes_above + self.notes_below
        n = 0
        for i in self.note_list:
            i["time"] = to_real_time(i["time"], self.bpm)
            if i["time"] in note_time_list and not i["time"] in note_hl_time:
                note_hl_time.append(i["time"])
            note_time_list.append(i["time"])
            i["holdTime"] = to_real_time(i["holdTime"], self.bpm)
            i["positionX"] = i["positionX"] * X
            i["floorPosition"] = get_floor_position(self.speed_events, i["time"])
            if i["type"] == 3:
                i["holdSpeed"] = i["speed"]
                i["speed"] = 1
                i["length"] = i["holdSpeed"] * Y * i["holdTime"]
                i["judgeTime"] = i["time"] + (i["holdTime"] - 0.2)
            else:
                i["holdSpeed"] = 1
                i["length"] = 0
                i["judgeTime"] = 0
            n += 1

    def load_note(self):
        self.notes = [Note(data) for data in self.note_list if data["type"] != 3]
        self.note_holds = [Note(data) for data in self.note_list if data["type"] == 3]
        s = {}
        for i in self.notes:
            if i.speed not in s:
                s[i.speed] = []
            s[i.speed].append(i)
        self.notes = [s[k] for k in s]
        for i in self.notes:
            i.sort(key=lambda x: x.time)
        self.note_holds.sort(key=lambda x: x.time)
        self.inote = len(self.notes) > 0 or len(self.note_holds) > 0
    
    def load_note_hl(self):
        for i in self.note_list:
            if i["time"] in note_hl_time:
                i["isHL"] = True
            else:
                i["isHL"] = False

    def update_event(self, events, time):
        if time < events[0]["endTime"]:
            return linear(time, events[0]["startTime"], events[0]["endTime"], events[0]["start"], events[0]["end"])
        else:
            events.pop(0)
            return self.update_event(events, time)

    def update_move_event(self, events, time):
        if time < events[0]["endTime"]:
            return linear(time, events[0]["startTime"], events[0]["endTime"], events[0]["start"], events[0]["end"]), linear(time, events[0]["startTime"], events[0]["endTime"], events[0]["start2"], events[0]["end2"])
        else:
            events.pop(0)
            return self.update_move_event(events, time)

    def update_speed_event(self, events, time):
        if time < events[0]["endTime"]:
            return linear(time, events[0]["startTime"], events[0]["endTime"], self.ufp, self.ufp + events[0]["fp"])
        else:
            self.ufp = self.ufp + events[0]["fp"]
            events.pop(0)
            return self.update_speed_event(events, time)

    def update_note(self, time):
        for s in self.notes[:]:
            for note in s[:]:
                if note.update(time, self.x, self.y, self.r, self.fp, self.bpm):
                    self.hits.append(Hit(note.x, note.y, note.time))
                    s.remove(note)
                if note.now_fp * note.speed > 2 * WINDOW_HEIGHT:
                    break

    def update_hold(self, time):
        for note in self.note_holds[:]:
            if note.update(time, self.x, self.y, self.r, self.fp, self.bpm):
                self.note_holds.remove(note)
            if note.play_hit:
                self.hits.append(Hit(note.x, note.y, note.hittime))
                note.play_hit = False
            if note.now_fp > 2 * WINDOW_HEIGHT:
                break

    def update_hit(self, time):
        for hit in self.hits[:]:
            if hit.update(time):
                self.hits.remove(hit)

    def update(self, time):
        self.x, self.y = self.update_move_event(self.move_events, time)
        self.r = self.update_event(self.rotate_events, time)
        self.a = self.update_event(self.alpha_events, time)
        if self.inote:
            self.fp = self.update_speed_event(self.speed_events, time)

    def draw(self):
        if self.a > 0:
            draw_rect(self.x, self.y, LINE_WIDTH, LINE_HEIGHT, self.r, self.a, (0.5,0.5), LINE_COLOR, xoffset=X_OFFSET)

class Note:
    def __init__(self, data: dict):
        self.type = data["type"]
        self.time = data["time"]
        self.x_position = data["positionX"]
        self.hold_time = data["holdTime"]
        self.speed = data["speed"]
        self.hold_speed = data["holdSpeed"]
        self.floor_position = data["floorPosition"]
        self.is_above = data["isAbove"]
        self.length = data["length"]
        self.judge_time = data["judgeTime"]
        self.judgeed = False
        self.start_length = self.length
        self.now_fp = self.floor_position
        self.r_fp = self.now_fp * self.speed * self.is_above
        self.click = False
        self.is_hl = False
        self.yscale = HOLD_YSCALE
        self.is_hl = data["isHL"]
        self.scale = NOTE_SCALE
        if self.is_hl:
            self.yscale = HOLD_HL_YSCALE
            if self.type == 3:
                self.scale = HOLD_HL_SCALE
        self.x = 0
        self.y = 0
        self.endx = 0
        self.endy = 0
        self.timer = float("inf")
        self.play_hit = False
        self.hittime = 0

    def update(self, time, linex, liney, linerot, currect_floor_position, bpm):
        self.now_fp = self.floor_position - currect_floor_position
        self.r_fp = self.now_fp * self.speed * self.is_above
        if time >= self.time:
            if not self.click:
                self.timer = self.time + 30 / bpm
                self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                NOTE_SOUNDS[self.type - 1].play()
                self.click = True
                self.hittime = self.time
                self.play_hit = True
            if self.type == 3 and time < self.time + self.hold_time:
                self.length = linear(time, self.time, self.time + self.hold_time, self.start_length, 0)
                self.now_fp = 0
                self.r_fp = 0
                if time >= self.timer:
                    self.hittime = self.timer
                    self.play_hit = True
                    self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                    self.timer += 30 / bpm
                if time >= self.judge_time and self.judgeed == False:
                    self.judgeed = True
                    data.judges.perfect += 1
                    data.judges.combo += 1
            else:
                self.x = linex + math.cos(math.radians(linerot)) * self.x_position
                self.y = liney + math.sin(math.radians(linerot)) * self.x_position
                if self.judgeed == False:
                    self.judgeed = True
                    data.judges.perfect += 1
                    data.judges.combo += 1
                return True
        self.x = linex + math.cos(math.radians(linerot)) * self.x_position
        self.y = liney + math.sin(math.radians(linerot)) * self.x_position
        self.x += math.cos(math.radians(linerot + 90)) * self.r_fp
        self.y += math.sin(math.radians(linerot + 90)) * self.r_fp
        if self.type == 3:
            self.endx = self.x + math.cos(math.radians(linerot + 90)) * (self.length * self.is_above)
            self.endy = self.y + math.sin(math.radians(linerot + 90)) * (self.length * self.is_above)

        if self.now_fp * self.speed > WINDOW_HEIGHT * 2 or math.ceil(self.now_fp) < 0 or self.hold_speed == 0:
            return

        self.draw(self.x, self.y, self.endx, self.endy, linerot)

    def draw(self, x, y, endx, endy, rot):
        if self.type == 3:
            draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], x, y, self.scale, self.yscale * self.length * self.is_above, rot, 1, (0.5,0), (1,1,1), xoffset=X_OFFSET)
            if not self.click:
                draw_texture(NOTE_TEXTURES[4 + self.is_hl * 6], x, y, self.scale, self.scale * self.is_above, rot, 1, (0.5,1), (1,1,1), xoffset=X_OFFSET)
            draw_texture(NOTE_TEXTURES[5 + self.is_hl * 6], endx, endy, NOTE_SCALE, NOTE_SCALE * self.is_above, rot, 1, (0.5,0), (1,1,1), xoffset=X_OFFSET)
        else:
            draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], x, y, NOTE_SCALE, NOTE_SCALE, rot, 1, (0.5,0.5), (1,1,1), xoffset=X_OFFSET)

class Hit:
    def __init__(self, x, y, startTime):
        self.x = x
        self.y = y
        self.start_time = startTime
        self.now_time = self.start_time
        self.p = 0
        self.hit_i = 0
        self.rot = tuple(math.radians(random.uniform(0, 360)) for i in range(4))
        self.distance = tuple(random.uniform(130, 160) * WIDTH_SCALE for i in range(4))

    def update(self, time):
        self.now_time = time - self.start_time
        self.p = self.now_time / 0.5
        self.hit_i = max(min(math.floor(self.p * 29), 29), 0)
        if self.now_time > 0.545 or self.now_time < 0:
            return True
        self.draw()

    def draw(self):
        if self.p <= 1:
            draw_texture(HIT_TEXTURES[self.hit_i], self.x, self.y, HIT_SCALE, HIT_SCALE, 0, 1, (0.5, 0.5), HIT_COLOR, xoffset=X_OFFSET)
        n = 0
        for r, d in zip(self.rot, self.distance):
            p = self.p - n * 0.03
            if p >= 0 and p <= 1:
                px = self.x + math.cos(r) * d * particle_easing(p)
                py = self.y + math.sin(r) * d * particle_easing(p)
                a = 1 - p
                size = PARTICLE_SIZE * (((0.2078 * p - 1.6524) * p + 1.6399) * p + 0.4988)
                draw_rect(px, py, size, size, 0, a, (0.5, 0.5), PARTICLE_COLOR, xoffset=X_OFFSET)
            n += 1