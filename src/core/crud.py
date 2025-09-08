from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Unit
from src.utils.constants import (
    BASE_AGILITY,
    BASE_FREEPOINT,
    BASE_HP,
    BASE_INTELLIGENCE,
    BASE_POINT,
    BASE_STRENGTH,
)
from src.utils.scripts import (
    CREATE_USER_SCRIPT, GET_USER_SCRIPT, SET_STATS_SCRIPT)


class CRUDBase:

    async def create_user(
        self,
        user_id: int,
        user_name: str,
        session: AsyncSession,
    ) -> dict | None | False:
        """Метод для создания пользователя."""
        query = text(CREATE_USER_SCRIPT)
        try:
            result = await session.execute(query, {
                "user_id": user_id,
                "user_name": user_name,
                "hp": BASE_HP,
                "strength": BASE_STRENGTH,
                "agility": BASE_AGILITY,
                "intelligence": BASE_INTELLIGENCE,
                "point": BASE_POINT,
                "free_point": BASE_FREEPOINT,
            })
            inserted_id = result.scalar_one_or_none()
            await session.commit()
            return inserted_id is not None
        except SQLAlchemyError:
            await session.rollback()
            return False

    async def get_user(
        self, user_id: int, session: AsyncSession,
    ) -> dict | bool | None:
        """Метод для получения пользователя."""
        query = text(GET_USER_SCRIPT)
        try:
            result = await session.execute(query, {'user_id': user_id})
            row = result.mappings().first()
            if row is None:
                return None
            return dict(row)
        except SQLAlchemyError:
            return False

    async def set_stats(
        self,
        user_id: int,
        strength: int,
        agility: int,
        intelligence: int,
        session: AsyncSession,
    ) -> bool:
        """Метод для установки характеристик."""
        query = text(SET_STATS_SCRIPT)
        try:
            await session.execute(query, {
                'user_id': user_id,
                'added_strength': strength,
                'added_agility': agility,
                'added_intelligence': intelligence,
                'summ_stats': strength + agility + intelligence,
            })
            await session.commit()
            # return result.rowcount > 0
            return True
        except SQLAlchemyError:
            return False


unit_crud = CRUDBase()
