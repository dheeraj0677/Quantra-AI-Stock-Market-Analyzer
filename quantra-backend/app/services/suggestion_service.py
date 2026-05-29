"""Quantra — Suggestion service."""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.suggestion import Suggestion

logger = logging.getLogger(__name__)

async def get_user_suggestions(db: AsyncSession, user_id: UUID) -> list[Suggestion]:
    result = await db.execute(
        select(Suggestion).where(Suggestion.user_id == user_id).order_by(desc(Suggestion.generated_at)).limit(10)
    )
    return list(result.scalars().all())

async def mark_suggestion_read(db: AsyncSession, suggestion_id: UUID, user_id: UUID) -> bool:
    result = await db.execute(select(Suggestion).where(Suggestion.id == suggestion_id, Suggestion.user_id == user_id))
    sug = result.scalar_one_or_none()
    if sug:
        sug.is_read = True
        await db.flush()
        return True
    return False
