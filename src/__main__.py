import asyncio
import aiocron
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from src.config import settings
from src.utils.cron import balance_minus
from src.database.db import db, async_session
from src.handlers import commands, user_handlers, admin_handlers
from src.middlewares.database import DatabaseMiddleware
from src.database.repositories import SettingsRepository
from src.database.db import async_session
from src.utils.webhook import start_webhook_server


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(
        token=settings.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
dp = Dispatcher()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Перезапустить бота")
    ]
    await bot.set_my_commands(commands)



async def main():
    
    await db.init()
    await db.init_models()
    async with async_session() as session:
        await SettingsRepository.init_default_settings(
            async_session=session
        )
        logging.info("✅ Default values init")
    await start_webhook_server(
        bot=bot
    )
    await set_commands(bot)
    
    # aiocron.crontab('* * * * *', func=balance_minus, start=True, args=[bot])  

    
    dp.include_routers(
        commands.router,
        admin_handlers.router,
        user_handlers.router
    )
    dp.update.outer_middleware(DatabaseMiddleware())
    
    try:
        logger.info("🚀 Бот запущен")
        logger.info("⏰ Cron задачи запущены")
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()
        logger.info("🔌 Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем") 