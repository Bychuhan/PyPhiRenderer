from const import *
from func import *
from dxsound import *
from rpe_easings import *
from log import *
from core import *
import math
import random
import data

note_time_list = []
note_hl_time = []

particle_easing = lambda x: 9 * x / (8.3 * x + 1)

NOTE_SOUNDS = (
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\tap.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\tap.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\flick.wav"),
    directSound(f"{RESOURCE_PATH}\\sounds\\hitsounds\\drag.wav")
)

NOTE_TEXTURES = (
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\tap.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\hold.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\flick.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\drag.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdhead.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdend.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\tapHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\flickHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\dragHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdheadHL.png"),
    Texture.from_path(f"{RESOURCE_PATH}\\textures\\holdendHL.png")
)

HIT_TEXTURES = tuple(Texture.from_path(f"{RESOURCE_PATH}\\textures\\hits\\{i + 1}.png") for i in range(30))

LINE_TEXTURES = {}

NOTE_HITSOUNDS = {}

def linear(time, st, et, s, e):
    return s + (e - s) * ((time - st) / (et - st))

def load_textures(lines, path):
    for i in lines:
        if i.istexture:
            if i.texture not in LINE_TEXTURES:
                LINE_TEXTURES[i.texture] = Texture.from_path(f"{path}/{i.texture}")
                info(f"Loaded texture | {i.texture}")

def load_hitsounds(lines, path):
    for i in lines:
        for note in i.notes:
            if "hitsound" in note and note["hitsound"] != "":
                if note["hitsound"] not in NOTE_HITSOUNDS:
                    NOTE_HITSOUNDS[note["hitsound"]] = directSound(f"{path}/{note["hitsound"]}")
                    info(f"Loaded hitsound | {note["hitsound"]}")

def beat(beat):
    return beat[0] + beat[1] / beat[2]

def to_real_time(bpmlist, time, bpmfactor):
    if len(bpmlist) > 1:
        time_ = 0
        for i in bpmlist:
            try:
                if beat(time) < i["endTime"]:
                    time_ += 60 / i["bpm"] * (beat(time) - i["startTime"])
                    break
                else:
                    time_ += 60 / i["bpm"] * (i["endTime"] - i["startTime"])
            except IndexError:
                time_ += 60 / i["bpm"] * (beat(time) - i["startTime"])
                break
        return time_ * bpmfactor
    else:
        return (60 / bpmlist[0]["bpm"] * beat(time)) * bpmfactor

def init_event(event, bpmlist, bpmfactor):
    for i in event:
        i["startTime"] = to_real_time(bpmlist, i["startTime"], bpmfactor)
        i["endTime"] = to_real_time(bpmlist, i["endTime"], bpmfactor)
        if "easingType" in i:
            if i["easingType"] < 0 or i["easingType"] > 29:
                i["easingType"] = 0
        i["bezier"] = 0 if "bezier" not in i else i["bezier"]
        i["bezier"] = True if i["bezier"] == 1 else False
        if "bezierPoints" in i:
            i["bezierPoints"] = [(i["bezierPoints"][0], i["bezierPoints"][1]), (i["bezierPoints"][0], i["bezierPoints"][1])]

def init_movex_event(event, bpmlist, bpmfactor):
    for n in event:
        init_event(n, bpmlist, bpmfactor)
        for i in n:
            i["start"] = i["start"] / 1350 * WINDOW_WIDTH
            i["end"] = i["end"] / 1350 * WINDOW_WIDTH

def init_movey_event(event, bpmlist, bpmfactor):
    for n in event:
        init_event(n, bpmlist, bpmfactor)
        for i in n:
            i["start"] = i["start"] / 900 * WINDOW_HEIGHT
            i["end"] = i["end"] / 900 * WINDOW_HEIGHT

def init_rotate_event(event, bpmlist, bpmfactor):
    for n in event:
        init_event(n, bpmlist, bpmfactor)
        for i in n:
            i["start"] = 0-i["start"]
            i["end"] = 0-i["end"]

def init_alpha_event(event, bpmlist, bpmfactor):
    for n in event:
        init_event(n, bpmlist, bpmfactor)
        for i in n:
            i["start"] = i["start"] / 255
            i["end"] = i["end"] / 255

def init_color_event(event, bpmlist, bpmfactor):
    init_event(event, bpmlist, bpmfactor)
    for i in event:
        i["start"] = [n / 255 for n in i["start"]]
        i["end"] = [n / 255 for n in i["end"]]

def init_paint_event(event, bpmlist, bpmfactor):
    init_event(event, bpmlist, bpmfactor)
    for i in event:
        if i["start"] > 0:
            i["start"] = i["start"] / 1350 * WINDOW_WIDTH
        if i["end"] > 0:
            i["end"] = i["end"] / 1350 * WINDOW_WIDTH

def init_text_event(event, bpmlist, bpmfactor):
    init_event(event, bpmlist, bpmfactor)
    for i in event:
        if is_number(i['start']) and is_number(i['end']) and "%P%" in i['start'] and "%P%" in i['end']:
            if i['start'].isdigit() and i['end'].isdigit():
                i['type'] = 3
            else:
                i['type'] = 2
        elif i['start'] == i['end']:
            i['type'] = 0
        elif i['start'][0:len(i['end'])] == i['end'] or i['end'][0:len(i['start'])] == i['start']:
            _t = []
            if i['start'][0:len(i['end'])] == i['end']:
                _ut = i['start']
                _t.append(i['start'])
                for t in i['start'][len(i['end']):len(i['start'])]:
                    if is_chinese(t):
                        _t.append(_ut)
                    _ut=_ut[:-1]
                    _t.append(_ut)
            else:
                _ut = i['start']
                _t.append(i['start'])
                for t in i['end'][len(i['start']):len(i['end'])]:
                    if is_chinese(t):
                        _t.append(_ut)
                    _ut+=t
                    _t.append(_ut)
            i['t'] = _t
            i['type'] = 1
        else:
            i['type'] = 0

