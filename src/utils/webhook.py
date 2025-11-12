import logging
from datetime import datetime
from aiogram import Bot
from aiohttp import web

from src.database.repositories import UserRepository, PayRepository
from src.database.db import async_session
from src.utils.helpers import pay_process
from src.config import settings

app = web.Application()
routes = web.RouteTableDef()

async def process_crypto_payment(payload):
    if payload["status"] == "paid":
        custom_payload = payload["payload"]
        user_id_str, amount_str, tariff_id = custom_payload.split(":")
        try:
            user_id = int(user_id_str)
            amount = int(amount_str)
            pay_id = int(tariff_id)
            bot: Bot = app['bot']
        
            async with async_session() as session:
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
                    bot=bot
                )
                await session.commit()
            
            logging.debug(f"Payment succeeded for user_id: {user_id}, amount: {amount}")
        except ValueError as e:
            logging.error(f"Ошибка конвертации user_id или amount: {e}")
    else:
        logging.warning(f"Получен неоплаченный инвойс: {payload}")


@routes.post('/webhook/cryptobot')
async def cryptobot_webhook(request):
    try:
        data = await request.json()
        logging.info(f"Получены данные вебхука: {data}")
        if data.get("update_type") == "invoice_paid":
            await process_crypto_payment(data["payload"])
            return web.Response(status=200)
        else:
            logging.warning(f"Неподдерживаемый тип обновления: {data.get('update_type')}")
            return web.Response(status=400)
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
        return web.Response(status=500)
    

async def setup_payments_app(bot):
    app.add_routes(routes)
    app['bot'] = bot
    return app


async def start_webhook_server(bot):
    app = await setup_payments_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)  
    await site.start()
    logging.info("Webhook server started on http://0.0.0.0:8000/webhook/cryptobot")
    return runner