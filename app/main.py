from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.manga.routers import router as manga_router

app = FastAPI()

app.include_router(manga_router, prefix="/api/manga")