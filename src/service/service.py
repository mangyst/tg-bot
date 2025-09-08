import random
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.crud import unit_crud
from src.models.models import Unit
from src.utils.constants import (
    BASE_CRIT_CHANGE,
    BASE_HIT_CHANGE,
    CHANCE_CRIT_INTELLIGENCE,
    CRIT_COEFFICIENT,
    DAMAGE_RESIST,
    EFFECT_INTELLIGENCE,
    EFFECT_STRANGTH,
    MAXIMUM_CRIT_CHANCE,
    MAX_HIT_CHANGE,
    MINIMUM_CRIT_CHANCE,
    MINIMUM_DAMAGE,
    MIN_HIT_CHANGE,
)

# =========================
# МАППИНГ СТАТОВ (кратко)
# =========================
# STR (Сила)      → +урон по врагу, +эффективная «толщина» (EHP)
# AGI (Ловкость)  → +шанс попасть, +шанс «жить дольше» (EHP через уклонения)
# INT (Интеллект) → +шанс крита и +сила крита; немного влияет на точность


def clamp_service(x, low, high) -> int:
    """Ограничение x в диапазоне [lo, hi]."""
    return max(low, min(high, x))


def expected_damage_service(att: Unit, deff: Unit) -> Tuple[float, dict]:
    """Возвращает ожидаемый урон одной атаки att → deff.
    Как статы влияют:
    - AGI_att ↑, AGI_def ↓ → p_hit ↑ (ловкость повышает точность/уклонение)
    - INT_att ↑, INT_def ↓ → p_hit ↑ слегка (интеллект об «решениях»/прицеле)
    - STR_att ↑, STR_def ↓ → base_dmg ↑ (сила как урон и «телесная» защита)
    - INT_att ↑            → p_crit ↑ и crit_mult ↑ (интеллект = криты)
    """
    # ---- ШАНС ПОПАСТЬ (AGI, INT влияют на точность/уклонение) ----
    p_hit = BASE_HIT_CHANGE + EFFECT_STRANGTH * (
        att.AGI - deff.AGI) + EFFECT_INTELLIGENCE * (
            att.INT - deff.INT)
    p_hit = clamp_service(p_hit, MIN_HIT_CHANGE, MAX_HIT_CHANGE)

    # ---- БАЗОВЫЙ УРОН (STR против STR-защиты) ----
    base_dmg = att.STR - DAMAGE_RESIST * deff.STR
    base_dmg = max(MINIMUM_DAMAGE, base_dmg)

    # ---- КРИТЫ (INT усиливает и шанс, и множитель) ----
    p_crit = clamp_service(
        BASE_CRIT_CHANGE + CHANCE_CRIT_INTELLIGENCE * att.INT,
        MINIMUM_CRIT_CHANCE,
        MAXIMUM_CRIT_CHANCE,
    )
    crit_mult = CRIT_COEFFICIENT + CHANCE_CRIT_INTELLIGENCE * att.INT

    # Средний множитель урона с учётом вероятности крита
    avg_mult = (1 - p_crit) * CHANCE_CRIT_INTELLIGENCE + p_crit * crit_mult

    # Итоговый ожидаемый урон одной атаки
    return base_dmg * p_hit * avg_mult, {
        "p_hit": p_hit,
        "base_dmg": base_dmg,
        "p_crit": p_crit,
        "crit_mult": crit_mult,
        "avg_mult": avg_mult,
    }


def effective_hp_service(u: Unit):
    """Эффективное здоровье (сколько, условно, «живёт» юнит).
    - AGI ↑ → повышает EHP через уклонение (каждая AGI даёт +2% EHP)
    - STR ↑ → повышает EHP через «толщину/стойкость» (каждая STR даёт +1% EHP)
    """
    return u.HP * (1 + 0.02 * u.AGI + 0.01 * u.STR)


def fight_with_log_service(u1: Unit, u2: Unit, rng=random):
    """Считает исход боя одним вычислением и возвращает подробный лог.
    Победитель — у кого выше «время жизни» (EHP),
    с учётом случайного фактора ±15% (апсет).
    """
    dmg1, meta1 = expected_damage_service(u1, u2)  # урон u1 → u2
    dmg2, meta2 = expected_damage_service(u2, u1)  # урон u2 → u1

    ehp1 = effective_hp_service(u1)  # Эффективное ХП первого юнита
    ehp2 = effective_hp_service(u2)  # Эффективное ХП второго юнита

    # Сколько «ударов»/итераций в среднем выдержит каждый
    time1 = ehp1 / max(1e-9, dmg2)
    time2 = ehp2 / max(1e-9, dmg1)

    # Случайный аспект: ±15% к итоговой выживаемости
    rnd1 = rng.uniform(0.85, 1.15)
    rnd2 = rng.uniform(0.85, 1.15)
    time1_adj = time1 * rnd1
    time2_adj = time2 * rnd2

    if time1_adj > time2_adj:
        winner = u1.name
    elif time2_adj > time1_adj:
        winner = u2.name
    else:
        winner = "Ничья"

    return winner


async def get_or_create_user_service(
    user_id: int,
    user_name: str,
    session: AsyncSession,
) -> Unit | None | False:
    user = await unit_crud.get_user(user_id, session=session)
    if user is False:
        return False

    if user is None:
        return await unit_crud.create_user(
            user_id=user_id,
            user_name=user_name,
            session=session,
        )
    return user


"""async def set_stats_service(user_id: int, user_name: str, s: int = 0, a: int = 0, i: int = 0) -> bool:
    user_id = int(user_id)
    user_name = str(user_name)
    user = await get_or_create_user_service(user_id=user_id, user_name=user_name)
    number_free = user.FREE_POINT
    summ_stats = s + a + i
    if summ_stats > number_free:
        return False
    result = await db.set_stats(user_id=user_id, s=s, a=a, i=i, summ_stats=summ_stats)
    if result:
        return True
    return False"""
