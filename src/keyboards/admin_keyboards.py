from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
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