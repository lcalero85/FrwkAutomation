from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.dashboard_routes import router as dashboard_router
from app.api.routes.execution_routes import router as execution_router
from app.api.routes.email_routes import router as email_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.project_routes import router as project_router
from app.api.routes.report_routes import router as report_router
from app.api.routes.recorder_routes import router as recorder_router
from app.api.routes.scheduler_routes import router as scheduler_router
from app.api.routes.settings_routes import router as settings_router
from app.api.routes.template_routes import router as template_router
from app.api.routes.user_routes import router as user_router
from app.api.routes.web_routes import router as web_router
from app.database.init_db import init_database

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "app" / "web" / "static"

app = FastAPI(
    title=os.getenv("APP_NAME", "AutoTest Pro Framework"),
    description="API backend and professional web interface for AutoTest Pro Framework.",
    version="0.18.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")




@app.middleware("http")
async def security_headers_middleware(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.on_event("startup")
def on_startup() -> None:
    init_database()


@app.get("/")
def root():
    return {
        "app": os.getenv("APP_NAME", "AutoTest Pro Framework"),
        "version": "0.18.0",
        "docs": "/docs",
        "health": "/health",
        "ui": "/ui",
    }


app.include_router(health_router)
app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(execution_router, prefix="/api")
app.include_router(email_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(recorder_router, prefix="/api")
app.include_router(scheduler_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(template_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(web_router)
