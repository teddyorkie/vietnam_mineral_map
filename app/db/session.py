from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.models import Base
from app.db.seed import seed_database


def create_db_engine(database_url: str | None = None) -> Engine:
    url = database_url or settings.database_url
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {"future": True}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if url != "sqlite:///:memory:" and "mode=memory" not in url:
            raw_path = url.replace("sqlite:///", "", 1)
            db_file = Path(raw_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_recycle"] = 1800

    eng = create_engine(url, connect_args=connect_args, **engine_kwargs)

    if url.startswith("sqlite"):

        @event.listens_for(eng, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return eng


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def ensure_database_ready(
    target_engine: Engine | None = None,
    seed_sql_path: Path | None = None,
    reset: bool = False,
) -> dict[str, int]:
    eng = target_engine or engine
    sql_file = seed_sql_path or settings.resolved_seed_sql_path
    Base.metadata.create_all(bind=eng)
    session_factory = sessionmaker(
        bind=eng, autoflush=False, autocommit=False, expire_on_commit=False
    )
    with session_factory() as session:
        return seed_database(session, sql_file, reset=reset)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
