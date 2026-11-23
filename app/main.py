from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router as api_router
from app.db.session import ensure_database_ready
from app.i18n import PROVINCE_EN_NAMES, TRANSLATIONS

APP_DIR = Path(__file__).resolve().parent


def create_app(auto_init_db: bool = True) -> FastAPI:
    @asynccontextmanager
    async def app_lifespan(_app: FastAPI):
        if auto_init_db:
            ensure_database_ready()
        yield

    application = FastAPI(
        title="Vietnam Mineral Map",
        description="Interactive mineral map across Vietnam's 34 post-2025 provinces and cities.",
        version="0.1.0",
        lifespan=app_lifespan,
    )

    application.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
    application.include_router(api_router)

    templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

    @application.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "translations": TRANSLATIONS,
                "province_en_names": PROVINCE_EN_NAMES,
            },
        )

    return application


app = create_app()
