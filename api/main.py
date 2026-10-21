import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exceptions import register_exception_handlers
from core.logging import RequestIdMiddleware
from core.responses import success
from modules import auth, chat, product

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

app = FastAPI(title="AI Product Advisor")

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
def health():
    return success(message="ok", result={"service": "ai-product-advisor"})
