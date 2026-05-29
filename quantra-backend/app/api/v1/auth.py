"""
Quantra — Auth API endpoints.

POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
PATCH /auth/preferences
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import delete_session, get_session, set_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PreferencesUpdate,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        risk_profile=payload.risk_profile,
    )
    db.add(user)
    await db.flush()

    # Generate tokens
    token_data = {"sub": str(user.id)}
    access = create_access_token(token_data)
    refresh = create_refresh_token(token_data)

    # Store refresh token in Redis
    await set_session(str(user.id), refresh)

    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email + password."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Update last_login
    user.last_login = datetime.now(UTC)
    await db.flush()

    token_data = {"sub": str(user.id)}
    access = create_access_token(token_data)
    refresh = create_refresh_token(token_data)
    await set_session(str(user.id), refresh)

    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(payload: RefreshRequest):
    """Rotate access + refresh tokens."""
    user_id = verify_refresh_token(payload.refresh_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Verify token matches stored session
    stored = await get_session(user_id)
    if stored != payload.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    token_data = {"sub": user_id}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)
    await set_session(user_id, new_refresh)

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user: User = Depends(get_current_user)):
    """Revoke refresh token (logout)."""
    await delete_session(str(user.id))


@router.get("/me", response_model=UserProfile)
async def get_me(user: User = Depends(get_current_user)):
    """Return current user profile."""
    return UserProfile(
        id=str(user.id),
        email=user.email,
        name=user.name,
        plan=user.plan,
        risk_profile=user.risk_profile,
        preferred_sectors=user.preferred_sectors,
        investment_horizon=user.investment_horizon,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.patch("/preferences", response_model=UserProfile)
async def update_preferences(
    payload: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user investment preferences."""
    if payload.risk_profile is not None:
        user.risk_profile = payload.risk_profile
    if payload.preferred_sectors is not None:
        user.preferred_sectors = payload.preferred_sectors
    if payload.investment_horizon is not None:
        user.investment_horizon = payload.investment_horizon

    await db.flush()

    return UserProfile(
        id=str(user.id),
        email=user.email,
        name=user.name,
        plan=user.plan,
        risk_profile=user.risk_profile,
        preferred_sectors=user.preferred_sectors,
        investment_horizon=user.investment_horizon,
        created_at=user.created_at,
        last_login=user.last_login,
    )
