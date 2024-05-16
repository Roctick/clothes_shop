from sqlalchemy import BigInteger, String, ForeignKey #импортируем типы данных которые будут в БД
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column #
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine # тк фреймворк асинхронный БД тоже ассинхронная

engine = create_async_engine(url='sqlite+aiosqlite:///db_hats.sqlite3')# создвём БД

async_session = async_sessionmaker(engine)#создвние сессии т.е запуск БД и создание колонок если их нет


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = 'hat_categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class Item(Base):
    __tablename__ = 'hats_items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))# String(150) БД  требует ограничений
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('hat_categories.id'))


async def async_main4():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)