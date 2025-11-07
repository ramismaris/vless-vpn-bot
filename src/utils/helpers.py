import logging
import asyncio
import openpyxl
from typing import List
from openpyxl.styles import Font, Alignment, PatternFill
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from datetime import datetime

from src.database.models import User

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


async def delete_state_message(state: FSMContext, message: Message) -> dict:
    state_info = await state.get_data()
    try:
        await message.bot.delete_messages(
            chat_id=message.from_user.id,
            message_ids=[
                state_info.get("mes_del"),
                message.message_id
            ]
        )
    except:
        logging.error("Error delete message in state")
    return state_info


async def answer_user_message(state_info: dict, bot: Bot, user_id: int):
    answer_users = []
    not_answer_users = []
    answer_btn = state_info.get("result_btn")
    res_type = state_info.get("res_type")
    text = state_info.get("text")
    photo = state_info.get("photo")
    
    try:
        if res_type == "text":
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML",
                reply_markup=answer_btn
            )
        else:
            await bot.send_photo(
                photo=photo,
                chat_id=user_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=answer_btn
            )
        answer_users.append(user_id)
    except:
        not_answer_users.append(user_id)
    await asyncio.sleep(0.2)


def export_users_to_excel(users: List[User]):
    filename = f'users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Пользователи"

    headers = [
        " ", "Айди пользователя", "Юзернейм пользователя", "Фулл нейм пользователя", "Дата регистрации",
        "Приглашен ли", "Баланс", "Реферальный баланс", "Активна ли подписка", "Ключ"
    ]

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
        cell.fill = PatternFill(start_color="E0E0E0", end_color="E0E0E0", fill_type="solid")

    for row_num, row_data in enumerate(users, 2):
        
        row_values = [
            row_num-1,
            row_data.user_id,
            row_data.username if row_data.username else "Отсутствует",
            row_data.full_name,
            row_data.created_at.strftime('%d.%m.%Y'),
            "Да" if row_data.referrer_id else "Нет",
            row_data.main_balance,
            row_data.referral_balance,
            "Да" if row_data.is_active else "Нет",
            row_data.vpn_key if row_data.vpn_key else "Отсутствует"
        ]

        for col_num, cell_value in enumerate(row_values, 1):
            ws.cell(row=row_num, column=col_num).value = cell_value

    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[column_letter].width = (max_length + 2) * 1.2

    wb.save(filename)
    return filename