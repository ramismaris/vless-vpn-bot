import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from src.keyboards.user_keyboards import user_menu, balance_keyboard, tariffs_btn
from src.utils.helpers import get_reflink, decode_payload
from src.database.repositories import UserRepository, SettingsRepository, TariffRepository

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession, state: FSMContext):
   
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    referrer_id = None
    args = message.text.split()
    try:
        if len(args) > 1:
            decoded_arg = await decode_payload(args[1])  
            referrer_id = int(decoded_arg)
            if referrer_id == user_id:
                referrer_id = None
    except:
        logging.info("decode_payload is none")

    await UserRepository.create_or_update_user(
       async_session=session,
       user_id=user_id,
       username=username,
       full_name=full_name,
       referrer_id=referrer_id
    )
    txt = (
        "👋 Добро пожаловать в бота для подключения vpn"
    )
    btn = user_menu
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.message(F.text == "🆘 Помощь")
@router.message(Command("help"))
async def help_command(message: Message, state: FSMContext):
    
    await state.clear()
    txt = (
        "ℹ️ Нужна помощь, или возникли вопросы?\n"
        "Обратитесь к <a href='https://google.com>администратору</a>"
    )
    btn = user_menu
    
    await message.answer(
        text=txt,
        reply_markup=btn
    )


@router.message(F.text == "💼 Баланс")
@router.message(Command("help"))
async def balance_command(message: Message, session: AsyncSession, state: FSMContext):

    await state.clear()
    user_id = message.from_user.id
    user_info = await UserRepository.give_user(
        async_session=session,
        user_id=user_id
    )
    cost_cent = await SettingsRepository.get_daily_cost_cents(
        async_session=session
    )
    daily_rub = cost_cent / 100
    main_rub = user_info.main_balance / 100
    referral_rub = user_info.referral_balance / 100

    if user_info.is_active and user_info.main_balance > 0:
        days_left = user_info.main_balance // cost_cent
        days_text = f"Осталось ~{days_left} дн." if days_left > 0 else "Менее 1 дня"
    else:
        days_text = "Подписка неактивна"

    txt = (
        "💰 <b>Ваш баланс</b>:\n\n"
        f"</b>Основной баланс:</b> {main_rub:.2f} ₽\n"
        f"→ Тратится на подписку: {daily_rub:.2f} ₽/день\n"
        f"→ {days_text}\n\n"
        f"<b>Реферальный баланс:</b> {referral_rub:.2f} ₽\n"
        f"→ Только для вывода (мин. 100 ₽)\n\n"
    )
    btn = balance_keyboard(
        balance=referral_rub
    )
    
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.message(F.text == "👨‍💼 Пригласить друга")
@router.message(Command("add_friend"))
async def add_friend_command(message: Message, session: AsyncSession, state: FSMContext):
    user_id = message.from_user.id
    user_info = await UserRepository.give_user(
        async_session=session,
        user_id=user_id
    )
    user_friends = await UserRepository.get_user_friends(
        async_session=session,
        user_id=user_id
    )
    link = await get_reflink(
        user_id=user_id,
        bot=message.bot
    )
    txt = (
        "🔗 <b>Реферальная программа</b>\n\n"
        f"      ● Всего приглашено друзей: {len(user_friends)}\n"
        f"      ● Ваша реферальная ссылка: {link}"
    )
    btn = user_menu
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.message(F.text == "💰 Оплатить")
@router.message(Command("buy"))
async def buy_command(message: Message, session: AsyncSession, state: FSMContext):

    txt = (
        "💰 <b>Меню приобретения"
        "Выберите тариф для приобретения"
    )
    other_tariffs = TariffRepository.give_other_tariffs(
        async_session=session
    )
    btn = await tariffs_btn(
        other_tariffs=other_tariffs
    )
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
