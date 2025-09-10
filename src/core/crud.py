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
from src.utils.exceptions import (
    UserCreateError,
    UserOperationError,
    UserReadError,
)
from src.utils.scripts import (
    ADD_STATS_SCRIPTS,
    CREATE_USER_SCRIPT,
    GET_USER_SCRIPT,
    RESET_STATS_SCRIPT,
    SET_STATS_SCRIPT,
)


class CRUDBase:

    @staticmethod
    def dict_to_class(data: dict, user_id: int) -> Unit:
        """Метод для преобразования данных из БД в объект класса Unit."""
        return Unit(
            user_id,
            name=data['user_name'],
            STR=data['strength'],
            AGI=data['agility'],
            INT=data['intelligence'],
            POINT=data['point'],
            FREE_POINT=data['free_point'],
        )

    async def create_user(
        self,
        user_id: int,
        user_name: str,
        session: AsyncSession,
    ) -> Unit:
        """Метод для создания пользователя."""
        query = text(CREATE_USER_SCRIPT)
        try:
            await session.execute(query, {
                "user_id": user_id,
                "user_name": user_name,
                "hp": BASE_HP,
                "strength": BASE_STRENGTH,
                "agility": BASE_AGILITY,
                "intelligence": BASE_INTELLIGENCE,
                "point": BASE_POINT,
                "free_point": BASE_FREEPOINT,
            })
            await session.commit()
            return Unit(user_id=user_id, name=user_name)
        except SQLAlchemyError:
            await session.rollback()
            raise UserCreateError

    async def get_user(
        self, user_id: int, session: AsyncSession,
    ) -> Unit | None:
        """Метод для получения пользователя."""
        query = text(GET_USER_SCRIPT)
        try:
            result = await session.execute(query, {'user_id': user_id})
            row = result.mappings().first()
            if row is None:
                return None
            return self.dict_to_class(dict(row), user_id)
        except SQLAlchemyError:
            raise UserReadError

    async def set_stats(
        self,
        user_id: int,
        strength: int,
        agility: int,
        intelligence: int,
        session: AsyncSession,
    ) -> Unit | None:
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
            return await self.get_user(user_id, session)  # возвращаем обновленный объект
        except SQLAlchemyError:
            raise UserOperationError

    async def resset_stats(
            self, user_id: int, session: AsyncSession) -> bool:
        """Метод для сброса характеристик."""
        query = text(RESET_STATS_SCRIPT)
        try:
            result = await session.execute(query, {
                'user_id': user_id,
            })
            await session.commit()
            return result.rowcount > 0  # type: ignore
        except SQLAlchemyError:
            await session.rollback()
            raise UserOperationError

    async def add_stats(
            self, user_id: int, f_points: int, session: AsyncSession) -> bool:
        """Метод для добавления очков характеристик."""
        query = text(ADD_STATS_SCRIPTS)
        try:
            result = await session.execute(query, {
                'user_id': user_id,
                'f_point': f_points,
            })
            await session.commit()
            return result.rowcount > 0  # type: ignore
        except SQLAlchemyError:
            await session.rollback()
            raise UserOperationError


unit_crud = CRUDBase()
