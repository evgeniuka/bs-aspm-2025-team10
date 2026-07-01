from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine
from app.routers import analytics, auth, clients, dashboard, exercises, groups, programs, sessions, trainee

settings = get_settings()

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
CSRF_HEADER = "x-requested-with"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Convenience for local SQLite/dev only; managed databases must use Alembic migrations.
    if settings.is_development or settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def require_csrf_header(request: Request, call_next):
    # Defense-in-depth for the cookie-authenticated API: state-changing requests must carry a
    # custom header, which browsers never attach on cross-site form/navigation requests.
    if request.method not in SAFE_METHODS and request.url.path.startswith(settings.api_prefix):
        if not request.headers.get(CSRF_HEADER):
            return JSONResponse(
                status_code=403,
                content={"detail": "Missing X-Requested-With header"},
            )
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(clients.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(exercises.router, prefix=settings.api_prefix)
app.include_router(groups.router, prefix=settings.api_prefix)
app.include_router(programs.router, prefix=settings.api_prefix)
app.include_router(sessions.router, prefix=settings.api_prefix)
app.include_router(trainee.router, prefix=settings.api_prefix)
