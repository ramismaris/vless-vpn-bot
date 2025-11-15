import logging
import asyncio
import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery, FSInputFile

from src.config import settings
from src.utils.states import AdminStates
from src.database.repositories import (
    UserRepository, SettingsRepository, TariffRepository, WithdrawalsRepository
)
from src.utils.helpers import (
    safe_answer, try_edit_callback, delete_state_message, answer_user_message,
    export_users_to_excel
)
from src.keyboards.admin_keyboards import (
    admin_menu, back_to_admin_page_btn, answer_page_btn, editor_page_btns,
    cancel_correct_btn, back_to_tariffs_editor_page, address_pagination_btns,
    cancel_tariffs_edit_btn, tariff_info_page_btn, cancel_tariff_edit_page
)

logger = logging.getLogger(__name__)
router = Router()

# router.message.filter(AdminFilter())
# router.callback_query.filter(AdminFilter())


@router.message(Command("admin"))
async def admin_command(message: Message, state: FSMContext):
    await state.clear()
    txt = (
        "👋 Добро пожаловать в админ панель бота"
    )
    btn = admin_menu
    
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_admin_page")
async def back_to_admin_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    txt = (
        "👋 Добро пожаловать в админ панель бота"
    )
    btn = admin_menu
    await try_edit_callback(
        callback=callback,
        reply_markup=btn,
        parse_mode="HTML",
        text=txt
    )


#=======================#STATISTIC#=======================#
@router.callback_query(F.data == "admin_stats")
async def admin_statistic_page(callback: CallbackQuery, session: AsyncSession):
    other_users = await UserRepository.get_users_in_statistic(
        async_session=session
    )
    txt = (
        "📊<b>Статистика:</b>\n\n"
        f"     ● Всего пользователей: {other_users.get('total_users')}\n"
        f"     ● Новые пользователи за неделю: {other_users.get('last_week_users')}\n"
        f"     ● Общая сумма пополнений: {other_users.get('total_sum') / 100}\n"
        f"     ● Пополнения за неделю: {other_users.get('last_week_sum') / 100}"
    )
    btn = back_to_admin_page_btn
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


#=======================#ANSWER#=======================#
@router.callback_query(F.data == "admin_answer")
async def admin_answer_page(callback: CallbackQuery, state: FSMContext):
    try:
        state_info = await state.get_data()

        await callback.bot.delete_message(
            chat_id=callback.from_user.id,
            message_id=state_info.get("mes_del")
        )
    except:
        pass

    await state.clear()
    txt = (
        "<b>✍🏻 Отправка рассылки</b>\n\n"
        "Напишите сообщение для рассылки в <b>1 сообщение</b>\n\n"
        "📋 <b>Поддерживаются такие форматы как: </b>\n"
        "   ● Только текст\n"
        "   ● Только фото\n"
        "   ● Фото + текст\n"
        "   ● HTML форматирование\n\n"
        "💡 <i>Сообщение будет отправлено всем пользователям бота</i>"
    )
    btn = back_to_admin_page_btn

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
        state=AdminStates.answer
    )


@router.message(AdminStates.answer)
async def text_answer_page(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.html_text

    await delete_state_message(
        message=message,
        state=state
    )

    if len(text) >= 900:
        txt = "❌ Слишком длинный текст, введите текст длинной не более 900 символов"
        btn = back_to_admin_page_btn
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return
    if message.photo:
        res_type = "photo"
        photo = message.photo[-1].file_id
        mes_del = await message.bot.send_photo(
            chat_id=user_id,
            caption=text,
            photo=photo
        )
    elif message.text:
        res_type = "text"
        photo = None
        mes_del = await message.answer(
            text=text
        )
    else:
        txt = "❌ Не распознанный формат, отправьте фото/текст/тест+фото"
        btn = back_to_admin_page
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return

    text = message.html_text
    btn = answer_page_btn
    txt = (
        "📋 Ваш текст:\n\n"
    )

    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
    await state.update_data(
        text=text,
        mes_del=mes_del.message_id,
        res_type=res_type,
        photo=photo,
        result_btn=None
    )


@router.callback_query(F.data == "answer_yes")
async def answer_yes_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    state_info = await state.get_data()
    try:
        await callback.bot.delete_message(
            chat_id=callback.from_user.id,
            message_id=state_info.get("mes_del")
        )
    except:
        pass

    other_users = await UserRepository.give_other_users(
        async_session=session
    )

    txt = "🏁 Рассылка началась"
    btn = back_to_admin_page_btn
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
    await state.clear()

    answer_users = []
    not_answer_users = []
    answered_user_id = callback.from_user.id
    for user in other_users:
        user_id = user.user_id
        if answered_user_id == user_id:
            continue
        await answer_user_message(
            state_info=state_info,
            bot=callback.bot,
            user_id=user_id
        )
    
    txt = (
        "✅ <b>Рассылка завершена</b>\n\n"
        f"🟢 Пользователей получивших рассылку: {len(answer_users)}\n"
        f"🔴 Пользователей заблокировавших бота: {len(not_answer_users)}"
    )
    mes_del = await callback.message.answer(
        text=txt,
        parse_mode="HTML"
    )

    await asyncio.sleep(20)
    await callback.bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=mes_del.message_id
    )


