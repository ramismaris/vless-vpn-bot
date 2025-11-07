from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert

from src.database.models import User


class UserRepository:

    @staticmethod
    async def give_user(async_session: AsyncSession, user_id: int) -> User:
        result = await async_session.execute(
            select(User)
            .where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()
    

    @staticmethod
    async def create_or_update_user(async_session: AsyncSession, user_id: int, username: str, full_name: str) -> User:
        user_info_on_base = await async_session.execute(
            select(User)
            .where(User.user_id == user_id)
        )
        user_info = user_info_on_base.scalar_one_or_none()
        if user_info:
            await async_session.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(
                    username=username
                )
            )
            return user_info
        
        await async_session.add(
            User(
                user_id=user_id,
                username=username,
                full_name=full_name
            )
        )