from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import alerts, auth, characters, conversations, dashboard, devices, end_users, factories, industry, network, observability, users


def create_app() -> FastAPI:
    app = FastAPI(title="Voice Box Dashboard API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
    app.include_router(factories.router, prefix="/api/factories", tags=["factories"])
    app.include_router(users.router, prefix="/api", tags=["users"])
    app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
    app.include_router(end_users.router, prefix="/api/end-users", tags=["end-users"])
    app.include_router(characters.router, prefix="/api", tags=["characters"])
    app.include_router(conversations.router, prefix="/api", tags=["conversations"])
    app.include_router(industry.router, prefix="/api/industry", tags=["industry"])
    app.include_router(observability.router, prefix="/api/observability", tags=["observability"])
    app.include_router(network.router, prefix="/api/network", tags=["network"])
    app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