#=======================#BASE#=======================#
@router.callback_query(F.data == "admin_base")
async def admin_base_page(callback: CallbackQuery, session: AsyncSession):
    other_users = await UserRepository.give_other_users(
        async_session=session
    )
    file_path = export_users_to_excel(
        users=other_users
    )
    file = FSInputFile(
        path=file_path
    )
    user_id = callback.from_user.id
    btn = back_to_admin_page_btn
    txt = "📁 Файл с текущими пользователями"
    try:
        await callback.message.delete()
    except Exception as e:
        logging.error(f"Error delete callback message: {e}")
    await callback.bot.send_document(
        chat_id=user_id,
        document=file,
        caption=txt,
        reply_markup=btn
    )
    try:
        os.remove(file_path)
    except:
        logging.error("error delete file")


#=======================#TARIFF EDITOR#=======================#
@router.callback_query(F.data == "admin_tariffs_editor")
async def admin_tariffs_editor_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    txt = (
        "✍🏻<b>Редактор тарифов</b>\n\n"
        "Здесь вы можете:\n"
        "   ● Добавлять и удалять тарифы\n"
        "   ● Редактировать существующие тарифы\n"
        "   ● Активировать или деактивировать тариф\n"
        "   ● Изменять базовую стоимость дня"
    )
    btn = editor_page_btns
    await try_edit_callback(
        callback=callback,
        reply_markup=btn,
        parse_mode="HTML",
        text=txt
    )


#=======================#DAY EDIT#=======================#
@router.callback_query(F.data == "day_edit")
async def day_edit_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    now_day_edit = await SettingsRepository.get_daily_cost_cents(
        async_session=session
    )
    txt = (
        f"ℹ️ Текущая стоимость дня: {now_day_edit / 100} руб\n\n"
        f"Введите новую стоимость для замены"
    )
    btn = cancel_correct_btn
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
        state=AdminStates.day_correct
    )


@router.message(AdminStates.day_correct)
async def day_correct_page(message: Message, session: AsyncSession, state: FSMContext):
    await delete_state_message(
        state=state,
        message=message
    )
    try:
        new_price = int(message.text) * 100
    except:
        txt = "❌ Введите значение в виде числа"
        btn = cancel_correct_btn
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return
    await SettingsRepository.update_settings_info(
        async_session=session,
        key="daily_cost_cents",
        value=str(new_price)
    )

    await state.clear()
    txt = (
        "<b>✅ Вы успешно обновили цену</b>\n"
        "✍🏻<b>Редактор тарифов</b>\n\n"
        "Здесь вы можете:\n"
        "   ● Добавлять и удалять тарифы\n"
        "   ● Редактировать существующие тарифы\n"
        "   ● Активировать или деактивировать тариф\n"
        "   ● Изменять базовую стоимость дня"
    )
    btn = editor_page_btns
    await message.answer(
        reply_markup=btn,
        parse_mode="HTML",
        text=txt
    )


#=======================#TARIFF EDIT#=======================#
@router.callback_query(F.data == "tariffs_edit")
async def tariffs_edit_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    txt = (
        "📋<b>Текущие тарифы</b>\n\n"
        "ℹ️ Для редактирование или удаления выберите кнопку с нужным тарифом"
    )
    other_tariffs = await TariffRepository.give_other_tariffs(
        async_session=session
    )
    start_point = 0
    end_point = 0 + settings.PAGINATION_COUNT
    total_pages = (len(other_tariffs) + settings.PAGINATION_COUNT - 1) // settings.PAGINATION_COUNT

    btn = address_pagination_btns(
        other_tariffs=other_tariffs,
        start_point=start_point,
        end_point=end_point,
        now_point=1,
        total_pages=total_pages
    )
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("pagination_tariff_"))
async def pagination_tariff_page(callback: CallbackQuery, session: AsyncSession):

    action = callback.data.split("_")[2]
    start_point = int(callback.data.split("_")[3])

    txt = (
        "📋<b>Текущие тарифы</b>\n\n"
        "ℹ️ Для редактирование или удаления выберите кнопку с нужным тарифом"
    )
    other_tariffs = await TariffRepository.give_other_tariffs(
        async_session=session
    )

    total = len(other_tariffs)
    total_pages = (total + settings.PAGINATION_COUNT - 1) // settings.PAGINATION_COUNT 
    current_page = start_point // settings.PAGINATION_COUNT 
    input_current_page = int(callback.data.split("_")[4])

    if action == "back":
        if input_current_page == 1:
            input_current_page = total_pages
        else:
            input_current_page -= 1
        new_page = (current_page - 1) % total_pages
    else:  
        if input_current_page == total_pages:
            input_current_page = 1
        else:
            input_current_page += 1
        new_page = (current_page + 1) % total_pages
    new_start = new_page * settings.PAGINATION_COUNT
    new_end = min(new_start + settings.PAGINATION_COUNT, total)

    btn = address_pagination_btns(
        other_tariffs=other_tariffs,
        start_point=new_start,
        end_point=new_end,
        now_point=input_current_page,
        total_pages=total_pages
    )
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )



