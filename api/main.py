import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from core.config import settings
from core.db import SessionLocal
from core.exceptions import register_exception_handlers
from core.logging import RequestIdMiddleware
from core.responses import success
from modules import auth, chat, product

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.require_ai_provider_key()
    settings.require_rate_limit_backend()
    yield


app = FastAPI(title="AI Product Advisor", lifespan=lifespan)

register_exception_handlers(app)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(product.router)
api_router.include_router(chat.router)

app.include_router(api_router)


@app.get("/health")
@app.get("/health/live")
def health_live():
    """Liveness — process is up (no dependency checks)."""
    return success(message="ok", result={"service": "ai-product-advisor", "status": "live"})


@app.get("/health/ready")
def health_ready():
    """Readiness — database is reachable."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logging.getLogger(__name__).exception("Readiness check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    finally:
        db.close()

    return success(
        message="ok",
        result={"service": "ai-product-advisor", "status": "ready", "database": "ok"},
    )
