"""Quantra — Alert service."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert

logger = logging.getLogger(__name__)

async def get_user_alerts(db: AsyncSession, user_id: UUID) -> list[Alert]:
    result = await db.execute(select(Alert).where(Alert.user_id == user_id))
    return list(result.scalars().all())

async def create_alert(db: AsyncSession, user_id: UUID, data: dict) -> Alert:
    alert = Alert(user_id=user_id, **data)
    db.add(alert)
    await db.flush()
    return alert

async def delete_alert(db: AsyncSession, alert_id: UUID, user_id: UUID) -> bool:
    result = await db.execute(select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id))
    alert = result.scalar_one_or_none()
    if alert:
        await db.delete(alert)
        return True
    return False
