# 这个是去啊起飞写的。

import time

from pydub import AudioSegment
from const import *

import audio_utils

def summon(Chart,audio,output,format,path):
    if format == "phi":
        NoteClickAudios: dict[int, AudioSegment] = {
            1: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            2: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/drag.wav"),
            3: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            4: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/flick.wav"),
        }
    else:
        NoteClickAudios: dict[int, AudioSegment] = {
            1: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            2: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            3: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/flick.wav"),
            4: AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/drag.wav"),
        }

    ExtendedAudios: dict[str, AudioSegment] = {}

    if format == "rpe":
        for line in Chart["judgeLineList"]:
            for note in (line["notes"] if "notes" in line else []):
                if "hitsound_path" not in note: note["hitsound_path"] = None
                if note["hitsound_path"] is not None:
                    if note["hitsound_path"] in ExtendedAudios: continue
                    try:
                        ExtendedAudios[note["hitsound_path"]] = AudioSegment.from_file(f"{path}/{note["hitsound_path"]}")
                    except Exception as e:
                        print(f"Failed to load extended audio: {repr(e)}")
                        ExtendedAudios[note["hitsound_path"]] = AudioSegment.empty()

    delay = (Chart["offset"] if format == "phi" else Chart["META"]["offset"] / 1000)

    mainMixer = audio_utils.AudioMixer(AudioSegment.from_file(audio))
    if format == "phi":
        notesNum = sum(len(line["notesAbove"]) + len(line["notesBelow"]) for line in Chart["judgeLineList"])
    else:
        notesNum = sum(len(line["notes"]) if "notes" in line else 0 for line in Chart["judgeLineList"])

    getprogresstext = lambda n: f"\rprogress: {(n / notesNum * 100):.2f}%    {n}/{notesNum}"
    print_once = lambda n, end="": print((text := getprogresstext(n)) + " " * (maxlength - len(text)), end=end)
    maxlength = len(getprogresstext(notesNum))

    st = time.perf_counter()
    processed = 0
    printtime = 1 / 15
    lastprint = time.time() - printtime

    for line_index, line in enumerate(Chart["judgeLineList"]):
        if format == "phi":
            notes = (line["notesAbove"] + line["notesBelow"]) if (line["notesAbove"] and line["notesBelow"])else (line["notesAbove"] if line["notesAbove"] else line["notesBelow"])
        else:
            notes = (line["notes"] if "notes" in line else [])
        for note_index, note in enumerate(notes):
            nt = (note["time"] + delay if format == "phi" else note["startTime"] + delay)
            if format == "phi":
                mainMixer.mix(NoteClickAudios[note["type"]], nt)
            else:
                if not note["isFake"]:
                    mainMixer.mix(NoteClickAudios[note["type"]] if note["hitsound_path"] is None else ExtendedAudios[note["hitsound_path"]], nt)
            processed += 1
            
            if time.time() - lastprint >= printtime:
                print_once(processed)
                lastprint = time.time()

    print_once(processed, end="\n")
        
    print(f"Usage time: {(time.perf_counter() - st):.2f}s")
    print("Exporting...")
    mainMixer.get().export(output)
    print("Done.")