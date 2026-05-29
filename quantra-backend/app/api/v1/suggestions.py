"""Quantra — Suggestions API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.suggestion_service import get_user_suggestions, mark_suggestion_read

router = APIRouter()


@router.get("")
async def list_suggestions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Today's personalized suggestions for user."""
    suggestions = await get_user_suggestions(db, user.id)
    return {
        "suggestions": [
            {"id": str(s.id), "ticker": s.ticker, "action": s.action, "confidence": float(s.confidence) if s.confidence else None,
             "reason": s.reason, "expires_at": s.expires_at.isoformat() if s.expires_at else None, "is_read": s.is_read}
            for s in suggestions
        ],
        "user_risk_profile": user.risk_profile,
    }


@router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_suggestions(user: User = Depends(get_current_user)):
    """Force regenerate suggestions."""
    from app.workers.tasks.generate_suggestions import run
    run.delay()
    return {"status": "queued"}


@router.patch("/{suggestion_id}/read")
async def mark_read(suggestion_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Mark suggestion as read."""
    success = await mark_suggestion_read(db, suggestion_id, user.id)
    if not success:
        return {"error": "Suggestion not found"}
    return {"status": "ok"}
