import json, os
from log import *
from func import *

def beat(beat):
    return beat[0] + beat[1] / beat[2]

def parse_chart(chart_path):
    try:
        with open(chart_path, "r", encoding="utf-8") as f:
            try:
                chart = json.load(f)
                if "META" in chart:
                    format = "rpe"
                elif "formatVersion" in chart:
                    format = "phi"
                else:
                    print("未知的谱面格式")
            except json.JSONDecodeError:
                format = "pec"
                chart = f.read()
                error_and_exit_no_tip("你来的真早！pec支持正在憋憋中，敬请谅解。/大怨种")

            path = os.path.dirname(chart_path)

            if format == "phi":
                import phi_objs
                formatVersion = chart["formatVersion"]
                BPMList = []
                if formatVersion == 1:
                    import fv12fv3
                    fv12fv3.fv12fv3(chart)
                offset = chart["offset"]
                judgeLineList = chart["judgeLineList"]
                lines = [phi_objs.JudgeLine(data) for data in judgeLineList]
                num_of_notes = 0
                for i in judgeLineList:
                    num_of_notes += len(i["notesAbove"])
                    num_of_notes += len(i["notesBelow"])
                attachUI = None
            if format == "rpe":
                import rpe_objs
                rpe_objs.LINE_TEXTURES = {}
                rpe_objs.NOTE_HITSOUNDS = {}
                rpe_objs.note_time_list = []
                rpe_objs.note_hl_time = []
                formatVersion = chart["META"]["RPEVersion"]
                offset = chart["META"]["offset"] / 1000
                judgeLineList = chart["judgeLineList"]
                BPMList = chart["BPMList"]
                for i in range(len(BPMList)):
                    if i == len(BPMList)-1:
                        BPMList[i]["endTime"] = 9999999999
                    else:
                        BPMList[i]["endTime"] = beat(BPMList[i+1]["startTime"])
                    BPMList[i]["startTime"] = beat(BPMList[i]["startTime"])
                _t = 0
                for i in BPMList:
                    i["time"] = _t + 60 / i["bpm"] * (i["endTime"] - i["startTime"])
                    _t == i["time"]
                lines = [rpe_objs.JudgeLine(data, BPMList) for data in judgeLineList]
                for i in lines:
                    if i.father != -1:
                        i.father_line = lines[i.father]
                attachUI = {"combo":None,"combonumber":None,"score":None,"name":None,"level":None,"pause":None,"bar":None}
                for i in lines:
                    if i.attach_ui != -1:
                        if i.attach_ui in attachUI:
                            attachUI[i.attach_ui] = i
                if formatVersion < 141:
                    attachUI["bar"] = None
                lines.sort(key = lambda x: x.z_order)
                num_of_notes = 0
                for i in judgeLineList:
                    if "notes" in i:
                        notes = [n for n in i["notes"] if n["isFake"] != 1]
                        num_of_notes += len(notes)
                notes = None
                if num_of_notes == 0:
                    num_of_notes = 114514
                rpe_objs.load_textures(lines, path)
                rpe_objs.load_hitsounds(lines, path)
            if format == "pec":
                # wtf bro
                chart = chart.split("\n")
                lines = []
                formatVersion = 114514
                offset = 0
                num_of_notes = 114514
                BPMList = []
                attachUI = {}
                for i in enumerate(chart):
                    if i[0] == 0:
                        offset = i[1]
                        continue
                    elif i[1] == "":
                        continue
                    data = i[1].split(" ")
                    if data[0] == "bp":
                        continue
                    if data[0][0] == "n" or data[0] == "#" or data[0] == "&":
                        continue
                    data[1] = int(data[1])
                    if len(lines)-1 < data[1]:
                        for i in range(data[1]+1-len(lines)):
                            lines.append({'cp':[],'cm':[],'cd':[],'cr':[],'ca':[],'cf':[],'cv':[],'n':[]})
            debug(f"Chart format | {format.upper()}({formatVersion})")
    except UnicodeDecodeError:
        error_and_exit_no_tip('你来的真早！二进制谱面支持正在憋憋中，敬请谅解。/大怨种')
    return lines, formatVersion, offset, num_of_notes, chart, format, BPMList, attachUI, path

def get_info(chart_path):
    try:
        path = os.path.dirname(chart_path)
        with open(chart_path, "r", encoding="utf-8") as f:
            chart = json.load(f)
            if "META" in chart:
                format = "rpe"
            elif "formatVersion" in chart:
                format = "phi"
            if format == "phi":
                return format, "", "", "", "", "", "", ""
            if format == "rpe":
                name = chart["META"]["name"]
                level = chart["META"]["level"]
                composer = chart["META"]["composer"]
                charter = chart["META"]["charter"]
                illustrator = (chart["META"]["illustration"] if "illustration" in chart["META"] else "null")
                music = f"{path}/{chart["META"]["song"]}"
                music = (music if os.path.exists(music) else None)
                ill = f"{path}/{chart["META"]["background"]}"
                ill = (ill if os.path.exists(ill) else None)
                return format, name, level, music, ill, composer, charter, illustrator
    except:
        return "", "", "", "", "", "", "", ""

def parse_extra(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            extra = json.load(f)
        except json.JSONDecodeError:
            error_and_exit_no_tip("extra不是json")

    file_path = os.path.dirname(path)

    effects = (extra["effects"] if "effects" in extra else [])
    video = (extra["videos"] if "videos" in extra else [])

    shaders = {}
    if effects:
        for i in effects:
            if i["shader"] not in shaders:
                if i["shader"][0] == "/":
                    shaders[i["shader"]] = get(f"{file_path}{i["shader"]}")
                else:
                    shaders[i["shader"]] = get(f".\\Resources\\shaders\\{i["shader"]}.glsl")
                #info(f"Loaded shader | {i["shader"]}")

    videos = {}
    if video:
        for i in video:
            if i["path"] not in shaders:
                videos[i["path"]] = f"{file_path}/{i["path"]}"
                #info(f"Loaded video | {i["path"]}")

    return shaders, videos

def parse_info(path):
    file_type = os.path.splitext(path)[1]
    file_path = os.path.split(path)[0]
    if file_type == '.yml':
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            f = yaml.load(f, Loader=yaml.FullLoader)
            return f"{file_path}\\{f['chart']}", f"{file_path}\\{f['music']}", f"{file_path}\\{f['illustration']}", f['name'], f['level'], f['composer'], f['charter'], f['illustrator']
    elif file_type == '.txt':
        with open(path, 'r', encoding='utf-8') as f:
            f = f.readlines()
            data = {}
            for i in f:
                i = i.replace('\n', '').split(': ')
                if len(i) > 1:
                    data[i[0]] = i[1]
            return f"{file_path}\\{data['Chart']}", f"{file_path}\\{data['Song']}", f"{file_path}\\{data['Picture']}", data['Name'], data['Level'], data['Composer'], data['Charter'], 'UK'
    elif file_type == '.csv':
        error_and_exit_no_tip('你来的真早！csv格式info支持正在憋憋中，敬请谅解。/大怨种')
    else:
        error_and_exit_no_tip('未知的info格式')