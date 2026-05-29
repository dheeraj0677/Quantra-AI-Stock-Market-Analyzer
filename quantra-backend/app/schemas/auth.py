"""
Pydantic v2 schemas — Auth.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str | None = None
    risk_profile: str = Field(default="moderate", pattern="^(conservative|moderate|aggressive)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    id: str
    email: str
    name: str | None = None
    plan: str
    risk_profile: str
    preferred_sectors: list[str] | None = None
    investment_horizon: str
    created_at: datetime
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class PreferencesUpdate(BaseModel):
    risk_profile: str | None = Field(
        default=None, pattern="^(conservative|moderate|aggressive)$"
    )
    preferred_sectors: list[str] | None = None
    investment_horizon: str | None = Field(
        default=None, pattern="^(short|medium|long)$"
    )
