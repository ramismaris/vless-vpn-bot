import logging
from aiogram import Bot
from src.database.db import async_session
from src.database.repositories import UserRepository, SettingsRepository
from src.utils.helpers import user_deactivate


async def balance_minus(bot: Bot):
    async with async_session() as session:
        users = await UserRepository.give_other_sub_users(
            async_session=session
        )
        day_price = int(await SettingsRepository.get_daily_cost_cents(
            async_session=session
        ))
        for user in users:
            logging.info(f"Old balance:{user.main_balance}\n")
            if user.main_balance <= 0 and user.main_balance < day_price:
                user_new_count = user.main_balance - day_price
                await user_deactivate(
                    user_id=user.user_id,
                    user_uuid=user.vless_uuid,
                    session=session,
                    new_amount=user_new_count
                )
                logging.info(f"User deactivate because have (< 0, < day_price) on balance.\n\nNew balance:{user_new_count}\nDay_price: {day_price}")
            else:
                user_new_count = user.main_balance - day_price
                if user_new_count <= 0:
                    user_new_count = 0
                    await user_deactivate(
                        user_id=user.user_id,
                        user_uuid=user.vless_uuid,
                        session=session,
                        new_amount=user_new_count
                    )
                    logging.info(f"User deactivate post minus because have (< 0) on balance.\n\nDay_price: {day_price}\nNew balance: {user_new_count}")
                elif user_new_count < day_price:
                    await user_deactivate(
                        user_id=user.user_id,
                        user_uuid=user.vless_uuid,
                        session=session,
                        new_amount=user_new_count
                    )
                    logging.info(f"User deactivate post minus because have (< day_price) on balance.\n\n\nDay_price: {day_price}\nNew balance: {user_new_count}")
                else:
                    await UserRepository.update_balance(
                        async_session=session,
                        user_id=user.user_id,
                        new_balance=user_new_count
                    )
                    logging.info(f"User balance min.\n\nDay_price: {day_price}\nNew balance: {user_new_count}")
        await session.commit()
                
                

