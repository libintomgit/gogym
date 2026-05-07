from contextlib import asynccontextmanager
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import NotFoundError, ForbiddenError, ConflictError


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

logger = logging.getLogger(__name__)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred - Libin"},
    )


app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(plan_router)
app.include_router(schedule_router)
app.include_router(session_router)
app.include_router(sharing_router)


@app.get("/")
def root():
    return {
        "service": "GoGym API",
        "description": "Backend service for the GoGym application — a workout planning, scheduling, and logging platform.",
        "version": "0.1.0",
        "docs": "/docs",
    }