from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, func
from datetime import datetime, timedelta

from src.database.models import Tariff, Payment


class TariffRepository:

    @staticmethod
    async def give_tariff(async_session: AsyncSession, tariff_id: int) -> Tariff:
        result = await async_session.execute(
            select(Tariff)
            .where(Tariff.id == tariff_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def give_other_tariffs(async_session: AsyncSession) -> Tariff:
        result = await async_session.execute(
            select(Tariff)
        )
        return result.scalars().all()
    

    @staticmethod
    async def add_tariff(async_session: AsyncSession, name: str, days: str, price_cents: str):
        new_tariff = Tariff(
            name=name,
            days=days,
            price_cents=price_cents
        )
        async_session.add(new_tariff)

    @staticmethod
    async def update_tariff_info(async_session: AsyncSession, agreement: str, value: int|str, tariff_id: int):
        column = getattr(Tariff, agreement)
        await async_session.execute(
            update(Tariff)
            .where(Tariff.id == tariff_id)
            .values({column: value})
        )