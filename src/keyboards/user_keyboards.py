from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


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


def balance_keyboard(balance: int) -> InlineKeyboardMarkup:
    
    btns = []

    btns.append([InlineKeyboardButton(text="💰 Пополнить", callback_data="balance_plus")])
    if balance >= 100:
        btns.append([InlineKeyboardButton(text="💸 Вывести", callback_data="balance_give")])
    
    
    return InlineKeyboardMarkup(inline_keyboard=btns)
