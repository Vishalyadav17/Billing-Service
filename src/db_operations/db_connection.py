import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    connect_args={"application_name": "billing-system"},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
