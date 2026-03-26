from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routes.auth import router as auth_router
from app.routes.inventory import router as inventory_router
from app.routes.plan import router as plan_router
from app.routes.schedule import router as schedule_router
from app.routes.session import router as session_router
from app.routes.sharing import router as sharing_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise RuntimeError(
            f"Failed to connect to the database on startup: {exc}"
        ) from exc
    yield

app = FastAPI(title="GoGym API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(plan_router)
app.include_router(schedule_router)
app.include_router(session_router)
app.include_router(sharing_router)