def init_speed_event(event, bpmlist, bpmfactor):
    en = 0
    for n in event:
        init_event(n, bpmlist, bpmfactor)
        s = []
        if n:
            num = 0
            for i in n:
                i["start"] = i["start"] * 120 / 900 * WINDOW_HEIGHT
                i["end"] = i["end"] * 120 / 900 * WINDOW_HEIGHT
                i["fp"] = (i["start"] + i["end"]) / 2 * (i["endTime"] - i["startTime"])
                s.append(i)
                if num == len(n)-1:
                    break
                if n[num+1]["startTime"] != i["endTime"]:
                    t = {}
                    t["startTime"] = i["endTime"]
                    t["endTime"] = n[num+1]["startTime"]
                    t["start"] = i["end"]
                    t["end"] = i["end"]
                    t["fp"] = i["end"] * (t["endTime"] - t["startTime"])
                    s.append(t)
                num += 1
            i = n[len(n)-1]
            t = {'endTime': 100000000}
            t["startTime"] = i["endTime"]
            t["start"] = i["end"]
            t["end"] = i["end"]
            t["fp"] = i["end"] * (100000000 - t["startTime"])
            s.append(t)
        else:
            t = {'startTime': 0, 'endTime': 100000000, 'start': 0, 'end': 0}
            t["fp"] = t["end"] * (100000000 - t["startTime"])
            s.append(t)
        ufp = 0
        for i in s:
            i['ufp'] = ufp
            ufp += i['fp']
        event[en] = s
        en += 1

def init_contorl_event(event: list, keyname):
    # 我也没想到是向后填充。。
    _e = event.copy()
    _e.sort(key=lambda x: x["x"])
    _e = _e[::-1]
    for i in _e:
        i["x"] = i["x"] / 900 * WINDOW_HEIGHT
        i["start"] = i[keyname]
        if i["easing"] < 0 or i["easing"] > 29:
            i["easing"] = 0
    for i in enumerate(_e):
        if i[0] == 0:
            i[1]["endx"] = i[1]["x"]
            i[1]["end"] = i[1]["start"]
            i[1]["x"] = i[1]["x"] + 9999999
        else:
            i[1]["endx"] = i[1]["x"]
            i[1]["x"] = _e[i[0]-1]["endx"]
            i[1]["end"] = i[1]["start"]
            i[1]["start"] = _e[i[0]-1]["end"]
        _e[i[0]] = i[1]
    if _e[-1]["x"] > -9999999:
        _e.append({"x": _e[-1]["x"], "endx": -9999999, "start": _e[-1]["end"], "end": _e[-1]["end"], "easing": 0})
    return _e

def get_floorposition(speedevents, time):
    _fp = 0
    for n in speedevents:
        for i in n:
            if time < i["endTime"]:
                _fp += (i["start"] + ((i["start"] + (i["end"] - i["start"]) * ((time - i["startTime"]) / (i["endTime"] - i["startTime"]))))) / 2 * (time - i["startTime"])
                break
            else:
                _fp += i["fp"]
    return _fp

