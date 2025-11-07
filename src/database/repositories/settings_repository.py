from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from datetime import datetime

from src.database.models import SystemSetting
from src.config import settings


class SettingsRepository:

    @staticmethod
    async def init_default_settings(async_session: AsyncSession):
        for key, default_value in settings.DEFAULTS.items():
            result = await async_session.execute(
                select(SystemSetting).where(SystemSetting.key == key)
            )
            exists = result.scalar_one_or_none()

            if not exists:
                description = settings.DESCRIPTIONS.get(key, " ")
                setting = SystemSetting(
                    key=key,
                    value=default_value,
                    description=description
                )
                async_session.add(setting)

        await async_session.commit()


    @staticmethod
    async def get_daily_cost_cents(async_session: AsyncSession) -> int:
        result = await async_session.execute(
            select(SystemSetting.value)
            .where(SystemSetting.key == "daily_cost_cents")
        )
        value_str = result.scalar_one_or_none()
        if value_str is None:
            raise ValueError("Настройка daily_cost_cents not create!")
        return int(value_str)
    
    @staticmethod
    async def update_settings_info(async_session: AsyncSession, key: str, value: str):
        now = datetime.now()
        await async_session.execute(
            update(SystemSetting)
            .where(
                SystemSetting.key == key
            )
            .values(
                value = value,
                updated_at = now
            )
        )