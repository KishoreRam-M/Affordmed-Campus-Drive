from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.utils.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(router, prefix=settings.api_v1_prefix)
    register_exception_handlers(app)
    return app


app = create_app()
