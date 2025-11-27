"""
Database configuration module for the application.

This module sets up the asynchronous database engine and session factory
using SQLAlchemy 2.0+ async capabilities. It provides a configured engine
and session maker that can be imported and used throughout the application
to interact with the database.

The configuration uses connection settings from the application's settings
module, allowing for environment-specific database configuration.
"""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.DB_URL)
"""
Async SQLAlchemy engine instance.

This engine is configured with the database URL from application settings
and is used to create database connections. It enables asynchronous
database operations throughout the application.
"""

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
"""
Factory for creating async database sessions.

This session maker produces async database sessions that are bound to the
configured engine. The expire_on_commit=False setting prevents attributes
from being expired after commit, which is useful when accessing object
attributes after a transaction has been committed.
"""


class Base(DeclarativeBase):
    """
    Base class for all ORM models in the application.

    This class serves as the declarative base for all SQLAlchemy models.
    All model classes should inherit from this Base class to be properly
    recognized by SQLAlchemy and included in the metadata.

    Example:
        class User(Base):
            __tablename__ = "users"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
    """
    pass
