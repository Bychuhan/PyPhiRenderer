from dataclasses import dataclass

@dataclass
class Judge:
    perfect: int
    good: int
    bad: int
    miss: int
    combo: int
    score: float
    max_combo: int
    acc: float
    judge_type: int

judges = Judge(0, 0, 0, 0, 0, 0, 0, 1, 2)
