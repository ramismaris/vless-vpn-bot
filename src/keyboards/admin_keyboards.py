from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from src.database.models import Tariff
from src.config import settings


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_answer")],
    [InlineKeyboardButton(text="👨‍💼 База пользователей", callback_data="admin_base")],
    [InlineKeyboardButton(text="✍🏻 Редактор тарифов", callback_data="admin_tariffs_editor")]
])



editor_page_btns = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✒️ Редактировать тарифы", callback_data="tariffs_edit")],
    [InlineKeyboardButton(text="💰 Редактировать стоимость базового дня", callback_data="day_edit")],
    [InlineKeyboardButton(text="🏡 В админ меню", callback_data="back_to_admin_page")]
])


back_to_admin_page_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏡 В админ меню", callback_data="back_to_admin_page")]
])


cancel_correct_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="admin_tariffs_editor")]
])


back_to_tariffs_editor_page = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_tariffs_editor")]
])

cancel_tariffs_edit_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="tariffs_edit")]
])


def get_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔙 Админ меню", callback_data="back_to_admin")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 


answer_page_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Отправить", callback_data="answer_yes")],
    [InlineKeyboardButton(text="🔴 Переписать", callback_data="admin_answer")],
    [InlineKeyboardButton(text="🏠 В меню", callback_data="back_to_admin_page")]
])


def tariff_info_page_btn(tariff_id: int, status: str = "🔴 Отключить"):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✍🏻 Редактировать название", callback_data="info_page_name")],
    [InlineKeyboardButton(text="🗓️ Редактировать количество дней", callback_data="info_page_days")],
    [InlineKeyboardButton(text="💰 Редактировать цену", callback_data="info_page_price")],
    [InlineKeyboardButton(text=, callback_data="info_page_price")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="tariffs_edit")]
])


def address_pagination_btns(
        other_tariffs: List[Tariff], start_point: int, end_point: int, 
        now_point: int, total_pages: int
):
    btns = []
    for tariff in other_tariffs[start_point:end_point]:
        btns.append([InlineKeyboardButton(text=tariff.name, callback_data=f"edit_tariff_{tariff.id}")])
    
    if len(other_tariffs) > settings.PAGINATION_COUNT:
        btns.append([InlineKeyboardButton(text="⏪️", callback_data=f"pagination_tariff_back_{start_point}_{now_point}"),
                     InlineKeyboardButton(text=f"{now_point}/{total_pages}", callback_data=f"-"),
                     InlineKeyboardButton(text="⏩️", callback_data=f"pagination_tariff_front_{start_point}_{now_point}")
        ])
    btns.append([InlineKeyboardButton(text="➕ Добавить тариф", callback_data="add_tariff")])
    btns.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_tariffs_editor")])
    return InlineKeyboardMarkup(
        inline_keyboard=btns
    )