"""
Configuración de base de datos para SQLAlchemy
"""
from sqlalchemy import create_engine  # type: ignore[import]
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore[import]
from os import getenv

# URL de conexión a PostgreSQL
DATABASE_URL = getenv(
    "DB_URL",
    getenv("DATABASE_URL", "postgresql://user:password@localhost/incidencias")
)

# Configuración de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
