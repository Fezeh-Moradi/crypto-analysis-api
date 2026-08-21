from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.api.routes import router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Crypto Analysis API with technical indicators",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["Crypto"])


@app.get("/")
async def root():
    return {
        "message": "Crypto Analysis API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup():
    logger.info("Crypto Analysis API started")