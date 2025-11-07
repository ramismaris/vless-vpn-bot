from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union

from src.database.db import db


class AdminFilter(BaseFilter):
    """Фильтр для проверки прав администратора"""
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id
        admin_list = await db.get_admin_list()
        return user_id in admin_list 