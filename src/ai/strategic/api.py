
"""
API Router for Strategic Meta-AI.
Exposes endpoints for quarterly strategic reviews and system oversight.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any

from common.logging_config import get_logger
from common.models import QuarterlyReview, StrategicPlan
from .meta_ai import StrategicMetaAI

logger = get_logger("ai.strategic.api")

router = APIRouter(tags=["Strategic AI"])

# Global instance for the service (singleton pattern for stateful AI)
_strategic_ai = None

def get_strategic_ai() -> StrategicMetaAI:
    global _strategic_ai
    if _strategic_ai is None:
        _strategic_ai = StrategicMetaAI()
    return _strategic_ai

@router.post("/strategic/evaluate", response_model=QuarterlyReview)
async def trigger_strategic_review(background_tasks: BackgroundTasks):
    """
    Trigger an immediate strategic review (manual override of quarterly schedule).
    Useful for testing or ad-hoc analysis.
    """
    try:
        ai = get_strategic_ai()
        review = await ai.run_immediate_review()
        return review
    except Exception as e:
        logger.error(f"Failed to trigger strategic review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategic/reviews", response_model=List[QuarterlyReview])
async def get_strategic_reviews():
    """
    Get history of quarterly strategic reviews.
    """
    ai = get_strategic_ai()
    return ai.get_reviews()

@router.get("/strategic/oversight", response_model=Dict[str, Any])
async def get_oversight_status():
    """
    Get current human oversight status (pending approvals, alerts).
    """
    ai = get_strategic_ai()
    return ai.get_oversight_status()
