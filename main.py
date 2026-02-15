# main.py
# FastAPI application for testing breaking change detection
# Clean, modular structure with separated concerns

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from models import (
    UserResponse,
    LoginRequest,
    LoginResponse,
    CreateUserRequest,
    RefreshTokenRequest
)
from database import fake_users_db

# ============================================
# APP INITIALIZATION
# ============================================

app = FastAPI(
    title="Sample User API",
    version="1.0.0",
    description="API for testing breaking change detection"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH CHECK ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API health check"""
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
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


@app.get("/api/status")
async def get_status():
    """Get API status and metadata"""
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat() + "Z",
        "users_count": len(fake_users_db)
    }

# ============================================
# USER ENDPOINTS
# ============================================

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get user by ID
    
    Returns: UserResponse with id, gmail, name, phone, created_at
    
    THIS ENDPOINT IS USED FOR TESTING BREAKING CHANGES
    
    Example breaking changes:
    1. Remove 'gmail' field -> Frontend fails when displaying gmail
    2. Remove 'phone' field -> Frontend fails when displaying phone
    3. Change response type from object to array
    4. Change gmail type from string to integer
    """
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = fake_users_db[user_id]
    return UserResponse(
        id=user["id"],
        gmail=user["gmail"],
        name=user["name"],
        phone=user["phone"],
        created_at=user["created_at"]
    )


@app.get("/api/users")
async def list_users():
    """
    List all users in the system
    
    Returns: List of UserResponse objects
    """
    return [
        UserResponse(
            id=user["id"],
            gmail=user["gmail"],
            name=user["name"],
            phone=user["phone"],
            created_at=user["created_at"]
        )
        for user in fake_users_db.values()
    ]


@app.post("/api/users")
async def create_user(request: CreateUserRequest):
    """
    Create a new user
    
    Body parameters:
    - gmail: str (required)
    - password: str (required)
    - name: str (required)
    - phone: str (required)
    
    Returns: UserResponse with all fields
    """
    new_user_id = f"user{len(fake_users_db) + 1}"
    
    new_user = {
        "id": new_user_id,
        "gmail": request.gmail,
        "password": request.password,
        "name": request.name,
        "phone": request.phone,
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    fake_users_db[new_user_id] = new_user
    
    return UserResponse(
        id=new_user["id"],
        gmail=new_user["gmail"],
        name=new_user["name"],
        phone=new_user["phone"],
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
    # Find user by gmail
    user = None
    user_id = None
    
    for uid, u in fake_users_db.items():
        if u["gmail"] == request.gmail:
            user = u
            user_id = uid
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Validate password
    if user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate fake tokens
    token = f"token_jwt_{user_id}_{datetime.now().timestamp()}"
    refresh_token = f"refresh_{user_id}_{datetime.now().timestamp()}"
    
    return LoginResponse(
        success=True,
        token=token,
        refreshToken=refresh_token,
        expiresIn=3600,  # 1 hour
        user={
            "id": user["id"],
            "gmail": user["gmail"],
            "name": user["name"]
        }
    )


@app.post("/api/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh authentication token
    
    Body parameter:
    - refresh_token: str (required)
    
    Returns: New token and refresh token
    """
    # Validate refresh token (simplified)
    if not request.refresh_token.startswith("refresh_"):
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
        "gmail": user["gmail"],
        "name": user["name"],
        "phone": user["phone"],
        "created_at": user["created_at"],
        "lastLogin": datetime.now().isoformat() + "Z"
    }

# ============================================
# SERVER STARTUP
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FastAPI server...")
    print("📖 API Docs: http://localhost:8000/docs")
    print("📡 OpenAPI Spec: http://localhost:8000/openapi.json")
    print("\nAvailable endpoints:")
    print("  GET  /                    - Health check")
    print("  GET  /health              - Health status")
    print("  GET  /api/status          - API status")
    print("  GET  /api/users/{id}      - Get user by ID")
    print("  GET  /api/users           - List all users")
    print("  POST /api/users           - Create new user")
    print("  POST /api/login           - User login")
    print("  POST /api/refresh-token   - Refresh authentication token")
    print("  GET  /api/profile         - Get user profile")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