class JudgeLine:
    def __init__(self, data: dict, bpm_list):
        self.bpm_list = bpm_list
        self.events = [event for event in data["eventLayers"] if event is not None]
        self.movex_events = [event["moveXEvents"] for event in self.events if "moveXEvents" in event]
        self.movey_events = [event["moveYEvents"] for event in self.events if "moveYEvents" in event]
        self.rotate_events = [event["rotateEvents"] for event in self.events if "rotateEvents" in event]
        self.alpha_events = [event["alphaEvents"] for event in self.events if "alphaEvents" in event]
        self.speed_events = [event["speedEvents"] for event in self.events if "speedEvents" in event]
        self.scalex_events = []
        self.scaley_events = []
        self.color_events = []
        self.paint_events = []
        self.text_events = []
        self.ispen = False
        self.text = None
        self.color = LINE_COLOR
        if "extended" in data:
            if "scaleXEvents" in data["extended"]:
                self.scalex_events = data["extended"]["scaleXEvents"]
            if "scaleYEvents" in data["extended"]:
                self.scaley_events = data["extended"]["scaleYEvents"]
            if "colorEvents" in data["extended"]:
                self.color_events = data["extended"]["colorEvents"]
            if "paintEvents" in data["extended"]:
                self.paint_events = data["extended"]["paintEvents"]
                self.ispen = True
                self.color = (1, 1, 1)
            if "textEvents" in data["extended"]:
                self.text_events = data["extended"]["textEvents"]
                self.text = Text("", FONT)
                self.color = RPE_TEXT_COLOR
        self.pen_pos = []
        self.pensize = -1
        self.notes = []
        if "notes" in data:
            self.notes = data["notes"]
        self.x = 0
        self.y = 0
        self.pux = 999999
        self.puy = 999999
        self.r = 0
        self.a = 0
        self.scalex = 1
        self.scaley = 1
        self.father_line = None
        self.utime = 0
        if "father" in data:
            self.father = data["father"]
        else:
            self.father = -1
        if self.father == -1:
            self.default_x = WINDOW_WIDTH / 2
            self.default_y = WINDOW_HEIGHT / 2
        else:
            self.default_x = 0
            self.default_y = 0
        self.anchor = [0.5, 0.5]
        if "anchor" in data:
            self.anchor = data["anchor"]
        self.bpm_factor = 1
        if "bpmfactor" in data:
            self.bpm_factor = data["bpmfactor"]
        self.texture = data["Texture"]
        self.istexture = False
        if self.texture != "line.png":
            self.istexture = True
            self.color = RPE_TEXTURE_COLOR
        self.x_cache = None
        self.y_cache = None
        self.r_cache = None
        self.z_order = 0
        if "zOrder" in data:
            self.z_order = data["zOrder"]
        self.inote = False
        self.cfp = 0
        self.ufp = 0
        self.hits = []
        self.attach_ui = -1
        if "attachUI" in data:
            self.attach_ui = data["attachUI"]
            if self.attach_ui != -1:
                if self.attach_ui == "bar":
                    self.color = [0.569, 0.569, 0.569]
                else:
                    self.color = [1, 1, 1]
        self.default_color = self.color
        self.is_cover = (True if data["isCover"] == 1 else False)
        self.scale_on_notes = (data["scaleOnNotes"] if "scaleOnNotes" in data else 0)
        self.n_notes = []
        self.note_holds = []
        self.alpha_control = data["alphaControl"]
        self.y_control = data["yControl"]
        self.preload()

    def preload(self):
        init_movex_event(self.movex_events, self.bpm_list, self.bpm_factor)
        init_movey_event(self.movey_events, self.bpm_list, self.bpm_factor)
        init_rotate_event(self.rotate_events, self.bpm_list, self.bpm_factor)
        init_alpha_event(self.alpha_events, self.bpm_list, self.bpm_factor)
        init_event(self.scalex_events, self.bpm_list, self.bpm_factor)
        init_event(self.scaley_events, self.bpm_list, self.bpm_factor)
        init_color_event(self.color_events, self.bpm_list, self.bpm_factor)
        init_paint_event(self.paint_events, self.bpm_list, self.bpm_factor)
        if not self.speed_events:
            self.speed_events.append([])
        init_speed_event(self.speed_events, self.bpm_list, self.bpm_factor)
        init_text_event(self.text_events, self.bpm_list, self.bpm_factor)
        self.alpha_control = init_contorl_event(self.alpha_control, 'alpha')
        self.y_control = init_contorl_event(self.y_control, 'y')
        n = 0
        a = len(self.notes)
        for i in self.notes:
            if i["above"] != 1:
                i["above"] = -1
            i["alpha"] = i["alpha"] / 255
            i["startTime"] = to_real_time(self.bpm_list, i["startTime"], self.bpm_factor)
            if i["startTime"] in note_time_list and not i["startTime"] in note_hl_time:
                note_hl_time.append(i["startTime"])
            note_time_list.append(i["startTime"])
            i["endTime"] = to_real_time(self.bpm_list, i["endTime"], self.bpm_factor)
            i["positionX"] = i["positionX"] / 1350 * WINDOW_WIDTH
            i["visibleTime"] = i["startTime"] - i["visibleTime"]
            i["yOffset"] = i["yOffset"] / 900 * WINDOW_HEIGHT
            i["isFake"] = (True if i["isFake"] == 1 else False)
            if "tint" in i:
                i["tint"] = [(i / 255) for i in i["tint"]]
            else:
                i["tint"] = [1, 1, 1]
            if "tintHitEffects" in i:
                i["tintHitEffects"] = [(i / 255) for i in i["tintHitEffects"]]
            else:
                i["tintHitEffects"] = HIT_COLOR
            i["fp"] = get_floorposition(self.speed_events, i["startTime"])
            i["endfp"] = i["fp"]
            i["length"] = 0
            if i["type"] == 2:
                i["endfp"] = get_floorposition(self.speed_events, i["endTime"])
                i["length"] = i["endfp"] - i["fp"]
            n += 1

    def load_note_hl(self):
        for i in self.notes:
            if i["startTime"] in note_hl_time:
                i["isHL"] = True
            else:
                i["isHL"] = False

    def note_s_sy(self, notes):
        s = {}
        for i in notes:
            if not i.speed in s:
                s[i.speed] = []
            s[i.speed].append(i)
        s = [s[k] for k in s]
        _y = []
        for n in s:
            y = {}
            for i in n:
                if not i.y_offset in y:
                    y[i.y_offset] = []
                y[i.y_offset].append(i)
            y = list(y[k] for k in y)
            _y.append(y.copy())
        for speed in _y:
            for y in speed:
                y.sort(key = lambda x: x.time)
        return _y
        # 史。

    def note_sort(self, notes):
        n = []
        n.append(self.note_s_sy([i for i in notes if i.is_above == 1]))
        n.append(self.note_s_sy([i for i in notes if i.is_above == -1]))
        return n

    def load_note(self):
        for i in self.notes:
            i["hitsound_path"] = (i["hitsound"] if "hitsound" in i else None)
            i["hitsound"] = (NOTE_HITSOUNDS[i["hitsound"]] if "hitsound" in i else NOTE_SOUNDS[i["type"]-1])
        self.n_notes = [Note(data, self.alpha_control, self.y_control) for data in self.notes if data["type"] != 2]
        self.note_holds = [Note(data, self.alpha_control, self.y_control) for data in self.notes if data["type"] == 2]
        self.n_notes = self.note_sort(self.n_notes)
        self.note_holds = self.note_sort(self.note_holds)
        self.inote = len(self.n_notes) > 0 or len(self.note_holds) > 0

    def update_note(self, time, keys):
        for a in self.n_notes[:]:
            for speed in a[:]:
                for y in speed[:]:
                    for note in y[:]:
                        u = note.update(time, self.x, self.y, self.r, self.cfp, self.a >= 0, 1, self.is_cover, self.scale_on_notes, RPE_LINE_WIDTH * self.scalex, keys)
                        if u:
                            if not note.is_fake:
                                if AUTOPLAY:   
                                    self.hits.append(Hit(note.x, note.y, note.hittime, note.tint_hit))
                                else:
                                    if note.is_judge:
                                        if note.judge_type != 'b':
                                            self.hits.append(Hit(note.x, note.y, time, (note.tint_hit if note.judge_type == 'p' else HIT_COLOR_GOOD)))
                            y.remove(note)
                        if u == 0:
                            break

    def update_hold(self, time, bpm, keys):
        self.x_cache = None
        self.y_cache = None
        self.r_cache = None
        for a in self.note_holds[:]:
            for speed in a[:]:
                for y in speed[:]:
                    for note in y[:]:
                        u = note.update(time, self.x, self.y, self.r, self.cfp, self.a >= 0, bpm, self.is_cover, self.scale_on_notes, RPE_LINE_WIDTH * self.scalex, keys)
                        if note.play_hit:
                            if AUTOPLAY:
                                self.hits.append(Hit(note.x, note.y, note.hittime, note.tint_hit))
                            else:
                                self.hits.append(Hit(note.x, note.y, time, (note.tint_hit if note.judge_type == 'p' else HIT_COLOR_GOOD)))
                            note.play_hit = False
                        if u:
                            y.remove(note)
                        if u == 0:
                            break

    def note_judge(self, time):
        n = None
        t = 9999999
        rn = None
        rt = 9999999
        for a in self.n_notes:
            for speed in a:
                for y in speed:
                    for note in y:
                        if note.time-time > 0.18:
                            break
                        if note.type == 1:
                            if not note.is_fake:
                                if not note.is_judge:
                                    if note.time-time < t:
                                        t = note.time-time
                                        n = note
        for a in self.note_holds:
            for speed in a:
                for y in speed:
                    for note in y:
                        if note.time-time > 0.16:
                            break
                        if not note.is_fake:
                            if not note.is_judge:
                                if note.time-time < t:
                                    t = note.time-time
                                    n = note
        for a in self.n_notes:
            for speed in a:
                for y in speed:
                    for note in y:
                        if note.time-time > 0.08:
                            break
                        if note.type == 3 or note.type == 4:
                            if not note.is_fake:
                                if not note.judge_dfn:
                                    if not note.is_judge:
                                        if note.time-time < rt:
                                            rt = note.time-time
                                            rn = note
        return t, n, rt, rn

    def update_hit(self, time):
        for hit in self.hits[:]:
            if hit.update(time):
                self.hits.remove(hit)

    def get_pos(self, time, default=True):
        if self.x_cache is None or self.y_cache is None or self.r_cache is None:
            self.x = self.default_x
            if self.movex_events:
                for i in self.movex_events:
                    if i:
                        self.x += self.event_update(i, time, 0)
            self.y = self.default_y
            if self.movey_events:
                for i in self.movey_events:
                    if i:
                        self.y += self.event_update(i, time, 0)
            self.r = 0
            if self.rotate_events:
                for i in self.rotate_events:
                    if i:
                        self.r += self.event_update(i, time, 0)
            if self.father != -1:
                fx, fy, fr = self.father_line.get_pos(time, default)
                yx = self.x
                yy = self.y
                self.x = fx + math.cos(math.radians(fr)) * yx
                self.y = fy + math.sin(math.radians(fr)) * yx
                self.x += math.cos(math.radians(fr+90)) * yy
                self.y += math.sin(math.radians(fr+90)) * yy
            self.x_cache = self.x
            self.y_cache = self.y
            self.r_cache = self.r
        if default:
            return self.x_cache, self.y_cache, self.r_cache
        else:
            return self.x_cache - self.default_x, self.y_cache - self.default_y, self.r_cache

    def get_data(self, time):
        x, y, r = self.get_pos(time, False)
        self.a = 0
        if self.alpha_events:
            for i in self.alpha_events:
                if i:
                    self.a += self.event_update(i, time, 0)
        self.scalex = 1
        if self.scalex_events:
            self.scalex = self.event_update(self.scalex_events, time, 1)
        self.scaley = 1
        if self.scaley_events:
            self.scaley = self.event_update(self.scaley_events, time, 1)
        self.color = self.default_color
        if self.color_events:
            self.color = self.colorevent_update(self.color_events, time, self.default_color)
        return x, y, r, self.a, self.scalex, self.scaley, self.color

    def event_update(self, event, time, default):
        if time < event[0]["endTime"]:
            if time >= event[0]["startTime"]:
                __p = (time - event[0]["startTime"]) / (event[0]["endTime"] - event[0]["startTime"])
                return event[0]["start"] + (event[0]["end"] - event[0]["start"]) * (bezier_get_y(__p, *event[0]["bezierPoints"]) if event[0]["bezier"] else rpe_easings[event[0]["easingType"]](__p))
            else:
                return default
        else:
            if len(event) > 1:
                if time >= event[1]["startTime"]:
                    event.pop(0)
                    return self.event_update(event, time, default)
                else:
                    return event[0]["end"]
            else:
                return event[0]["end"]
    
    def colorevent_update(self, event, time, default):
        if time < event[0]["endTime"]:
            if time >= event[0]["startTime"]:
                __p = (time - event[0]["startTime"]) / (event[0]["endTime"] - event[0]["startTime"])
                sc = event[0]["start"].copy()
                ec = event[0]["end"].copy()
                sc[0] = sc[0] + (ec[0] - sc[0]) * (bezier_get_y(__p, *event[0]["bezierPoints"]) if event[0]["bezier"] else rpe_easings[event[0]["easingType"]](__p))
                sc[1] = sc[1] + (ec[1] - sc[1]) * (bezier_get_y(__p, *event[0]["bezierPoints"]) if event[0]["bezier"] else rpe_easings[event[0]["easingType"]](__p))
                sc[2] = sc[2] + (ec[2] - sc[2]) * (bezier_get_y(__p, *event[0]["bezierPoints"]) if event[0]["bezier"] else rpe_easings[event[0]["easingType"]](__p))
                return sc
            else:
                return default
        else:
            if len(event) > 1:
                if time >= event[1]["startTime"]:
                    event.pop(0)
                    return self.colorevent_update(event, time, default)
                else:
                    return event[0]["end"]
            else:
                return event[0]["end"]
    
    def speedevent_update(self, event, time):
        if time < event[0]["endTime"]:
            if event[0]["start"] == event[0]["end"]:
                return event[0]["ufp"] + (event[0]["fp"]) * ((time - event[0]["startTime"]) / (event[0]["endTime"] - event[0]["startTime"]))
            else:
                return event[0]["ufp"] + (event[0]["start"] + ((event[0]["start"] + (event[0]["end"] - event[0]["start"]) * ((time - event[0]["startTime"]) / (event[0]["endTime"] - event[0]["startTime"]))))) / 2 * (event[0]["endTime"] - event[0]["startTime"]) * ((time - event[0]["startTime"]) / (event[0]["endTime"] - event[0]["startTime"]))
        else:
            event.pop(0)
            return self.speedevent_update(event, time)

    def textevent_update(self, event, time):
        if time < event[0]["endTime"]:
            if time >= event[0]["startTime"]:
                if event[0]['type'] == 0:
                    return event[0]["start"]
                elif event[0]['type'] == 1:
                    __p = (time - event[0]["startTime"]) / (event[0]["endTime"] - event[0]["startTime"])
                    return event[0]['t'][int((len(event[0]['t']) - 1) * (bezier_get_y(__p, *event[0]["bezierPoints"]) if event[0]["bezier"] else rpe_easings[event[0]["easingType"]](__p)))]
                else:
                    return event[0]['start']
            else:
                return ""
        else:
            if len(event) > 1:
                if time >= event[1]["startTime"]:
                    event.pop(0)
                    return self.textevent_update(event, time)
                else:
                    return event[0]["end"]
            else:
                return event[0]["end"]

    def update(self, time):
        self.x = self.default_x
        if self.movex_events:
            for i in self.movex_events:
                if i:
                    self.x += self.event_update(i, time, 0)
        self.y = self.default_y
        if self.movey_events:
            for i in self.movey_events:
                if i:
                    self.y += self.event_update(i, time, 0)
        if self.father != -1:
            fx, fy, fr = self.father_line.get_pos(time, True)
            yx = self.x
            yy = self.y
            self.x = fx + math.cos(math.radians(fr)) * yx
            self.y = fy + math.sin(math.radians(fr)) * yx
            self.x += math.cos(math.radians(fr+90)) * yy
            self.y += math.sin(math.radians(fr+90)) * yy
        self.r = 0
        if self.rotate_events:
            for i in self.rotate_events:
                if i:
                    self.r += self.event_update(i, time, 0)
        self.a = 0
        if self.alpha_events:
            for i in self.alpha_events:
                if i:
                    self.a += self.event_update(i, time, 0)
        if self.scalex_events:
            self.scalex = self.event_update(self.scalex_events, time, 1)
        if self.scaley_events:
            self.scaley = self.event_update(self.scaley_events, time, 1)
        if self.color_events:
            self.color = self.colorevent_update(self.color_events, time, self.default_color)
        elif not self.istexture and not self.paint_events and self.text is None:
            if data.judges.judge_type == 1 and self.color != LINE_COLOR_GOOD:
                self.color = LINE_COLOR_GOOD
            if data.judges.judge_type == 0 and self.color != (1, 1, 1):
                self.color = (1, 1, 1)
        if self.paint_events:
            self.pensize = self.event_update(self.paint_events, time, -1)
        if self.text_events:
            self.text.change_text(self.textevent_update(self.text_events, time))
        self.cfp = 0
        for i in self.speed_events:
            self.cfp += self.speedevent_update(i, time)
        if self.ispen:
            if self.pensize < 0:
                self.pen_pos = []
                self.pux = 999999
                self.puy = 999999
                self.utime = time
            elif time >= self.utime:
                if self.x != self.pux or self.y != self.puy:
                    self.pux = self.x
                    self.puy = self.y
                    t = {}
                    t["x"] = self.x
                    t["y"] = self.y
                    t["size"] = self.pensize
                    t["a"] = self.a
                    t["color"] = self.color
                    self.pen_pos.append(t)
                self.utime += PAINT_SPACE

    def draw(self):
        if self.ispen:
            if self.pensize != -1:
                if len(self.pen_pos) > 2:
                    draw_circle(self.pen_pos[0]["x"],self.pen_pos[0]["y"], self.pen_pos[0]["size"], self.pen_pos[0]["a"], self.pen_pos[0]["color"])
                    for i in range(len(self.pen_pos)):
                        if i + 1 != len(self.pen_pos):
                            px = self.pen_pos[i]["x"]
                            py = self.pen_pos[i]["y"]
                            dx = self.pen_pos[i + 1]["x"]
                            dy = self.pen_pos[i + 1]["y"]
                            d = math.sqrt((px-dx)**2+(py-dy)**2)
                            r = math.degrees(math.atan2(dy-py, dx-px))
                            draw_rect(px, py, d, self.pen_pos[i]["size"] * 2, r, self.pen_pos[i]["a"], (0, 0.5), self.pen_pos[i]["color"], xoffset = X_OFFSET)
                            #draw_circle(self.pen_pos[i]["x"],self.pen_pos[i]["y"], self.pen_pos[i]["size"], self.pen_pos[i]["a"], self.pen_pos[i]["color"])
                            #draw_line(self.pen_pos[i]['x'], self.pen_pos[i]['y'], self.pen_pos[i+1]['x'], self.pen_pos[i+1]['y'], 1, (*self.pen_pos[i]['color'], self.pen_pos[i]['a']))
                    l = len(self.pen_pos)-1
                    draw_circle(self.pen_pos[l]["x"],self.pen_pos[l]["y"], self.pen_pos[l]["size"], self.pen_pos[l]["a"], self.pen_pos[l]["color"])
        elif self.istexture:
            if self.a > 0:
                draw_texture(LINE_TEXTURES[self.texture], self.x, self.y, LINE_TEXTURE_SCALE * self.scalex, LINE_TEXTURE_SCALE * self.scaley, self.r, self.a, self.anchor, self.color, xoffset = X_OFFSET)
        elif not self.text is None:
            if self.a > 0:
                self.text.render(self.x, self.y, TEXT_SCALE * self.scalex, TEXT_SCALE * self.scaley, self.r, self.a, self.anchor, self.color)
        elif self.attach_ui == -1:
            if self.a > 0:
                draw_rect(self.x, self.y, RPE_LINE_WIDTH * self.scalex, RPE_LINE_HEIGHT * self.scaley, self.r, self.a, self.anchor, self.color, xoffset = X_OFFSET)

