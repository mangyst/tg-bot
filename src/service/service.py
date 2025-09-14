from src.models.models import Unit
import random
from typing import Tuple

from src.repository.repository import Database
from src.core.config import DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD


db = Database(host=DATABASE_HOST,
              port=DATABASE_PORT,
              dbname=DATABASE_NAME,
              user=DATABASE_USER,
              password=DATABASE_PASSWORD)


def compare_units_service(
    a: Unit,
    b: Unit,
    clamp=None,
) -> Tuple[Unit, Unit, bool]:

    default_weight = 1.0

    rules = [
        ('STR', 'INT'),
        ('INT', 'AGI'),
        ('AGI', 'STR'),
        ('STR', 'STR'),
        ('AGI', 'AGI'),
        ('INT', 'INT')
    ]

    weights = {
        ('STR', 'INT'): 2.0,
        ('INT', 'AGI'): 2.0,
        ('AGI', 'STR'): 2.0
    }

    def pair_contrib(attacker: Unit, defender: Unit, atk_key: str, def_key: str) -> float:
        diff = getattr(attacker, atk_key) - getattr(defender, def_key)
        if clamp is not None:
            diff = max(-clamp, min(diff, clamp))
        return weights.get((atk_key, def_key), default_weight) * diff

    score_a = 0.0
    score_b = 0.0

    for atk_key, def_key in rules:
        score_a += pair_contrib(a, b, atk_key, def_key)
        score_b += pair_contrib(b, a, atk_key, def_key)

    margin = score_a - score_b
    if margin > 0:
        return a, b, True
    elif margin < 0:
        return b, a, True
    return a, b, False


async def get_or_create_user_service(user_id: int, user_name: str) -> Unit | bool:
    user_id = int(user_id)
    user_name = str(user_name)
    result = await db.get_user(user_id)
    if result is None:
        result = await db.create_user(
            user_id=user_id,
            user_name=user_name,
            strength=5,
            agility=5,
            intelligence=5,
            point=18,
            free_point=3
        )
        if result:
            return True

    if not result:
        return False

    unit = Unit(
        user_id=user_id,
        name=result.get('user_name'),
        STR=result.get('strength'),
        AGI=result.get('agility'),
        INT=result.get('intelligence'),
        POINT=result.get('point'),
        FREE_POINT=result.get('free_point'),
        LOSE=result.get('lose'),
        WIN=result.get('win')
    )
    return unit


async def set_stats_service(user_id: int, user_name: str, s: int = 0, a: int = 0, i: int = 0) -> bool:
    user_id = int(user_id)
    user_name = str(user_name)
    user = await get_or_create_user_service(user_id=user_id, user_name=user_name)
    number_free = user.FREE_POINT
    summ_stats = s + a + i
    if summ_stats > number_free or any((s < 0, a < 0, i < 0)):
        return False
    result = await db.set_stats(user_id=user_id, s=s, a=a, i=i, summ_stats=summ_stats)
    if result:
        return True
    return False


async def resset_stats_service(user_id: int) -> bool:
    user_id = int(user_id)
    result = await db.resset_stats(user_id=user_id)
    if result:
        return True
    return False


async def add_stats_service(user_id: int) -> Tuple[bool, int]:
    user_id = int(user_id)
    f_points = random.randint(0, 3)
    result = await db.add_stats(user_id=user_id, f_points=f_points)
    if result:
        return True, f_points
    return False, f_points


async def add_statistics_service(user_id: int, lose: int = 0, win: int = 0) -> bool:
    user_id = int(user_id)
    result = await db.add_statistics(user_id=user_id, f_lose=lose, f_win=win)
    if result:
        return True
    return False

