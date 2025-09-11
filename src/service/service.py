import random  # рандом для «апсета» (±15% к итоговой выживаемости)
from src.models.models import Unit
from aiogram import types

from src.repository.repository import Database
from src.core.config import DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD


db = Database(host=DATABASE_HOST,
              port=DATABASE_PORT,
              dbname=DATABASE_NAME,
              user=DATABASE_USER,
              password=DATABASE_PASSWORD)


# =========================
# МАППИНГ СТАТОВ (кратко)
# =========================
# STR (Сила)      → +урон по врагу, +эффективная «толщина» (EHP)
# AGI (Ловкость)  → +шанс попасть, +шанс «жить дольше» (EHP через уклонения)
# INT (Интеллект) → +шанс крита и +сила крита; немного влияет на точность (через p_hit)


def clamp_service(x, lo, hi):
    """Ограничение x в диапазоне [lo, hi]"""
    return max(lo, min(hi, x))


def expected_damage_service(att, deff) -> tuple:
    """
    Возвращает ОЖИДАЕМЫЙ УРОН одной атаки att → deff.
    Как статы влияют:
    - AGI_att ↑, AGI_def ↓ → p_hit ↑ (ловкость повышает точность/уклонение)
    - INT_att ↑, INT_def ↓ → p_hit ↑ слегка (интеллект об «решениях»/прицеле)
    - STR_att ↑, STR_def ↓ → base_dmg ↑ (сила как урон и «телесная» защита)
    - INT_att ↑            → p_crit ↑ и crit_mult ↑ (интеллект = криты)
    """

    # ---- ШАНС ПОПАСТЬ (AGI, INT влияют на точность/уклонение) ----
    p_hit = 0.70 + 0.02 * (att.AGI - deff.AGI) + 0.01 * (att.INT - deff.INT)
    p_hit = clamp_service(p_hit, 0.10, 0.95)  # не даём 0%/100%

    # ---- БАЗОВЫЙ УРОН (STR против STR-защиты) ----
    base_dmg = att.STR - 0.30 * deff.STR  # 30% силы защитника «гасит» урон
    base_dmg = max(1, base_dmg)                # минимальный урон = 1

    # ---- КРИТЫ (INT усиливает и шанс, и множитель) ----
    p_crit = clamp_service(0.05 + 0.01 * att.INT, 0.0, 0.50)  # 5% +1% за INT, максимум 50%
    crit_mult = 1.50 + 0.01 * att.INT               # базово ×1.5 +0.01 за INT

    # Средний множитель урона с учётом вероятности крита
    avg_mult = (1 - p_crit) * 1.0 + p_crit * crit_mult

    # Итоговый ожидаемый урон одной атаки
    return base_dmg * p_hit * avg_mult, {
        "p_hit": p_hit,
        "base_dmg": base_dmg,
        "p_crit": p_crit,
        "crit_mult": crit_mult,
        "avg_mult": avg_mult,
    }


def effective_hp_service(u) -> int:
    """
    Эффективное здоровье (сколько, условно, «живёт» юнит).
    - AGI ↑ → повышает EHP через уклонение (каждая AGI даёт +2% EHP)
    - STR ↑ → повышает EHP через «толщину/стойкость» (каждая STR даёт +1% EHP)
    """
    return u.HP * (1 + 0.02 * u.AGI + 0.01 * u.STR)


def fight_with_log_service(u1, u2, rng=random) -> bool | Unit:
    """
    Считает исход боя одним вычислением и возвращает подробный лог.
    Победитель — у кого выше «время жизни» (EHP) относительно входящего ДПС противника,
    с учётом случайного фактора ±15% (апсет).
    """

    dmg1, meta1 = expected_damage_service(u1, u2)  # урон u1 → u2
    dmg2, meta2 = expected_damage_service(u2, u1)  # урон u2 → u1

    ehp1 = effective_hp_service(u1)
    ehp2 = effective_hp_service(u2)

    # Сколько «ударов»/итераций в среднем выдержит каждый
    time1 = ehp1 / max(1e-9, dmg2)  # защита от деления на 0
    time2 = ehp2 / max(1e-9, dmg1)

    # Случайный аспект: ±15% к итоговой выживаемости
    rnd1 = rng.uniform(0.85, 1.15)
    rnd2 = rng.uniform(0.85, 1.15)
    time1_adj = time1 * rnd1
    time2_adj = time2 * rnd2

    if time1_adj > time2_adj:
        winner = u1
    elif time2_adj > time1_adj:
        winner = u2
    else:
        winner = False
    return winner


async def get_or_create_user_service(user_id: int, user_name: str) -> Unit | bool:
    user_id = int(user_id)
    user_name = str(user_name)
    result = await db.get_user(user_id)
    if result is None:
        result = await db.create_user(
            user_id=user_id,
            user_name=user_name,
            hp=100,
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
        HP=result.get('hp'),
        POINT=result.get('point'),
        FREE_POINT=result.get('free_point')
    )
    return unit


async def set_stats_service(user_id: int, user_name: str, s: int = 0, a: int = 0, i: int = 0) -> bool:
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
    return False


async def resset_stats_service(user_id: int) -> bool:
    user_id = int(user_id)
    result = await db.resset_stats(user_id=user_id)
    if result:
        return True
    return False


async def add_stats_service(user_id: int) -> bool:
    user_id = int(user_id)
    f_points = random.randint(0, 3)
    result = await db.add_stats(user_id=user_id, f_points=f_points)
    if result:
        return True
    return False
