import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.keyboards.user_keyboards import user_menu
from src.utils.helpers import safe_answer, try_edit_callback
from src.database.repositories import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = Router()



# @router.callback_query(F.data.startswith("user_agreed_"))
# async def user_agreed(callback: CallbackQuery, session: AsyncSession):
#     user_answer = callback.data.split("_")[2]
#     user_id = callback.from_user.id
#     username = callback.from_user.username
#     fullname=callback.from_user.full_name


#     if user_answer == "not":
#         txt = ("Для работы с ботом необходимо ваше согласие на обработку персональных данных.\n\n"
#            "<a href=https:google.com'>Ознакомиться с политикой конфиденциальности:</a>"
#         )
#         btn = user_agreed_btns

#         await try_edit_callback(
#             callback=callback,
#             text=txt,
#             reply_markup=btn,
#             parse_mode="HTML"
#         )
#         return
#     await UserRepository.create_or_update_user(
#         async_session=session,
#         user_id=user_id,
#         username=username,
#         fullname=fullname

#     )
#     txt = ("👋 Добро пожаловать в систему подачи заявок!\n\n"
#            "Здесь вы можете быстро сообщить о проблемах в здании и отслеживать их решение.")
#     btn = user_menu

#     mes_del = await try_edit_callback(
#         callback=callback,
#         text=txt,
#         reply_markup=btn,
#         parse_mode="HTML"
#     )

    
