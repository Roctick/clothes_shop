from sqlalchemy import BigInteger, String, ForeignKey #импортируем типы данных которые будут в БД
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column #
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine # тк фреймворк асинхронный БД тоже ассинхронная

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')# создвём БД

async_session = async_sessionmaker(engine)#создвние сессии т.е запуск БД и создание колонок если их нет


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'# название таблицы

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    number = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(100))


async def async_main5():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)