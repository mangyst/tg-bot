from dataclasses import dataclass


@dataclass
class Unit:
    user_id: int
    name: str
    STR: int = 5  # +урон и +EHP
    AGI: int = 5  # +точность(p_hit) и +EHP
    INT: int = 5  # +шанс и сила крита
    HP: int = 100   # базовое здоровье
    POINT: int = 15 # базовые поинты
    FREE_POINT: int = 3 # фри поинты
