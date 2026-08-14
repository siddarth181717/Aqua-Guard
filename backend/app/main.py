"""
AquaGuard FastAPI Main Application Entrypoint
----------------------------------------------
Production-ready FastAPI backend serving REST APIs for water body surveillance,
geospatial PostGIS analytics, and AI/ML restoration priority predictions.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.router import api_router
from backend.app.core.config import settings
from backend.app.core.database import Base, engine

# Initialize database tables on application startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AquaGuard – AI-Driven Geospatial Surveillance for Water Body Restoration API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS Middleware for React frontend & local development
cors_origins = settings.BACKEND_CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler delivering structured JSON error responses."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later."
            }
        }
    )


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root_redirect():
    """Root URL redirecting to API documentation."""
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
