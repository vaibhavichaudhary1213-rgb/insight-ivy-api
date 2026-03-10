from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.mood import router as mood_router
from app.routes.analytics import router as analytics_router
from app.routes.wellness import router as wellness_router      # Wellness tracking
from app.routes.growth import router as growth_router          # Growth & motivation
from app.logger import logger
from app.routes import admin

# -------------------------
# Create FastAPI App
# -------------------------
app = FastAPI(
    title="Happiness API",
    description="Emotional support chatbot with wellness tracking, habit formation, and personal growth features",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("🌸 Happiness API v2.0 initializing with enhanced features...")

# -------------------------
# Register Routers
# -------------------------
# Core emotional support
app.include_router(mood_router, prefix="/mood", tags=["Mood Analysis"])
logger.info("✅ Mood router registered at /mood")

# Analytics dashboard
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
logger.info("✅ Analytics router registered at /analytics")

# Wellness tracking (sleep, exercise, water, habits)
app.include_router(wellness_router, prefix="/wellness", tags=["Wellness Tracking"])
logger.info("✅ Wellness router registered at /wellness")

# Growth & motivation (goals, fears, prompts, kindness)
app.include_router(growth_router, prefix="/growth", tags=["Growth & Motivation"])
logger.info("✅ Growth router registered at /growth")

app.include_router(admin.router)

# -------------------------
# Root Endpoint
# -------------------------
@app.get("/")
def root():
    """
    Welcome endpoint showing all available features
    """
    logger.info("Root endpoint accessed")

    return {
        "message": "Happiness API is running with enhanced features! 🌸",
        "version": "2.0.0",
        "endpoints": {
            "core": {
                "mood": "/mood/analyze - Analyze emotions and get responses",
                "analytics": "/analytics - Get system analytics"
            },
            "wellness": {
                "sleep": "/wellness/track/sleep - Track sleep hours",
                "exercise": "/wellness/track/exercise - Track exercise",
                "water": "/wellness/track/water - Track water intake",
                "habits": "/wellness/habits/ - Habit tracking",
                "happiness": "/wellness/happiness/ - Mood logging and graphs"
            },
            "growth": {
                "joy": "/growth/joy/ - Personal joy triggers",
                "goals": "/growth/goal - Long-term goals",
                "prompts": "/growth/student/prompt - Student reflection prompts",
                "emotional": "/growth/emotional/prompt - Emotional awareness",
                "gratitude": "/growth/gratitude/ - Micro-gratitude",
                "appreciation": "/growth/appreciation/ - Self-appreciation",
                "kindness": "/growth/kindness/ - Kindness challenges"
            }
        },
        "documentation": "/docs or /redoc for API documentation"
    }

# -------------------------
# Health Check Endpoint
# -------------------------
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "services": {
            "mood": "active",
            "analytics": "active",
            "wellness": "active",
            "growth": "active"
        },
        "timestamp": logger.get_timestamp() if hasattr(logger, 'get_timestamp') else "active"
    }

# -------------------------
# Startup Event
# -------------------------
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform when the application starts
    """
    logger.info("🚀 Happiness API is starting up...")
    logger.info("Features loaded: Mood Analysis, Analytics, Wellness Tracking, Growth & Motivation")
    logger.info("All systems ready! 🌈")

# -------------------------
# Shutdown Event
# -------------------------
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform when the application shuts down
    """
    logger.info("👋 Happiness API is shutting down. Take care! 🌸")