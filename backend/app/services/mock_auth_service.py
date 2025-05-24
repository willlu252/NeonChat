"""Mock authentication service for testing without database"""
from typing import Dict, Any
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import uuid

# Mock user data
MOCK_USERS = {
    "test@example.com": {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "password": "$2b$12$KIkxE3kJ7vGMn5XD2uY0LuVjgZ6Fz5Gp5vJQkN8jX2zQ5X5X5X5X5",  # "password"
        "full_name": "Test User",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
}

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "mock-secret-key-for-testing-only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class MockAuthService:
    """Mock authentication service that works without a database"""
    
    def __init__(self):
        # Hash the password "password" for the test user
        MOCK_USERS["test@example.com"]["password"] = pwd_context.hash("password")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mock user"""
        email = user_data.get("email")
        
        # Check if user already exists
        if email in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "email": email,
            "password": pwd_context.hash(user_data.get("password", "password")),
            "full_name": user_data.get("full_name", ""),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        MOCK_USERS[email] = new_user
        
        # Return user without password
        user_response = new_user.copy()
        del user_response["password"]
        
        return {
            "user": user_response,
            "session": {
                "access_token": self.create_access_token({"sub": user_id, "email": email}),
                "token_type": "bearer"
            }
        }
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a mock user"""
        user = MOCK_USERS.get(email)
        
        if not user:
            return None
        
        if not self.verify_password(password, user["password"]):
            return None
        
        # Return user without password
        user_response = user.copy()
        del user_response["password"]
        
        return {
            "user": user_response,
            "session": {
                "access_token": self.create_access_token({"sub": user["id"], "email": email}),
                "token_type": "bearer"
            }
        }
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and return access token"""
        user_data = await self.authenticate_user(email, password)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = self.create_access_token(
            data={
                "sub": user_data["user"]["id"],
                "email": user_data["user"]["email"]
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("email")
            
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = MOCK_USERS.get(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Return user without password
            user_response = user.copy()
            del user_response["password"]
            return user_response
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Global instance
mock_auth_service = MockAuthService()