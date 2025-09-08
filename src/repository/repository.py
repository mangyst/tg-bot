from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


class Database:
    def __init__(self, host, port, dbname, user, password):
        self.engine = create_async_engine(
            f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}',
            echo=False
        )
        self.async_session = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

# ОСУЖДАЮ ORM

    async def create_user(
            self,
            user_id: int,
            user_name: str,
            hp: int,
            strength: int,
            agility: int,
            intelligence: int,
            point: int,
            free_point: int
    ) -> bool:
        query = text("""
            INSERT INTO users_bot (user_id, user_name, hp, strength, agility, intelligence, point, free_point)
            VALUES (:user_id, :user_name, :hp, :strength, :agility, :intelligence, :point, :free_point)
            RETURNING user_id;
        """)
        async with self.async_session() as session:
            try:
                result = await session.execute(query, {
                    "user_id": user_id,
                    "user_name": user_name,
                    "hp": hp,
                    "strength": strength,
                    "agility": agility,
                    "intelligence": intelligence,
                    "point": point,
                    "free_point": free_point
                })
                inserted_id = result.scalar_one_or_none()
                await session.commit()
                return inserted_id is not None
            except SQLAlchemyError:
                await session.rollback()
                return False

    async def get_user(self, user_id: int) -> dict | bool | None:
        query = text("""
        SELECT 
            user_id,
            user_name,
            hp,
            strength,
            agility,
            intelligence,
            point,
            free_point
            FROM users_bot
            WHERE user_id = :user_id;
           """)
        async with self.async_session() as session:
            try:
                result = await session.execute(query, {'user_id': user_id})
                row = result.mappings().first()
                if row is None:
                    return None
                user = dict(row)
                return user
            except SQLAlchemyError as e:
                return False

    async def set_stats(self, user_id: int, s: int, a: int, i: int, summ_stats: int) -> bool:
        query = text("""
            UPDATE users_bot
            SET 
            strength = strength + :s,
            agility = agility + :a,
            intelligence = intelligence + :i,
            free_point = free_point - :summ_stats
            WHERE user_id = :user_id;
           """)
        async with self.async_session() as session:
            try:
                result = await session.execute(query, {
                    'user_id': user_id,
                    's': s,
                    'a': a,
                    'i': i,
                    'summ_stats': summ_stats
                })
                await session.commit()
                return result.rowcount > 0
            except SQLAlchemyError as e:
                await session.rollback()
                return False

    async def resset_stats(self, user_id: int) -> bool:
        query = text("""
            UPDATE users_bot
            SET 
            strength = 0,
            agility = 0,
            intelligence = 0,
            free_point = point
            WHERE user_id = :user_id;
           """)
        async with self.async_session() as session:
            try:
                result = await session.execute(query, {
                    'user_id': user_id,
                })
                await session.commit()
                return result.rowcount > 0
            except SQLAlchemyError as e:
                await session.rollback()
                return False

    async def add_stats(self, user_id: int, f_points: int) -> bool:
        query = text("""
            UPDATE users_bot
            SET 
            point = point + :f_point,
            free_point = free_point + :f_point
            WHERE user_id = :user_id;
           """)
        async with self.async_session() as session:
            try:
                result = await session.execute(query, {
                    'user_id': user_id,
                    'f_point': f_points
                })
                await session.commit()
                return result.rowcount > 0
            except SQLAlchemyError as e:
                await session.rollback()
                return False
