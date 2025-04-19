def fv12fv3(chart):
    for i in chart["judgeLineList"]:
        for n in i["judgeLineMoveEvents"]:
            n["start2"] = n["start"] % 1000 / 520
            n["end2"] = n["end"] % 1000 / 520
            n["start"] = (n["start"] - (n["start"] % 1000)) / 1000 / 880
            n["end"] = (n["end"] - (n["end"] % 1000)) / 1000 / 880