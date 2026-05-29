"""Quantra — Alerts API endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.alert import AlertCreate
from app.services.alert_service import create_alert, delete_alert, get_user_alerts

router = APIRouter()


@router.get("")
async def list_alerts(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alerts = await get_user_alerts(db, user.id)
    return [{"id": str(a.id), "ticker": a.ticker, "condition": a.condition, "channels": a.channels, "is_active": a.is_active, "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None} for a in alerts]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create(payload: AlertCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alert = await create_alert(db, user.id, payload.model_dump())
    return {"id": str(alert.id), "ticker": alert.ticker, "condition": alert.condition, "is_active": alert.is_active}


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(alert_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    deleted = await delete_alert(db, alert_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/{alert_id}/log")
async def alert_log(alert_id: str, user: User = Depends(get_current_user)):
    """Trigger history for an alert."""
    return []
