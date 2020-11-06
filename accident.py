from dataclasses import dataclass

@dataclass
class ACCIDENT:
    """Class for an accident."""
    acc_id: int
    date: str
    visibility: str
    light: str
    road_conditions: str
    fatalities: int
    inj_index: float
