from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.database.models import Tariff


user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Получить доступ")],
        [KeyboardButton(text="🔑 Мой ключ"), KeyboardButton(text="💰 Оплатить")],
        [KeyboardButton(text="💼 Баланс"), KeyboardButton(text="🆘 Помощь")],
        [KeyboardButton(text="👨‍💼 Пригласить друга")]
    ],
    is_persistent=True,
    resize_keyboard=True
)


cancel_buy_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="balance_plus")]
])


def tariffs_btn(other_tariffs: List[Tariff], back_btn: bool=False):
    btns =[]
    for tariff in other_tariffs:
        btns.append([InlineKeyboardButton(text=tariff.name, callback_data=f"user_buy_{tariff.id}")])
    btns.append([InlineKeyboardButton(text="✍🏻 Свою сумму", callback_data="user_buy_main")])
    if back_btn is True:
        btns.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_balance_page")])
    return ReplyKeyboardMarkup(keyboard=btns)


def balance_keyboard(balance: int) -> InlineKeyboardMarkup:
    btns = []

    btns.append([InlineKeyboardButton(text="💰 Пополнить", callback_data="balance_plus")])
    if balance >= 100:
        btns.append([InlineKeyboardButton(text="💸 Вывести", callback_data="balance_give")])

    return InlineKeyboardMarkup(inline_keyboard=btns)


def pay_btn(pay_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 CryptoPay", callback_data=f"end_pay_crypto_{pay_id}")],
        [InlineKeyboardButton(text="⭐️ TG Stars", callback_data=f"end_pay_stars_{pay_id}")],
        [InlineKeyboardButton(text="☁️ Wata", callback_data=f"end_pay_wata_{pay_id}")]
        [InlineKeyboardButton(text="❌ Отменить", callback_data="balance_plus")]
    ])


def pay_link_btn(link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатить", url=link)]
        [InlineKeyboardButton(text="❌ Отменить", callback_data="balance_plus")]
    ])
