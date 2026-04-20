from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

from app.auth.auth import get_current_user
from app.models.user import User
from app.services.wellbeing_service import (
    WellbeingService, ALL_QUESTIONS, SWEMWBS_QUESTIONS, PHQ2_QUESTIONS,
    calculate_category, process_responses
)

# ============================================
# ✅ THIS CREATES THE ROUTER - REQUIRED!
# ============================================
router = APIRouter(prefix="/wellbeing", tags=["wellbeing"])


# Request/Response Models
class AssessmentRequest(BaseModel):
    responses: Dict[str, int]


class AssessmentResponse(BaseModel):
    id: str
    total_score: float
    category: str
    category_icon: str
    tips: List[str]
    date: str


# ============================================
# ENDPOINTS
# ============================================

@router.get("/questions")
async def get_questions():
    """Get all wellbeing questions"""
    return {
        "swemwbs": SWEMWBS_QUESTIONS,
        "phq2": PHQ2_QUESTIONS,
        "all": ALL_QUESTIONS
    }


@router.post("/assess", response_model=AssessmentResponse)
async def submit_assessment(
    request: AssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit a wellbeing assessment"""
    
    responses = request.responses
    
    # Validate all questions answered
    expected_ids = [q["id"] for q in ALL_QUESTIONS]
    for q_id in expected_ids:
        if q_id not in responses:
            raise HTTPException(status_code=400, detail=f"Missing answer for {q_id}")
        if not 1 <= responses[q_id] <= 5:
            raise HTTPException(status_code=400, detail=f"Invalid score for {q_id}")
    
    # Process responses (flip negative questions)
    processed_responses = process_responses(responses)
    
    # Calculate scores using PROCESSED (flipped) responses
    swemwbs_scores = [processed_responses[q["id"]] for q in SWEMWBS_QUESTIONS]
    phq2_scores = [processed_responses[q["id"]] for q in PHQ2_QUESTIONS]
    
    all_scores = swemwbs_scores + phq2_scores
    total_score = sum(all_scores) / len(all_scores)
    
    # Calculate category
    category, category_icon = calculate_category(total_score)
    
    # Get personalised tips
    tips = WellbeingService.get_tips_for_assessment(responses, total_score, category)
    
    # Save to CSV
    success = WellbeingService.save_assessment(
        user_id=current_user.id,
        responses=responses,
        total_score=total_score,
        category=category,
        tips=tips
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save assessment")
    
    return AssessmentResponse(
        id=str(datetime.utcnow().timestamp()),
        total_score=round(total_score, 2),
        category=category,
        category_icon=category_icon,
        tips=tips,
        date=datetime.utcnow().isoformat()
    )


@router.get("/history")
async def get_assessment_history(
    current_user: User = Depends(get_current_user)
):
    """Get user's assessment history"""
    history = WellbeingService.get_user_history(current_user.id)
    return history


@router.get("/latest")
async def get_latest_assessment(
    current_user: User = Depends(get_current_user)
):
    """Get user's most recent assessment"""
    latest = WellbeingService.get_latest_assessment(current_user.id)
    
    if not latest:
        return {"has_assessment": False, "message": "No assessments yet"}
    
    return {
        "has_assessment": True,
        "id": latest.get('id'),
        "date": latest.get('date'),
        "total_score": float(latest.get('total_score', 0)),
        "category": latest.get('category'),
        "tips": latest.get('tips_list', [])
    }