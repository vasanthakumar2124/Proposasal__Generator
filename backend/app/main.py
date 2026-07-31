from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.infrastructure.database.mongodb import connect_to_mongodb, close_mongodb_connection, ensure_indexes
from app.infrastructure.database.redis import connect_to_redis, close_redis_connection
from app.api.v1.api import api_router
from app.domain.exceptions import DomainError
from app.middleware import RateLimitMiddleware

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    await ensure_indexes()
    await connect_to_redis()
    yield
    await close_mongodb_connection()
    await close_redis_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Proposal Generation SaaS Platform",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-RateLimit-Remaining"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.add_middleware(RateLimitMiddleware)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API", "version": "3.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "3.0.0"}
