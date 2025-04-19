from dataclasses import dataclass

@dataclass
class Judge:
    perfect: int
    good: int
    bad: int
    miss: int
    combo: int
    score: float

judges = Judge(0, 0, 0, 0, 0, 0)
