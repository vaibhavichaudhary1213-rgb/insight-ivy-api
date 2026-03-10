from fastapi import APIRouter
from app.services.analytics_engine import get_summary
from app.logger import logger

router = APIRouter()


# -------------------------
# Get Analytics Summary
# -------------------------
@router.get("/")
def read_analytics():

    logger.info("Analytics summary requested")

    summary = get_summary()

    logger.info(f"Analytics data returned: {summary}")

    return summary


# -------------------------
# Analytics Health Check
# -------------------------
@router.get("/health")
def analytics_health():

    logger.info("Analytics health check accessed")

    return {"status": "Analytics service running"}




