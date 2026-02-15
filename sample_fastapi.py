# main.py
# Simple FastAPI application for testing breaking change detection
# No database, just in-memory data and simple endpoints

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

app = FastAPI(title="Sample User API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# MODELS (Schemas)
# ============================================

class UserResponse(BaseModel):
    """Response model for user data"""
    id: str
    name: str
    mobile: str  # <- This field will also be removed
    created_at: str

class LoginRequest(BaseModel):
    """Request model for login"""
    password: str

class LoginResponse(BaseModel):
    """Response model for login"""
    success: bool
    token: str  # <- This will be removed in breaking change
    refreshToken: str  # <- This will be removed in breaking change
    expiresIn: int
    user: dict

class CreateUserRequest(BaseModel):
    """Request model for creating user"""
    password: str
    name: str
    mobile: str

# ============================================
# FAKE DATA (In-memory storage)
# ============================================

fake_users_db = {
    "user1": {
        "id": "user1",
        "email": "john@example.com",
        "name": "John Doe",
        "mobile": "+1-234-567-8900",
        "password": "hashed_password_123",
        "created_at": "2024-01-01T10:00:00Z"
    },
    "user2": {
        "id": "user2",
        "email": "jane@example.com",
        "name": "Jane Smith",
        "mobile": "+1-987-654-3210",
        "password": "hashed_password_456",
        "created_at": "2024-01-02T10:00:00Z"
    }
}

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "User API is running",
        "version": "1.0.0",
        "endpoints": [
            "GET /users/{id}",
            "POST /users",
            "POST /login",
            "GET /health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# ============================================
# USER ENDPOINTS
# ============================================

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get user by ID
    
    Returns: UserResponse with id, email, name, mobile, created_at
    
    THIS ENDPOINT IS USED FOR TESTING BREAKING CHANGES
    
    Example breaking changes:
    1. Remove 'email' field -> Frontend fails when displaying email
    2. Remove 'mobile' field -> Frontend fails when displaying mobile
    3. Change response type from object to array
    4. Change email type from string to integer
    """
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = fake_users_db[user_id]
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        mobile=user["mobile"],
        created_at=user["created_at"]
    )

@app.get("/api/users")
async def list_users():
    """
    List all users
    
    Returns: List of UserResponse objects
    """
    return [
        UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            mobile=user["mobile"],
            created_at=user["created_at"]
        )
        for user in fake_users_db.values()
    ]

@app.post("/api/users")
async def create_user(request: CreateUserRequest):
    """
    Create a new user
    
    Body parameters:
    - password: str (required)
    - name: str (required)
    - mobile: str (required)
    
    Returns: UserResponse with all fields including email and mobile
    """
    new_user_id = f"user{len(fake_users_db) + 1}"
    
    new_user = {
        "id": new_user_id,
        "email": request.email,
        "password": request.password,
        "name": request.name,
        "mobile": request.mobile,
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    fake_users_db[new_user_id] = new_user
    
    return UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        name=new_user["name"],
        mobile=new_user["mobile"],
        created_at=new_user["created_at"]
    )

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    
    THIS ENDPOINT IS USED FOR TESTING BREAKING CHANGES
    
    Returns: LoginResponse with token, refreshToken, expiresIn, user
    
    Example breaking changes:
    1. Remove 'token' field -> Frontend can't authenticate
    2. Remove 'refreshToken' field -> Refresh mechanism breaks
    3. Change token format
    4. Remove user object from response
    """
    # Find user
    user = None
    user_id = None
    
    for uid, u in fake_users_db.items():
        if u["email"] == request.email:
            user = u
            user_id = uid
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate fake token
    token = f"token_jwt_{user_id}_{datetime.now().timestamp()}"
    refresh_token = f"refresh_{user_id}_{datetime.now().timestamp()}"
    
    return LoginResponse(
        success=True,
        token=token,
        refreshToken=refresh_token,
        expiresIn=3600,  # 1 hour
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"]
        }
    )

@app.post("/api/refresh-token")
async def refresh_token(refresh_token: str):
    """
    Refresh authentication token
    
    Returns: New token and refresh token
    """
    # Validate refresh token (simplified)
    if not refresh_token.startswith("refresh_"):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_token = f"token_jwt_refreshed_{datetime.now().timestamp()}"
    new_refresh_token = f"refresh_refreshed_{datetime.now().timestamp()}"
    
    return {
        "token": new_token,
        "refreshToken": new_refresh_token,
        "expiresIn": 3600
    }

# ============================================
# PROFILE ENDPOINTS
# ============================================

@app.get("/api/profile")
async def get_profile(token: str):
    """
    Get current user profile
    
    Query parameter: token (authentication token)
    
    Returns: User profile data
    """
    # Simple token validation (in real app, validate JWT)
    if not token.startswith("token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # For demo, return user1
    user = fake_users_db["user1"]
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "mobile": user["mobile"],
        "created_at": user["created_at"],
        "lastLogin": datetime.now().isoformat() + "Z"
    }

# ============================================
# STATUS ENDPOINT (For testing)
# ============================================

@app.get("/api/status")
async def get_status():
    """
    Get API status and info
    
    Used for testing API availability
    """
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat() + "Z",
        "users_count": len(fake_users_db)
    }

# ============================================
# RUN THE APP
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FastAPI server...")
    print("📖 API Docs: http://localhost:8000/docs")
    print("📡 OpenAPI Spec: http://localhost:8000/openapi.json")
    print("\nAvailable endpoints:")
    print("  GET  /                    - Health check")
    print("  GET  /api/users/{id}      - Get user (has email, mobile fields)")
    print("  GET  /api/users           - List all users")
    print("  POST /api/users           - Create user")
    print("  POST /api/login           - Login (returns token, refreshToken)")
    print("  POST /api/refresh-token   - Refresh token")
    print("  GET  /api/profile         - Get user profile")
    print("  GET  /api/status          - API status")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
