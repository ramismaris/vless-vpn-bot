import logging

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.db import async_session

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with async_session() as session:
            data['session'] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                await session.flush()
                logging.error(f"Ошибка в мидлваре: {e}")
                raise