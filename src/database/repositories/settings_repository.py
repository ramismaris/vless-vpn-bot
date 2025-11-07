from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert

from src.database.models import SystemSetting


class SettingsRepository:

    @staticmethod
    async def get_daily_cost_cents(async_session: AsyncSession) -> int:
        result = await async_session.execute(
            select(SystemSetting.value).where(SystemSetting.key == "daily_cost_cents")
        )
        value_str = result.scalar_one_or_none()
        if value_str is None:
            raise ValueError("Настройка daily_cost_cents не установлена!")
        return int(value_str)