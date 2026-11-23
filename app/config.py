from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'khoang_san_vn.db').as_posix()}"
    seed_sql_path: str = str(PROJECT_ROOT / "khoang_san_viet_nam_tinh.sql")
    geojson_path: str = str(
        PROJECT_ROOT / "app" / "static" / "data" / "vietnam_provinces_34.geojson"
    )
    app_host: str = "127.0.0.1"
    app_port: int = 8000

    @property
    def resolved_seed_sql_path(self) -> Path:
        p = Path(self.seed_sql_path)
        return p if p.is_absolute() else PROJECT_ROOT / p

    @property
    def resolved_geojson_path(self) -> Path:
        p = Path(self.geojson_path)
        return p if p.is_absolute() else PROJECT_ROOT / p


settings = Settings()
