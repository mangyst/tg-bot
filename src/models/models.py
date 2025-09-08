from dataclasses import dataclass, field

from src.utils.constants import (
    BASE_AGILITY,
    BASE_FREEPOINT,
    BASE_HP,
    BASE_INTELLIGENCE,
    BASE_POINT,
    BASE_STRENGTH,
)


@dataclass
class Unit:
    """Базовый класс юнита."""

    user_id: int
    name: str
    STR: int = field(default=BASE_STRENGTH)  # +урон и +EHP
    AGI: int = field(default=BASE_AGILITY)  # +точность(p_hit) и +EHP
    INT: int = field(default=BASE_INTELLIGENCE)  # +шанс и сила крита
    HP: int = field(default=BASE_HP, init=False)  # базовое здоровье
    POINT: int = field(default=BASE_POINT)  # базовые поинты
    FREE_POINT: int = field(default=BASE_FREEPOINT)  # свободные поинты