class Note:
    def __init__(self, data: dict, acontrol: dict, ycontrol: list):
        self.floor_position = data["fp"]
        self.end_fp = data["endfp"]
        self.now_fp = data["fp"]
        self.r_fp = data["fp"]
        self.end_r_fp = data["endfp"]
        self.time = data["startTime"]
        self.end_time = data["endTime"]
        self.x_position = data["positionX"]
        self.judge_time = data["endTime"] - 0.2
        self.speed = data["speed"]
        self.is_above = data["above"]
        self.type = data["type"]
        self.is_hl = data["isHL"]
        self.x = 999999
        self.y = 999999
        self.endx = 999999
        self.endy = 999999
        self.length = data["length"]
        self.click = False
        self.judgeed = False
        self.yscale = HOLD_YSCALE
        self.scale = NOTE_SCALE
        if self.is_hl:
            self.yscale = HOLD_HL_YSCALE
            if self.type == 2:
                self.scale = HOLD_HL_SCALE
        self.alpha = data["alpha"]
        self.is_fake = data["isFake"]
        self.size = data["size"]
        self.visible_time = data["visibleTime"]
        self.y_offset_n = data["yOffset"]
        self.play_hit = False
        self.tint = data["tint"]
        self.tint_hit = data["tintHitEffects"]
        self.hitsound: directSound = data["hitsound"]
        self.y_offset = self.y_offset_n * self.speed * self.is_above
        self.update_break = False
        # Judge ↓
        self.judge_type = -1
        self.is_judge = False
        self.timer = self.time
        self.is_miss = False
        self.pre_judge = False
        self.judge_dfn = False
        # Control ↓
        self.alpha_control = acontrol
        self.acontrol_a = 1
        self.acontrol_index = 0
        self.y_control = ycontrol
        self.ycontrol_y = 1
        self.ycontrol_index = 0

    def update_control(self, event: list, y, index):
        _i = index
        if y > event[_i]["endx"]:
            return event[_i]["start"] + (event[_i]["end"] - event[_i]["start"]) * rpe_easings[event[_i]["easing"]]((event[_i]["x"] - y) / (event[_i]["x"] - event[_i]["endx"])), _i
        else:
            if _i < len(event)-1:
                _i += 1
                return self.update_control(event, y, _i)
            else:
                return event[0]["end"], _i

    def update(self, time, linex, liney, linerot, cfp, render_note, bpm, iscover, scale_on_notes, scalex, keys=[]):
        self.update_break = False
        self.now_fp = self.floor_position - cfp
        self.now_end_fp = self.end_fp - cfp
        self.r_fp = self.now_fp * self.speed * self.is_above
        self.end_r_fp = (self.end_fp - cfp) * self.speed * self.is_above

        if AUTOPLAY:
            if time >= self.time:
                if not self.click:
                    if not self.is_fake:
                        self.timer = self.time + 30 / bpm
                        self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                        self.hitsound.play()
                        self.hittime = self.time
                        self.play_hit = True
                    self.click = True
                if self.type == 2 and time < self.end_time:
                    self.length = (self.end_fp - cfp)
                    self.now_fp = 0
                    self.r_fp = 0
                    if not self.is_fake:
                        if time >= self.timer:
                            self.hittime = self.timer
                            self.play_hit = True
                            self.timer += 30 / bpm
                            self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                        if time >= self.judge_time and self.judgeed == False:
                            self.judgeed = True
                            data.judges.perfect += 1
                            data.judges.combo += 1
                else:
                    self.x = linex + math.cos(math.radians(linerot)) * (self.x_position)
                    self.y = liney + math.sin(math.radians(linerot)) * (self.x_position)
                    if self.y_offset != 0:
                        self.x += math.cos(math.radians(linerot + 90)) * self.y_offset
                        self.y += math.sin(math.radians(linerot + 90)) * self.y_offset
                    if not self.is_fake:
                        if self.judgeed == False:
                            self.judgeed = True
                            data.judges.perfect += 1
                            data.judges.combo += 1
                    return True
        else:
            if not self.is_fake:
                if self.type == 3 or self.type == 4:
                    if keys and abs(time-self.time) <= 0.08 and not self.pre_judge:
                        self.pre_judge = True
                    if time >= self.time and self.pre_judge and not self.is_judge:
                        self.judge(0, time)
            if time >= self.time:
                if self.is_fake:
                    self.click = True
                    self.is_judge = True
                if not self.click:
                    if self.type == 2:
                        if not self.is_fake:
                            if self.is_judge:
                                self.timer = self.time + 30 / bpm
                                self.play_hit = True
                        self.click = True
                if self.type == 2 and time < self.end_time:
                    self.length = (self.end_fp - cfp)
                    self.now_fp = 0
                    self.r_fp = 0
                    if not self.is_fake:
                        if self.is_judge and not self.is_miss:
                            if time >= self.timer:
                                self.play_hit = True
                                self.timer -= (self.timer - self.time) % (30 / bpm * 0.26)
                                self.timer += 30 / bpm
                            if time >= self.judge_time and not self.judgeed:
                                self.judgeed = True
                                data.judges.combo += 1
                                if self.judge_type == 'p':
                                    data.judges.perfect += 1
                                else:
                                    data.judges.good += 1
                                    if data.judges.judge_type > 1:
                                        data.judges.judge_type = 1
                else:
                    self.x = linex + math.cos(math.radians(linerot)) * (self.x_position)
                    self.y = liney + math.sin(math.radians(linerot)) * (self.x_position)
                    if self.y_offset != 0:
                        self.x += math.cos(math.radians(linerot + 90)) * self.y_offset
                        self.y += math.sin(math.radians(linerot + 90)) * self.y_offset
                    if not self.is_fake:
                        if self.is_judge and self.type == 2 and not self.is_miss:
                            if self.judgeed == False:
                                data.judges.combo += 1
                                if self.judge_type == 'p':
                                    data.judges.perfect += 1
                                else:
                                    data.judges.good += 1
                                    if data.judges.judge_type > 1:
                                        data.judges.judge_type = 1
                    if self.type == 2:
                        return True
            if time > self.time + 0.22 and (not self.is_judge) and not self.is_miss:
                if not self.is_fake:
                    self.miss()
                    if self.type != 2:
                        return True
            if self.type != 2:
                if self.is_judge:
                    self.x = linex + math.cos(math.radians(linerot)) * (self.x_position)
                    self.y = liney + math.sin(math.radians(linerot)) * (self.x_position)
                    if self.y_offset != 0:
                        self.x += math.cos(math.radians(linerot + 90)) * self.y_offset
                        self.y += math.sin(math.radians(linerot + 90)) * self.y_offset
                    if self.judge_type == 'b':
                        self.miss()
                    return True
            if self.type == 2 and self.is_judge and not self.is_miss and not self.judgeed:
                if not self.is_fake:
                    if not keys:
                        self.miss()

        self.x = linex + math.cos(math.radians(linerot)) * (self.x_position)
        self.y = liney + math.sin(math.radians(linerot)) * (self.x_position)
        if self.y_control:
            self.ycontrol_y, self.ycontrol_index = self.update_control(self.y_control, self.now_fp + self.y_offset_n, self.ycontrol_index)
        if self.type == 2:
            _l = self.end_r_fp - self.r_fp
            self.endx = self.x + math.cos(math.radians(linerot + 90)) * ((self.r_fp + self.y_offset) * self.ycontrol_y + _l)
            self.endy = self.y + math.sin(math.radians(linerot + 90)) * ((self.r_fp + self.y_offset) * self.ycontrol_y + _l)
        self.x += math.cos(math.radians(linerot + 90)) * ((self.r_fp + self.y_offset) * self.ycontrol_y)
        self.y += math.sin(math.radians(linerot + 90)) * ((self.r_fp + self.y_offset) * self.ycontrol_y)

        if self.alpha_control:
            self.acontrol_a, self.acontrol_index = self.update_control(self.alpha_control, self.now_fp + self.y_offset_n, self.acontrol_index)

        if self.type == 2:
            x1 = self.x-WINDOW_WIDTH/2
            y1 = self.y-WINDOW_HEIGHT/2
            x2 = self.endx-WINDOW_WIDTH/2
            y2 = self.endy-WINDOW_HEIGHT/2
            if (is_intersection((self.x,self.y),math.radians(linerot), WINDOW_WIDTH, WINDOW_HEIGHT) or is_intersection((self.endx,self.endy),math.radians(linerot), WINDOW_WIDTH, WINDOW_HEIGHT)):
                r = False
            else:
                if ((-x1<0 and x2<0) or (-x1>0 and x2>0)) or ((-y1<0 and y2<0) or (-y1>0 and y2>0)):
                    r = False
                else:
                    r = True
        else:
            r = not is_intersection((self.x,self.y),math.radians(linerot), WINDOW_WIDTH, WINDOW_HEIGHT)

        if r:
            x2 = self.x + math.cos(math.radians(linerot + 90)) * self.is_above
            y2 = self.y + math.sin(math.radians(linerot + 90)) * self.is_above
            d = math.sqrt((self.x-WINDOW_WIDTH/2)**2+(self.y-WINDOW_HEIGHT/2)**2)
            d2 = math.sqrt((x2-WINDOW_WIDTH/2)**2+(y2-WINDOW_HEIGHT/2)**2)
            if d2 > d:
                return 0
            return

        if self.type != 2:
            if not ((-NOTE_WIDTH <= self.x <= WINDOW_WIDTH + NOTE_WIDTH) and (-NOTE_WIDTH <= self.y <= WINDOW_HEIGHT + NOTE_WIDTH)):
                return

        if (math.ceil((self.now_end_fp + self.y_offset_n if self.type == 2 else self.now_fp + self.y_offset_n)) < 0 and iscover and (time <= self.time)):
            return
        if not render_note:
            return
        if time < self.visible_time:
            return
        self.draw(self.x, self.y, self.endx, self.endy, linerot, scale_on_notes, scalex, time)

    def get_xclip(self, texture: Texture, x, xmin, xmax, scale):
        s = texture.width * scale / 2
        if x + s > xmax:
            c = 1 - (x + s - xmax) / (texture.width * scale)
            if c <= 0:
                return None
            return ((0, 0), (c, 0), (c, 1), (0, 1))
        elif x - s < xmin:
            c = (xmin - (x - s)) / (texture.width * scale)
            if c > 1:
                return None
            return ((c, 0), (1, 0), (1, 1), (c, 1))
        else:
            return ((0, 0), (1, 0), (1, 1), (0, 1))

    def judge(self, time_offset, time):
        self.click = True
        if time_offset <= 0.08:
            self.judge_type = 'p'
        elif time_offset <= 0.16:
            self.judge_type = 'g'
        else:
            self.judge_type = 'b'
        self.is_judge = True
        if self.judge_type != 'b':
            self.hitsound.play()
        if self.type != 2:
            data.judges.combo += 1
            if self.judge_type == 'p':
                data.judges.perfect += 1
            elif self.judge_type == 'g':
                data.judges.good += 1
                if data.judges.judge_type > 1:
                    data.judges.judge_type = 1
            elif self.judge_type == 'b':
                data.judges.bad += 1
                if data.judges.judge_type > 0:
                    data.judges.judge_type = 0
        else:
            if time < self.time-0.08:
                self.play_hit = True

    def miss(self):
        data.judges.miss += 1
        data.judges.combo = 0
        self.is_miss = True
        if data.judges.judge_type > 0:
            data.judges.judge_type = 0

    def draw(self, x, y, endx, endy, rot, scale_on_notes, scalex, time):
        if self.alpha > 0:
            a = (1 if AUTOPLAY else ((linear(time-self.time, 0, 0.16, 1, 0) if time-self.time > 0 else 1) if time-self.time < 0.16 else 0))
            scale = self.size
            if scale_on_notes == 1:
                scale *= scalex
            if scale_on_notes == 2:
                xmax = scalex/2
                xmin = -scalex/2
                if self.type == 2:
                    clip = self.get_xclip(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], self.x_position, xmin, xmax, self.scale * scale)
                    if not clip is None:
                        draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], x, y, self.scale * scale, self.yscale * self.length * self.speed * self.is_above, rot, self.alpha * (0.5 if self.is_miss else 1) * self.acontrol_a, (0.5,0), self.tint, clip, xoffset = X_OFFSET)
                    if time < self.time:
                        if not clip is None:
                            draw_texture(NOTE_TEXTURES[4 + self.is_hl * 6], x, y, self.scale * scale, self.scale * self.is_above, rot, self.alpha * self.acontrol_a, (0.5,1), self.tint, clip, xoffset = X_OFFSET)
                    if not clip is None:
                        draw_texture(NOTE_TEXTURES[5 + self.is_hl * 6], endx, endy, NOTE_SCALE * scale, NOTE_SCALE * self.is_above, rot, self.alpha * (0.5 if self.is_miss else 1) * self.acontrol_a, (0.5,0), self.tint, clip, xoffset = X_OFFSET)
                else:
                    clip = self.get_xclip(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], self.x_position, xmin, xmax, NOTE_SCALE * scale)
                    if not clip is None:
                        draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], x, y, NOTE_SCALE * scale, NOTE_SCALE, rot, self.alpha * a * self.acontrol_a, (0.5,0.5), self.tint, clip, xoffset = X_OFFSET)
            else:
                if self.type == 2:
                    draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], x, y, self.scale * scale, self.yscale * self.length * self.speed * self.is_above, rot, self.alpha * (0.5 if self.is_miss else 1) * self.acontrol_a, (0.5,0), self.tint, xoffset = X_OFFSET)
                    if time < self.time:
                        draw_texture(NOTE_TEXTURES[4 + self.is_hl * 6], x, y, self.scale * scale, self.scale * self.is_above, rot, self.alpha * self.acontrol_a, (0.5,1), self.tint, xoffset = X_OFFSET)
                    draw_texture(NOTE_TEXTURES[5 + self.is_hl * 6], endx, endy, NOTE_SCALE * scale, NOTE_SCALE * self.is_above, rot, self.alpha * (0.5 if self.is_miss else 1) * self.acontrol_a, (0.5,0), self.tint, xoffset = X_OFFSET)
                else:
                    draw_texture(NOTE_TEXTURES[self.type - 1 + self.is_hl * 6], x, y, NOTE_SCALE * scale, NOTE_SCALE, rot, self.alpha * a * self.acontrol_a, (0.5,0.5), self.tint, xoffset = X_OFFSET)

