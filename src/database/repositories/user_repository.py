from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, func
from datetime import datetime, timedelta

from src.database.models import User, Payment


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

    @staticmethod
    async def get_users_in_statistic(async_session: AsyncSession) -> dict:
        now = datetime.now()
        last_week = now - timedelta(days=7)

        total_users = select(func.count()).select_from(User)
        
        last_week_users = select(func.count()).select_from(
            select(User).where(User.created_at >= last_week).subquery()
        )
        total_sum = select(func.coalesce(func.sum(Payment.credited_cents), 0)).select_from(Payment)
        last_week_sum = select(
            func.coalesce(func.sum(Payment.credited_cents).filter(Payment.created_at >= last_week), 0)
        ).select_from(Payment)

        results = await async_session.execute(
            select(
                total_users.label("total_user"), 
                last_week_users.label("last_week_user"), 
                total_sum.label("total_sum"), 
                last_week_sum.label("last_week_sum")
            )
        )
        row = results.one()

        return {
        "total_users": row.total_user,
        "last_week_users": row.last_week_user,
        "total_sum": row.total_sum,
        "last_week_sum": row.last_week_sum,
    }
    

    @staticmethod
    async def give_other_users(async_session: AsyncSession):
        total_users = await async_session.execute(
            select(User)
        )
        return total_users.scalars().all()