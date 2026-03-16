from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv(".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import app_config
from src.db_operations.db_connection import engine
from src.db_operations.db_models import Base
from src.logger import logger
from src.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting up [env=%s]", app_config.env)
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("shutting down")


app = FastAPI(
    title="Billing System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/billing")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "billing-system", "version": "1.0.0"}


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
