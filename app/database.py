import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()  # reads the .env file in the project root

# Alembic and psql tools use this URL (driver: psycopg2, which is not async).
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Create a .env file (see .env.example).")

# The app talks to the same database through the async driver, asyncpg.
ASYNC_DATABASE_URL = DATABASE_URL.replace("+psycopg2", "+asyncpg", 1)

engine = create_async_engine(
    ASYNC_DATABASE_URL, pool_size=5, max_overflow=10, pool_pre_ping=True
)
SessionLocal = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as db:
        yield db
