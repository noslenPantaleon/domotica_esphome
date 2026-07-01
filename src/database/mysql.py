import re

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings


def _build_engine():
    url = settings.database_url
    # PyMySQL does not accept ssl-mode=REQUIRED (MySQL Connector/C syntax).
    # Strip it from the URL and translate to connect_args so both dev (no ssl-mode)
    # and prod (ssl-mode=REQUIRED) work without changing .env files.
    ssl_required = bool(re.search(r"ssl-mode=REQUIRED", url, re.IGNORECASE))
    clean_url = re.sub(r"[?&]ssl-mode=[^&]*", "", url)
    clean_url = re.sub(r"\?$", "", clean_url)

    connect_args = {"ssl": {"check_hostname": False}} if ssl_required else {}
    return create_engine(clean_url, pool_pre_ping=True, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
