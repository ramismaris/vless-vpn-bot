from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from sqlalchemy.ext.declarative import DeclarativeMeta
import asyncpg
import logging

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:5432/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base: DeclarativeMeta = declarative_base()


class Database:
   
    async def init(self):
        """Инициализация пула соединений"""
        try:
            temp_pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                user=settings.DB_USER,
                password=settings.DB_PASS,
                database='postgres',  
                min_size=1,
                max_size=2
            )
            
            async with temp_pool.acquire() as conn:
                exists = await conn.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1", 
                    settings.DB_NAME
                )
                
                if not exists:
                    await conn.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
                    logging.info(f"✅ База данных {settings.DB_NAME} создана")
                else:
                    logging.info(f"✅ База данных {settings.DB_NAME} уже существует")
            
            await temp_pool.close()
            
        except Exception as e:
            logging.error(f"❌ Ошибка подключения к БД: {e}")
            raise

    

    async def init_models(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("таблицы созданы")


db = Database() 