#=======================#TARIFF ADD#=======================#
@router.callback_query(F.data == "add_tariff")
async def add_tariff_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    txt = "💬 Введите название тарифа"
    btn = cancel_tariffs_edit_btn

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
        state=AdminStates.add_tariff_name
    )


@router.message(AdminStates.add_tariff_name)
async def add_tariff_name_page(message: Message, session: AsyncSession, state: FSMContext):

    await delete_state_message(
        state=state,
        message=message
    )
    name = message.text
    txt = "🗓️ Введите количество дней в тарифе"
    btn = cancel_tariffs_edit_btn
    mes_del = await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
    await state.update_data(
        mes_del=mes_del.message_id,
        name=name
    )
    await state.set_state(
        state=AdminStates.add_tariff_days
    )


@router.message(AdminStates.add_tariff_days)
async def add_tariff_days_page(message: Message, session: AsyncSession, state: FSMContext):
    await delete_state_message(
        state=state,
        message=message
    )
    btn = cancel_tariffs_edit_btn
    try:
        days = int(message.text)
    except:
        txt = "❌ Введите значение в виде числа"
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return
    
    txt = "💰 Введите стоимость тарифа (в рублях)"
    mes_del = await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )
    await state.update_data(
        mes_del=mes_del.message_id,
        days=days
    )
    await state.set_state(
        AdminStates.add_tariff_price
    )


@router.message(AdminStates.add_tariff_price)
async def add_tariff_price_page(message: Message, session: AsyncSession, state: FSMContext):
    state_info = await delete_state_message(
        state=state,
        message=message
    )
    btn = cancel_tariffs_edit_btn
    try:
        price_cents = int(message.text) * 100
    except:
        txt = "❌ Введите значение в виде числа"
        mes_del = await message.answer(
            text=txt,
            reply_markup=btn,
            parse_mode="HTML"
        )
        await state.update_data(
            mes_del=mes_del.message_id
        )
        return

    name = state_info.get("name")
    days = state_info.get("days")

    await TariffRepository.add_tariff(
        async_session=session,
        name=name,
        days=days,
        price_cents=price_cents
    )
    await session.flush()
    await state.clear()

    txt = (
        "✅ <b>Вы успешно добавили тариф</b>\n"
        "📋<b>Текущие тарифы</b>\n\n"
        "ℹ️ Для редактирование или удаления выберите кнопку с нужным тарифом"
    )
    other_tariffs = await TariffRepository.give_other_tariffs(
        async_session=session
    )
    start_point = 0
    end_point = 0 + settings.PAGINATION_COUNT
    total_pages = (len(other_tariffs) + settings.PAGINATION_COUNT - 1) // settings.PAGINATION_COUNT

    btn = address_pagination_btns(
        other_tariffs=other_tariffs,
        start_point=start_point,
        end_point=end_point,
        now_point=1,
        total_pages=total_pages
    )
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_mode="HTML"
    )


#=======================#TARIFF PAGE#=======================#
@router.callback_query(F.data.startswith("edit_tariff_"))
async def tariffs_info_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    tariff_id = int(callback.data.split("_")[2])
    tariff_info = await TariffRepository.give_tariff(
        async_session=session,
        tariff_id=tariff_id
    )
    if tariff_info.is_active == True:
        status = "🟢 Включить"
    else:
        status = "🔴 Отключить"

    txt = (
        "ℹ️ <b>Информация о тарифе:</b>\n\n"
        f"    ● Название тарифа: '{tariff_info.name}'\n"
        f"    ● Количество дней по тарифу: {tariff_info.days}\n"
        f"    ● Стоимость тарифа: {tariff_info.price_cents / 100}"
    )
    btn = tariff_info_page_btn(
        tariff_id=tariff_id,
        status=status
    )
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_ode="HTML"
    )


