# models.py
# Pydantic models for request/response validation

from pydantic import BaseModel
from typing import Optional, Dict, Any


class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    name: str
    mobile: str
    created_at: str


class LoginRequest(BaseModel):
    """Request model for login"""
    mailId: str
    password: str


class LoginResponse(BaseModel):
    """Response model for login"""
    success: bool
    token: str
    refreshToken: str
    expiresIn: int
    user: dict


class CreateUserRequest(BaseModel):
    """Request model for creating user"""
    mailId: str
    password: str
    name: str
    mobile: str


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing token"""
    refresh_token: str
