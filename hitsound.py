from sys import argv
from json import load

from pydub import AudioSegment

from const import *

from log import *

def summon(Chart, audio, output, format):
    if format == "phi":
        NoteClickAudios = (
            None,
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/drag.wav"),
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/flick.wav"),
        )
    elif format == "rpe":
        NoteClickAudios = (
            None,
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/tap.wav"),
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/flick.wav"),
            AudioSegment.from_file(f"{RESOURCE_PATH}/sounds/hitsounds/drag.wav"),
        )
    ChartAudio:AudioSegment = AudioSegment.from_file(audio)
    ChartAudio_Length = ChartAudio.duration_seconds
    ChartAudio_Split_Audio_Block_Length = ChartAudio.duration_seconds * 1000 / 85 #ms
    ChartAudio_Split_Length = int(ChartAudio_Length / (ChartAudio_Split_Audio_Block_Length / 1000)) + 1
    ChartAudio_Split_Audio_List = [AudioSegment.silent(ChartAudio_Split_Audio_Block_Length + 500) for _ in [None] * ChartAudio_Split_Length]
    JudgeLine_cut = 0

    for JudgeLine in Chart["judgeLineList"]:
        Note_cut = 0
        if format == "phi":
            for note in JudgeLine["notesBelow"] + JudgeLine["notesAbove"]:
                try:
                    t = note["time"]
                    t_index = int(t / (ChartAudio_Split_Audio_Block_Length / 1000))
                    t %= ChartAudio_Split_Audio_Block_Length / 1000
                    seg: AudioSegment = ChartAudio_Split_Audio_List[t_index]
                    ChartAudio_Split_Audio_List[t_index] = seg.overlay(NoteClickAudios[note["type"]], t * 1000)
                    Note_cut += 1
                except IndexError:
                    pass
        elif format == "rpe":
            try:
                for note in [i for i in JudgeLine["notes"] if not i["isFake"]]:
                    n = len(note)
                    try:
                        t = note["startTime"]
                        t_index = int(t / (ChartAudio_Split_Audio_Block_Length / 1000))
                        t %= ChartAudio_Split_Audio_Block_Length / 1000
                        seg: AudioSegment = ChartAudio_Split_Audio_List[t_index]
                        ChartAudio_Split_Audio_List[t_index] = seg.overlay(NoteClickAudios[note["type"]], t * 1000)
                        Note_cut += 1
                    except IndexError:
                        pass
            except KeyError:
                pass
        JudgeLine_cut += 1

    print("Merge...")
    for i,seg in enumerate(ChartAudio_Split_Audio_List):
        if format == "phi":
            ChartAudio = ChartAudio.overlay(seg, i * ChartAudio_Split_Audio_Block_Length + Chart["offset"] * 1000)
        elif format == "rpe":
            ChartAudio = ChartAudio.overlay(seg, i * ChartAudio_Split_Audio_Block_Length + Chart["META"]["offset"])

    ChartAudio.export(output)

    print("Done.")