@router.callback_query(F.data.startswith("on_off_"))
async def tariffs_info_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    tariff_id = int(callback.data.split("_")[2])
    tariff_info = await TariffRepository.give_tariff(
        async_session=session,
        tariff_id=tariff_id
    )
    txt = (
        "ℹ️ <b>Информация о тарифе:</b>\n\n"
        f"    ● Название тарифа: '{tariff_info.name}'\n"
        f"    ● Количество дней по тарифу: {tariff_info.days}\n"
        f"    ● Стоимость тарифа: {tariff_info.price_cents / 100}"
    )
    if tariff_info.is_active == True:
        status = "🟢 Включить"
        value = False
    else:
        status = "🔴 Отключить"
        value = True
    
    await TariffRepository.update_tariff_info(
        async_session=session,
        tariff_id=tariff_id,
        agreement="is_active",
        value=value
    )
    btn = tariff_info_page_btn(
        tariff_id=tariff_id,
        status=status
    )
    await try_edit_callback(
        callback=callback,
        text=txt,
        reply_markup=btn,
        parse_ode="HTML"
    )


@router.callback_query(F.data.startswith("info_page_"))
async def info_tariff_agreement_edit_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    tariff_id = int(callback.data.split("_")[3])
    agreement = callback.data.split("_")[2]
    texts_dict = {
        "name": "✍🏻 Введите новое название тарифа",
        "days": "🗓️ Введите новое количество дней работы тарифа",
        "price": "💰 Введите новую стоимость"
    }
    btn = cancel_tariff_edit_page(
        tariff_id=tariff_id
    )
    mes_del = await try_edit_callback(
        callback=callback,
        text=texts_dict.get(agreement),
        reply_markup=btn,
        parse_mode="HTML"
    )

    await state.update_data(
        mes_del=mes_del.message_id,
        tariff_id=tariff_id,
        agreement=agreement
    )
    await state.set_state(
        state=AdminStates.tariff_edit_values
    )


@router.message(AdminStates.tariff_edit_values)
async def tariff_edit_values_page(message: Message, session: AsyncSession, state: FSMContext):
    state_info = await delete_state_message(
        state=state,
        message=message
    )
    tariff_id = state_info.get("tariff_id")
    agreement = state_info.get("agreement")
    if agreement in ['days', 'price']:
        try:
            value = int(message.text)
        except:
            txt = "❌ Введите значение в виде числа"
            btn = cancel_tariff_edit_page(
                tariff_id=tariff_id
            )
            mes_del = await message.answer(
                text=txt,
                reply_markup=btn,
                parse_mode="HTML"
            )
            await state.update_data(
                mes_del=mes_del.message_id
            )
            return
    else:
        value = message.text
    if agreement == "price":
        value *= 100
        agreement = "price_cents"
    await TariffRepository.update_tariff_info(
        async_session=session,
        tariff_id=tariff_id,
        agreement=agreement,
        value=value
    )
    await session.flush()
    await state.clear()

    tariff_info = await TariffRepository.give_tariff(
        async_session=session,
        tariff_id=tariff_id
    )
    txt = (
        "ℹ️ <b>Информация о тарифе:</b>\n\n"
        f"    ● Название тарифа: '{tariff_info.name}'\n"
        f"    ● Количество дней по тарифу: {tariff_info.days}\n"
        f"    ● Стоимость тарифа: {tariff_info.price_cents / 100}"
    )
    if tariff_info.is_active == True:
        status = "🔴 Отключить"
    else:
        status = "🟢 Включить"
    btn = tariff_info_page_btn(
        tariff_id=tariff_id,
        status=status
    )
    await message.answer(
        text=txt,
        reply_markup=btn,
        parse_ode="HTML"
    )


@router.callback_query(F.data == "withdrawal_answer_")
async def withdrawal_answer_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    answer = callback.data.split("_")[2]
    withdrawal_id = int(callback.data.split("_")[3])
    withdrawal_info = await WithdrawalsRepository.get_on_id(
        async_session=session,
        withdrawal_id=withdrawal_id
    )
    if answer == "yes":
        new_status = "paid"
        user_txt = "Ваша заявка на вывод средств была подтверждена"
        callback_text = "✅ Подтверждена"
    else:
        new_status = "cancel"
        user_txt = "Ваша заявка на вывод средств была отклонена"
        callback_text = "❌ Отклонена"
    await WithdrawalsRepository.update_status(
        async_session=session,
        withdrawal_id=withdrawal_id,
        new_status=new_status
    )
    user_id = withdrawal_info.user_id
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text=user_txt,
            parse_mode="HTML"
        )
    except:
        logging.error("error send message to user")
    
    txt = (
        f"{callback.message.text}\n\n"
        f"{callback_text}"
    )
    try:
        await callback.message.edit_text(
            text=txt,
            reply_markup=None
        )
    except:
        logging.error("error edit callback text")
