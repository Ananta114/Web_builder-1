from fastapi import FastAPI
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.db.session import engine
from app.db.base import Base
from app.api.v1 import auth, other  # import all routers here

# Define one common prefix (applies to all APIs)
API_PREFIX = "/auth"

def create_app() -> FastAPI:
    app = FastAPI(title="Auth API", debug=settings.DEBUG)

    # ✅ Include all routers under one common prefix
    app.include_router(auth.router, prefix=API_PREFIX, tags=["Auth"])
    app.include_router(other.router, prefix=API_PREFIX, tags=["Auth"])

    # Register custom error handlers
    register_exception_handlers(app)

    @app.on_event("startup")
    def on_startup():
        # Create DB tables if not exist
        Base.metadata.create_all(bind=engine)

    return app

app = create_app()
