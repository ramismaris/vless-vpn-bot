from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from datetime import datetime

from src.database.models import Payment
from src.config import settings


class PayRepository:

    @staticmethod
    async def get_pay(async_session: AsyncSession, pay_id: int):
        result = await async_session.execute(
            select(Payment)
            .where(
                Payment.id == pay_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_payment(async_session: AsyncSession, user_id: int, tariff_id: int|None, amount_cents: int) -> int:
        new_pay = Payment(
            user_id=user_id,
            tariff_id=tariff_id,
            amount_cents=amount_cents
        )
        async_session.add(
            new_pay
        )
        await async_session.flush()
        return new_pay.id