from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import PROJECT_ROOT
from app.db.session import ensure_database_ready, get_db
from app.main import create_app


@pytest.fixture(scope="session")
def test_db_engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(eng, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    ensure_database_ready(
        target_engine=eng,
        seed_sql_path=PROJECT_ROOT / "khoang_san_viet_nam_tinh.sql",
        reset=True,
    )
    yield eng
    eng.dispose()


@pytest.fixture()
def client(test_db_engine):
    app = create_app(auto_init_db=False)
    testing_session_local = sessionmaker(
        bind=test_db_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    def _override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
