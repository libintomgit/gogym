import uuid as uuid_mod

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.types import CHAR, TypeDecorator

from app.config import settings

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class GUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses CHAR(32) for SQLite, native UUID for PostgreSQL.
    """
    impl = CHAR(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid_mod.UUID):
                return value.hex
            return uuid_mod.UUID(value).hex
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid_mod.UUID):
                return uuid_mod.UUID(value)
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(CHAR(32))


class Base(DeclarativeBase):
    type_annotation_map = {
        uuid_mod.UUID: GUID,
    }