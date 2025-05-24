import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv
from ..utils.supabase_client import supabase_client
from ..models.database import UserCreate, UserResponse

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthService:
    def __init__(self):
        self.supabase = supabase_client.get_client() if supabase_client else None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Create a new user"""
        if not self.supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is not configured"
            )
        
        try:
            # Create user in Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if auth_response.user:
                # Create profile in database
                profile_data = {
                    "id": auth_response.user.id,
                    "email": user_data.email,
                    "full_name": user_data.full_name
                }
                
                profile_response = self.supabase.table("profiles").insert(profile_data).execute()
                
                return {
                    "user": profile_response.data[0],
                    "session": auth_response.session
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user"""
        try:
            # Sign in with Supabase Auth
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user and auth_response.session:
                # Get user profile
                profile_response = self.supabase.table("profiles")\
                    .select("*")\
                    .eq("id", auth_response.user.id)\
                    .single()\
                    .execute()
                
                return {
                    "user": profile_response.data,
                    "session": auth_response.session
                }
            else:
                return None
                
        except Exception as e:
            return None
    
    async def login(self, login_data: LoginRequest) -> Token:
        """Login user and return access token"""
        user_data = await self.authenticate_user(login_data.email, login_data.password)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={
                "sub": user_data["user"]["id"],
                "email": user_data["user"]["email"]
            },
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
        """Get current user from token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None:
                raise credentials_exception
                
            token_data = TokenData(user_id=user_id, email=email)
            
        except JWTError:
            raise credentials_exception
        
        # Get user from database
        user_response = self.supabase.table("profiles")\
            .select("*")\
            .eq("id", token_data.user_id)\
            .single()\
            .execute()
        
        if not user_response.data:
            raise credentials_exception
            
        return user_response.data
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        try:
            # Refresh session with Supabase
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if auth_response.session:
                # Create new JWT token
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = self.create_access_token(
                    data={
                        "sub": auth_response.user.id,
                        "email": auth_response.user.email
                    },
                    expires_delta=access_token_expires
                )
                
                return Token(access_token=access_token, token_type="bearer")
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
    
    async def logout(self, token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
        """Logout user"""
        try:
            # Sign out from Supabase
            self.supabase.auth.sign_out()
            return {"message": "Successfully logged out"}
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to logout"
            )

# Global instance
auth_service = AuthService()

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    return await auth_service.get_current_user(token)

# Dependency to get current active user
async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user