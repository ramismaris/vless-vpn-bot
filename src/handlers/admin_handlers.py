import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.filters.admin import AdminFilter
from src.keyboards.admin_keyboards import get_admin_keyboard
from src.database.db import db
from src.utils.helpers import safe_answer, try_edit_callback

logger = logging.getLogger(__name__)
router = Router()

# Применяем фильтр админа ко всем хендлерам
# router.message.filter(AdminFilter())
# router.callback_query.filter(AdminFilter())


@router.message(Command("admin"))
async def admin_command(message: Message):
    
    txt = (
        "👋 Добро пожаловать в админ панель бота"
    )
    btn = 
    
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
