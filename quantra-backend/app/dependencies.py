"""
Quantra — FastAPI dependency injection.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import get_redis
from app.core.security import verify_access_token
from app.db.session import get_db_session
from app.models.user import User

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


# ── Database Session ────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session (alias for get_db_session)."""
    async for session in get_db_session():
        yield session


# ── Current User ────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate JWT from Authorization header, return User.

    Raises 401 if token is missing, invalid, or user not found.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Like get_current_user but returns None instead of raising 401.

    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# ── Rate Limiter ────────────────────────────────────────────


class RateLimiter:
    """
    Redis-based sliding window rate limiter.

    Usage as a dependency::

        @router.get("/endpoint", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
    """

    def __init__(self, times: int = 60, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = f"ratelimit:{client_ip}:{path}"

        try:
            redis = await get_redis()
            current = await redis.get(key)
            if current is not None and int(current) >= self.times:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {self.seconds} seconds.",
                )
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.seconds)
            await pipe.execute()
        except HTTPException:
            raise
        except Exception as e:
            # If Redis is down, allow the request (graceful degradation)
            logger.warning("Rate limiter Redis error: %s — allowing request", e)
