from pydantic import BaseModel, EmailStr, validator, datetime
from typing import Optional

#Schema for user registration
class UserCreate(BaseModel):
    username: str
    email: EmailStr  #Validates email format automatically!
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

#Schema for login request
class UserLogin(BaseModel):
    username: str
    password: str

#Schema for returning user info (NO PASSWORD!)
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

#Schema for login response (includes token)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Schema for token data (stored in JWT)
class TokenData(BaseModel):
    user_id: Optional[str] = None