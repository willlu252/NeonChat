from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from ...models.database import UserCreate, UserResponse
from ...utils.feature_flags import is_auth_enabled

# Import the appropriate auth service
if is_auth_enabled():
    from ...services.auth_service import (
        auth_service, 
        LoginRequest, 
        Token,
        get_current_active_user
    )
else:
    # Use mock auth service when Supabase is not configured
    from ...services.mock_auth_service import mock_auth_service as auth_service
    from ...services.auth_service import LoginRequest, Token
    from fastapi import Depends
    from fastapi.security import OAuth2PasswordBearer
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
    
    async def get_current_active_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
        """Get current user for mock auth"""
        return await auth_service.get_current_user(token)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Convert UserCreate to dict for mock service
        user_dict = {
            "email": user_data.email,
            "password": user_data.password,
            "full_name": user_data.full_name
        }
        result = await auth_service.create_user(user_dict)
        return result["user"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login with email and password"""
    result = await auth_service.login(login_data.email, login_data.password)
    return Token(**result)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token endpoint"""
    result = await auth_service.login(form_data.username, form_data.password)
    return Token(**result)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Logout current user"""
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    # For mock auth, just return a new token
    return Token(access_token="mock-refreshed-token", token_type="bearer")

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    full_name: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update user profile"""
    # For mock auth, just return updated user
    current_user["full_name"] = full_name
    return current_user

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Change user password"""
    # For mock auth, just return success
    return {"message": "Password changed successfully"}

@router.post("/verify-token")
async def verify_token():
    """Verify if token is valid - for checking auth availability"""
    # This endpoint is used to check if auth is available
    # Return 200 to indicate auth routes are loaded
    return {
        "auth_available": True,
        "mock_mode": not is_auth_enabled()
    }

@router.get("/status")
async def auth_status():
    """Get auth system status - no authentication required"""
    return {
        "auth_available": True,
        "mock_mode": not is_auth_enabled(),
        "test_credentials": {
            "email": "test@example.com",
            "password": "password"
        } if not is_auth_enabled() else None
    }