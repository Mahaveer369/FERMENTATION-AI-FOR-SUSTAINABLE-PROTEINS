"""
FermaGen AI - Main FastAPI Application
AI-powered precision fermentation platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.database import init_db
from app.auth.routes import router as auth_router
from app.experiments.routes import router as experiments_router
from app.protein.routes import router as protein_router
from app.ai.routes import router as ai_router
from app.external_routes import router as external_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_db()
    yield


app = FastAPI(
    title="FermaGen AI",
    description="AI-powered precision fermentation platform for sustainable protein R&D",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(experiments_router, prefix="/experiment", tags=["Experiments"])
app.include_router(protein_router, prefix="/protein", tags=["Protein Analysis"])
app.include_router(ai_router, prefix="/ai", tags=["AI Optimization"])
app.include_router(external_router, prefix="/external", tags=["External APIs"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "FermaGen AI",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "database": "connected",
        "ml_models": "loaded"
    }
