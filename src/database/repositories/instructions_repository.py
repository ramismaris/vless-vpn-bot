from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from datetime import datetime
from typing import List

from src.database.models import Instruction
from src.config import settings


class InstructionRepository:

    @staticmethod
    async def get_other_instructions(async_session: AsyncSession) -> List[Instruction]:
        result = await async_session.execute(
            select(Instruction)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_buy_id(async_session: AsyncSession, id: int) -> Instruction:
        result = await async_session.execute(
            select(Instruction)
            .where(
                Instruction.id == id
            )
        )
        return result.scalar_one_or_none()