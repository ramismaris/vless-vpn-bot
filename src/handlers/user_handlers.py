import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.keyboards.user_keyboards import balance_keyboard, tariffs_btn, cancel_buy_btn, pay_btn, pay_link_btn
from src.utils.helpers import safe_answer, try_edit_callback, delete_state_message, create_invoice_crypto_pay
from src.database.repositories import UserRepository, SettingsRepository, TariffRepository, PayRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.states import UserStates

logger = logging.getLogger(__name__)
router = Router()



@router.callback_query(F.data == "back_to_balance_page")
async def back_to_balance_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
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
    
    await try_edit_callback(
        callback=callback,
        parse_mode="HTML",
        text=txt,
        reply_markup=btn
    )


@router.callback_query(F.data == "balance_plus")
async def balance_plus_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
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
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("user_buy_"))
async def user_buy_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_id = callback.from_user.id
    try:
        tariff_id = int(callback.data.split("_")[2])
        tariff_info = await TariffRepository.give_tariff(
            async_session=session,
            tariff_id=tariff_id
        )
        txt = (
            "<b>Выбранный вами тариф:</b>\n\n"
            f"     ● Название тарифа: {tariff_info.name}"
            f"     ● Стоимость тарифа: {tariff_info.price_cents/100}"
            f"     ● Количество дней по тарифу: {tariff_info.days}\n"
            f"Выберите метод оплаты"
        )
        day_price = int(await SettingsRepository.get_daily_cost_cents(
            async_session=session
        ))
        amount_cents = day_price * tariff_info.days
        pay_id = await PayRepository.add_payment(
            async_session=session,
            user_id=user_id,
            tariff_id=tariff_id,
            amount_cents=amount_cents
        )
        btn = pay_btn(
            pay_id=pay_id
        )
        await try_edit_callback(
            callback=callback,
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
    except:
        tariff_id = callback.data.split("_")[2]
        txt = "✍🏻 Введите сколько хотите внести"
        btn = cancel_buy_btn
    
        mes_del = await try_edit_callback(
            callback=callback,
            reply_markup=btn,
            parse_mode="HTML",
            text=txt
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        await state.set_state(
            state=UserStates.pay_sum
        )

    

@router.message(UserStates.pay_sum)
async def pay_sum_page(message: Message, session: AsyncSession, state: FSMContext):
    await delete_state_message(
        state=state,
        message=message
    )
    user_id = message.from_user.id
    try:
        input_pay_sum = int(message.text)
    except:
        txt = "❌ Введите сумму в виде числа"
        btn = cancel_buy_btn
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return
    
    pay_id = await PayRepository.add_payment(
            async_session=session,
            user_id=user_id,
            tariff_id=None,
            amount_cents=input_pay_sum
        )
    btn = pay_btn(
            pay_id=pay_id
        )
    txt = "✅ Выберите платежную систему"
    await state.clear()
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("end_pay_"))
async def end_pay_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    pay_system = callback.data.split("_")[2]
    pay_id = int(callback.data.split("_")[3])

    pay_info = await PayRepository.get_pay(
        async_session=session,
        pay_id=pay_id
    )
    if pay_system == "crypto":
        link = await create_invoice_crypto_pay(
            callback=callback,
            pay_id=pay_id,
            amount=pay_info.amount_cents
        )
        txt = "🔗 Ссылка для оплаты создана"
        btn = pay_link_btn(
            link=link
        )
        await try_edit_callback(
            callback=callback,
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )