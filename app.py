# app.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from models import ModelVersion, Policy, Application
from routes.routes_models import router as models_router
from routes.routes_policy import router as policy_router
from routes.routes_score import router as score_router
from routes.routes_legacy import legacy as legacy_router

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Credit System – Modular")

# CORS dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Static
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# DB init
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(models_router)
app.include_router(policy_router)
app.include_router(score_router)
app.include_router(legacy_router)

# HTML routes
@app.get("/", include_in_schema=False)
def home():
    # use index.html (você disse que vai renomear o home -> index)
    path = STATIC_DIR / "index.html"
    if not path.exists():
        # fallback se ainda não renomeou
        fallback = STATIC_DIR / "home.html"
        return FileResponse(fallback if fallback.exists() else path)
    return FileResponse(path)

@app.get("/apply", include_in_schema=False)
def apply_page(): return FileResponse(STATIC_DIR / "apply.html")

@app.get("/policy", include_in_schema=False)
def policy_page(): return FileResponse(STATIC_DIR / "policy.html")

@app.get("/model", include_in_schema=False)
def model_page(): return FileResponse(STATIC_DIR / "model.html")

@app.get("/healthz")
def healthz(): return {"ok": True, "service": "credit-system-modular", "version": "v2"}

@app.get("/model", include_in_schema=False)
def model_page():
    return FileResponse(STATIC_DIR / "model.html")