# models.py

from sqlalchemy import BigInteger, String, ForeignKey, Integer, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DB_URI

engine = create_async_engine(url=DB_URI)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    signup_date: Mapped[str] = mapped_column(String(50), nullable=True)

class Plan(Base):
    __tablename__= 'plans'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    duration: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(255))

class Bill(Base):
    __tablename__= 'bills'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    bill_number: Mapped[str] = mapped_column(String(50))
    status: Mapped[bool] = mapped_column()
    plan: Mapped[str] = mapped_column(ForeignKey('plans.name'))
    price: Mapped[float] = mapped_column(Float)
    pay_link: Mapped[str] = mapped_column(String(255), nullable=True)
    issue_date: Mapped[str] = mapped_column(String(50), nullable=True)
    paid_date: Mapped[str] = mapped_column(String(50), nullable=True)

class Subscription(Base):
    __tablename__= 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    status: Mapped[bool] = mapped_column(Boolean)
    bill_number: Mapped[str] = mapped_column(ForeignKey('bills.bill_number'))
    plan: Mapped[str] = mapped_column(ForeignKey('plans.name'))
    duration: Mapped[int] = mapped_column(Integer)
    payment_info: Mapped[str] = mapped_column(String)
    issue_date: Mapped[str] = mapped_column(String(50))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



# category: Mapped[int] = mapped_column(ForeignKey('categories.id'))