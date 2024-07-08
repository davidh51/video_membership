from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
#from app.db.models import Base
from sqlalchemy.orm import declarative_base

#SQLALCHEMY_DATABASE_URL=(f'postgresql+asyncpg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@\
#{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}')
SQLALCHEMY_DATABASE_URL=(f'postgresql+asyncpg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@\
{settings.DATABASE_HOSTNAME}/{settings.DATABASE_NAME}')

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

Base = declarative_base()

async def init_models():
    async with async_engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)  #luego de tener alembic no es necesario para crear las tables
        

async def get_session():
    async with async_session() as db:
        try:
            yield db
        finally:
            await db.close()
