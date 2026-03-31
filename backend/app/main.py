from fastapi import FastAPI
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.models.user import User
from app.models.meme_history import MemeHistory
from app.models.meme import Meme

from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router
from app.routes.meme_history_routes import router as meme_history_router
from app.routes.meme_routes import router as meme_router
from app.routes.recognition_routes import router as recognition_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=f"ambiente atual: {settings.app_env}",
    version=settings.app_version
)


app.mount("/media", StaticFiles(directory="storage"), name="media")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database": "connected"}


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(meme_history_router)
app.include_router(meme_router)
app.include_router(recognition_router)