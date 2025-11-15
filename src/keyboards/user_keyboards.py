from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.database.models import Tariff, Instruction
from src.config import settings


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


back_to_balance_page_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отменить", callback_data="back_to_balance_page")]
])


def tariffs_btn(other_tariffs: List[Tariff], back_btn: bool=False):
    btns =[]
    for tariff in other_tariffs:
        btns.append([InlineKeyboardButton(text=tariff.name, callback_data=f"user_buy_{tariff.id}")])
    btns.append([InlineKeyboardButton(text="✍🏻 Свою сумму", callback_data="user_buy_main")])
    if back_btn is True:
        btns.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_balance_page")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def balance_keyboard(balance: int, user_channel_status: bool) -> InlineKeyboardMarkup:
    btns = []

    btns.append([InlineKeyboardButton(text="💰 Пополнить", callback_data="balance_plus")])
    if balance >= 100:
        btns.append([InlineKeyboardButton(text="💸 Вывести", callback_data="balance_give")])
    if user_channel_status == False:
        btns.append([InlineKeyboardButton(text="💰 Получить 100 рублей", url=settings.CHANNEL_LINK)])

    return InlineKeyboardMarkup(inline_keyboard=btns)


def pay_btn(pay_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 CryptoPay", callback_data=f"end_pay_crypto_{pay_id}")],
        [InlineKeyboardButton(text="⭐️ TG Stars", callback_data=f"end_pay_stars_{pay_id}")],
        [InlineKeyboardButton(text="☁️ Wata", callback_data=f"end_pay_wata_{pay_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="balance_plus")]
    ])


def pay_link_btn(link: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплатить", url=link)],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="balance_plus")]
    ])

def instructions_btn(instructions: List[Instruction]):
    btns = []
    for instruction in instructions:
        btns.append(
            [InlineKeyboardButton(text=instruction.value, callback_data=f"instruction_{instruction.id}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=btns)


def withdrawal_btn(withdrawal_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Подтвердить", callback_data=f"withdrawal_answer_yes_{withdrawal_id}")],
        [InlineKeyboardButton(text="🔴 Отклонить", callback_data=f"withdrawal_answer_no_{withdrawal_id}")]
    ])