from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str


    VPN_KEY: str  
    VPN_BASE_URL: str

    DEFAULTS: Dict[str, str] = {
        "daily_cost_cents": "600",          
        "channel_id": "",                       
        "channel_bonus_days": "7",
        "channel_bonus_cents": "4200",        
        "referral_trial_bonus_cents": "10000",   
        "referral_payment_bonus_cents": "5000",  
        "min_withdrawal_cents": "10000",         
        "admin_chat_id": "",
        "remnavawe_cluster_id": "1",
        "support_link": "t.me/support",
        "bot_username": "VlesVPNbot",
        "payment_wata_enabled": "true",
        "payment_cryptobot_enabled": "true",
        "payment_stars_enabled": "false",
    }

    DESCRIPTIONS: Dict[str, str] = {
        "daily_cost_cents": "Базовая стоимость 1 дня в копейках",
        "channel_id": "ID канала для бонуса (например, -1001234567890)",
        "channel_bonus_days": "Дней бонуса за подписку",
        "channel_bonus_cents": "Сумма бонуса в копейках (автосинхрон с base_day_price)",
        "referral_trial_bonus_cents": "Бонус рефереру за пробный период",
        "referral_payment_bonus_cents": "Бонус рефереру за пополнение",
        "min_withdrawal_cents": "Минимальная сумма вывода в копейках",
        "admin_chat_id": "ID админа или чата для уведомлений",
        "remnavawe_cluster_id": "ID кластера в remnavawe",
        "support_link": "Ссылка на поддержку",
        "bot_username": "Юзернейм бота без @",
        "payment_wata_enabled": "Включить оплату через Wata",
        "payment_cryptobot_enabled": "Включить оплату через CryptoBot",
        "payment_stars_enabled": "Включить оплату Telegram Stars",
    }
    PAGINATION_COUNT: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  
    )

settings = Settings()