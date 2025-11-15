import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, ContentType
from aiogram.fsm.context import FSMContext

from src.keyboards.user_keyboards import balance_keyboard, tariffs_btn, cancel_buy_btn, pay_btn, pay_link_btn, back_to_balance_page_btn, withdrawal_btn
from src.utils.helpers import safe_answer, try_edit_callback, delete_state_message, create_invoice_crypto_pay, pay_process
from src.database.repositories import UserRepository, SettingsRepository, TariffRepository, PayRepository, InstructionRepository, WithdrawalsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.states import UserStates
from src.config import settings

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
        balance=referral_rub,
        user_channel_status=user_info.has_channel_bonus
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
        "💰 <b>Меню приобретения</b>\n"
        "Выберите тариф для приобретения"
    )
    other_tariffs = await TariffRepository.give_other_tariffs(
        async_session=session
    )
    btn = tariffs_btn(
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
            f"     ● Название тарифа: {tariff_info.name}\n"
            f"     ● Стоимость тарифа: {tariff_info.price_cents/100}\n"
            f"     ● Количество дней по тарифу: {tariff_info.days}\n"
            f"Выберите метод оплаты"
        )
        day_price = int(await SettingsRepository.get_daily_cost_cents(
            async_session=session
        ))
        result_day_price = day_price * 100
        amount_cents = result_day_price * tariff_info.days
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
    
    cents_payment = input_pay_sum * 100
    pay_id = await PayRepository.add_payment(
            async_session=session,
            user_id=user_id,
            tariff_id=None,
            amount_cents=cents_payment
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
async def end_pay_page(callback: CallbackQuery, session: AsyncSession):
    pay_system = callback.data.split("_")[2]
    pay_id = int(callback.data.split("_")[3])

    pay_info = await PayRepository.get_pay(
        async_session=session,
        pay_id=pay_id
    )
    amount_rub = pay_info.amount_cents / 100
    if pay_system == "crypto":
        link = await create_invoice_crypto_pay(
            callback=callback,
            pay_id=pay_id,
            amount=amount_rub / settings.USDT_COURSE
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
    elif pay_system == "stars":
        pay_to_usdt = amount_rub / settings.USDT_COURSE
        prices = [LabeledPrice(label="Пополнение баланса", amount=pay_to_usdt)] 
        await callback.bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Покупка тестового товара",
            description="Оплата 1 звездой за цифровой товар",
            payload=pay_id, 
            provider_token="",  
            currency="XTR",
            prices=prices,
            need_name=False, 
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False  
        )
    
@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: Message, session: AsyncSession):
    payload = message.successful_payment.invoice_payload
    payment_info = message.successful_payment
    if payload.startswith("payment_id:"):
        pay_id = int(payload.split(":")[1])
            
        pay_info = await PayRepository.get_pay(
            async_session=session,
            pay_id=pay_id
        )
        result_amount = pay_info.amount_cents / 100

        await PayRepository.payment_update_sum(
            async_session=session,
            buy_id=pay_id,
            new_value=pay_info.amount_cents
        )
        await pay_process(
            session=session,
            pay_id=pay_id,
            amount=result_amount,
            bot=message.bot
        )
        await session.commit()
        await message.bot.send_message(message.chat.id, "Платёж успешно завершён!")
    else:
        # Обработка ошибок
        pass
    await message.answer(f"Оплата прошла! ID платежа: {payment_info.telegram_payment_charge_id}. Вот твой товар.")
    

@router.callback_query(F.data.startswith("instruction_"))
async def instruction_page(callback: CallbackQuery, session: AsyncSession):
    instruction_id = int(callback.data.split("_")[1])
    instruction = await InstructionRepository.get_buy_id(
        async_session=session,
        id=instruction_id
    )

    await try_edit_callback(
        callback=callback,
        text=instruction.description
    )


@router.callback_query(F.data == "balance_give")
async def balance_give_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user_id = callback.from_user.id
    user_info = await UserRepository.give_user(
        async_session=session,
        user_id=user_id
    )
    if user_info.referral_balance / 100 >= 100:
        txt = "❌ Минимальная сумма баланса 100 рублей"
        await callback.answer(
            text=txt
        )
        return
    txt = "✍🏻 Введите сумму для вывода"
    btn = back_to_balance_page_btn
    mes_del = await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
    await state.update_data(
        mes_del=mes_del.message_id
    )
    await state.set_state(
        UserStates.give_money_sum
    )


@router.message(UserStates.give_money_sum)
async def balance_give_sum_page(message: Message, session: AsyncSession, state: FSMContext):
    await delete_state_message(
        state=state,
        message=message
    )
    btn = back_to_balance_page_btn
    try:
        sum = int(message.text)
    except:
        txt = "❌ Введите сумму в виде числа"
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return
    txt = "💬 Введите номер карты"
    mes_del = await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTM:"
    )
    await state.update_data(
        mes_del=mes_del.message_id,
        sum=sum
    )
    await state.set_state(
        UserStates.give_money_card
    )


@router.message(UserStates.give_money_card)
async def balance_give_card_page(message: Message, session: AsyncSession, state: FSMContext):
    state_info = await delete_state_message(
        state=state,
        message=message
    )
    await state.clear()
    btn = back_to_balance_page_btn
    try:
        card = int(message.text)
    except:
        txt = "❌ Введите сумму в виде числа"
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return
    sum = state_info.get('sum') / 100
    user_id = message.from_user.id
    withdrawal_id = await WithdrawalsRepository.add_withdrawal(
        async_session=session,
        user_id=user_id,
        card_number=card,
        amount_cents=sum
    )
    btn = withdrawal_btn(
        withdrawal_id=withdrawal_id
    )
    txt = (
        "Заявка на вывод средств:\n\n"
        f"Сумма: {state_info.get('sum')}\n"
        f"Номер карты: {card}"
    )
    await message.bot.send_message(
        chat_id=settings.GROUP_ID,
        text=txt
    )