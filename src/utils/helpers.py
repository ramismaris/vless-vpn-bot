import logging
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


async def safe_answer(message: Message, text: str, reply_markup=None, **kwargs):
    """Безопасная отправка сообщения"""
    try:
        return await message.answer(
            text=text, 
            reply_markup=reply_markup, 
            **kwargs
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        try:
            # Попробуем отправить без разметки
            return await message.answer(text=text, **kwargs)
        except Exception as e2:
            logger.error(f"Критическая ошибка отправки сообщения: {e2}")
            return None


async def try_edit_callback(callback: CallbackQuery, text: str, reply_markup=None, **kwargs):
    """Попытка редактирования сообщения из callback"""
    try:
        return await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        try:
            await callback.message.delete()
        except:
            pass
        return await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
            **kwargs
        )


async def try_delete_message(message: Message):
    """Попытка удаления сообщения"""
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")


def format_price(price: float) -> str:
    """Форматирование цены"""
    if price == int(price):
        return f"{int(price)} ₽"
    return f"{price:.2f} ₽"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезка текста с троеточием"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..." 