class Hit:
    def __init__(self, x, y, startTime, color):
        self.x = x
        self.y = y
        self.start_time = startTime
        self.now_time = self.start_time
        self.p = 0
        self.hit_i = 0
        self.rot = tuple(math.radians(random.uniform(0, 360)) for i in range(4))
        self.distance = tuple(random.uniform(135, 165) * WIDTH_SCALE for i in range(4))
        self.color = color

    def update(self, time):
        self.now_time = time - self.start_time
        self.p = self.now_time / 0.5
        self.hit_i = max(min(math.floor(self.p * 29), 29), 0)
        if self.now_time > 0.545 or self.now_time < 0:
            return True
        self.draw()

    def draw(self):
        if self.p <= 1:
            draw_texture(HIT_TEXTURES[self.hit_i], self.x, self.y, HIT_SCALE, HIT_SCALE, 0, 1, (0.5, 0.5), self.color, xoffset = X_OFFSET)
        n = 0
        for r, d in zip(self.rot, self.distance):
            p = self.p - n * 0.03
            if p >= 0 and p <= 1:
                px = self.x + math.cos(r) * d * particle_easing(p)
                py = self.y + math.sin(r) * d * particle_easing(p)
                a = 1 - p
                size = PARTICLE_SIZE * (((0.2078 * p - 1.6524) * p + 1.6399) * p + 0.4988)
                draw_rect(px, py, size, size, 0, a, (0.5, 0.5), self.color, xoffset = X_OFFSET)
            n += 1