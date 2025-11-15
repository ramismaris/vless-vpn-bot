from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from datetime import datetime

from src.database.models import Withdrawal


class WithdrawalsRepository:

    @staticmethod
    async def get_on_id(async_session: AsyncSession, withdrawal_id: int):
        result = await async_session.execute(
            select(Withdrawal)
            .where(
                Withdrawal.id == withdrawal_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_withdrawal(async_session: AsyncSession, user_id: int, amount_cents: int, card_number: int) -> int:
        new_withdrawal = Withdrawal(
            user_id=user_id,
            amount_cents=amount_cents,
            card_number=card_number
        )
        async_session.add(
            new_withdrawal
        )
        await async_session.flush()
        return new_withdrawal.id

    @staticmethod
    async def update_status(async_session: AsyncSession, withdrawal_id: int, new_status: str) -> int:
        await async_session.execute(
            update(Withdrawal)
            .where(
                Withdrawal.id == withdrawal_id
            )
            .values(
                status=new_status
            )
        )
       