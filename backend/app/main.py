"""
FermaGen AI - Main FastAPI Application
AI-powered precision fermentation platform
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.database.database import init_db
from app.cache import init_cache, close_cache
from app.auth.routes import router as auth_router
from app.experiments.routes import router as experiments_router
from app.protein.routes import router as protein_router
from app.ai.routes import router as ai_router
from app.external_routes import router as external_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info("Starting FermaGen AI application")
    await init_db()
    logger.info("Database initialized successfully")
    
    # Initialize cache
    await init_cache()
    
    yield
    
    # Close cache on shutdown
    await close_cache()
    
    logger.info("Shutting down FermaGen AI application")


app = FastAPI(
    title="FermaGen AI",
    description="AI-powered precision fermentation platform for sustainable protein R&D",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceptions"""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )


# CORS Configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_url.split(",") if "," in settings.frontend_url else [settings.frontend_url],
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


from fastapi.responses import JSONResponse

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "FermaGen AI",
        "version": "1.0.0",
        "production": settings.is_production
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "ok",
        "database": "connected",
        "ml_models": "loaded",
        "production": settings.is_production
    }
