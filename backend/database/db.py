from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./support.db")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_customers()


async def get_db():
    """Dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session


async def seed_customers():
    """Seed a few demo customers so the app works out of the box."""
    from database.models import Customer
    from sqlalchemy import select

    demo_customers = [
        Customer(id="CUST-001", name="Alice Johnson",  email="alice@example.com",  plan="pro"),
        Customer(id="CUST-002", name="Bob Smith",      email="bob@example.com",    plan="enterprise"),
        Customer(id="CUST-003", name="Carol Williams", email="carol@example.com",  plan="free"),
    ]

    async with AsyncSessionLocal() as session:
        for customer in demo_customers:
            result = await session.execute(
                select(Customer).where(Customer.id == customer.id)
            )
            if not result.scalars().first():
                session.add(customer)
        await session.commit()
