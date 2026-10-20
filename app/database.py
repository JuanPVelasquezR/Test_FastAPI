import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

# 1. Intentamos obtener la URL completa (la que provee Render)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Si no existe DATABASE_URL, armamos la URL usando settings (tu entorno local)
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# 3. Solución al prefijo: Render entrega 'postgres://', pero SQLAlchemy requiere 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crear el motor de la base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para la creación de los modelos
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()