from __future__ import annotations

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.api.health import router as health_router
from app.api.websocket import router as websocket_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.state import build_state


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.backend_state = await build_state(settings)
    yield


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
app.include_router(health_router)
app.include_router(websocket_router)


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.app_env == "development",
    )
