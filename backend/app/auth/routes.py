"""
FermaGen AI - Authentication Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.database.database import get_db, User
from app.auth.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth.utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from app.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    
    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    - **role**: student, researcher, scientist, admin, or viewer
    - **organization**: Optional organization name
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        organization=user_data.organization
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(
        data={
            "sub": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password
    
    Returns JWT access token on success
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the current user's profile
    
    Requires valid JWT token in Authorization header
    """
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    full_name: str = None,
    organization: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's profile
    """
    if full_name:
        current_user.full_name = full_name
    if organization:
        current_user.organization = organization
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


from pydantic import BaseModel

class FirebaseAuthRequest(BaseModel):
    """Firebase authentication request"""
    id_token: str
    email: str
    full_name: str = None
    photo_url: str = None


@router.post("/firebase", response_model=Token)
async def firebase_auth(auth_data: FirebaseAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user with Firebase ID token (Google Sign-In)
    
    - Creates new user if doesn't exist
    - Returns JWT token for API access
    """
    import httpx
    
    # Verify Firebase token with Google's API
    # Note: For production, use Firebase Admin SDK for proper verification
    # This is a simplified version that trusts the email from the frontend
    # In production, verify the id_token with Firebase
    
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == auth_data.email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user with Firebase (no password - OAuth user)
            # Use a placeholder hash for OAuth users
            user = User(
                email=auth_data.email,
                password_hash="FIREBASE_OAUTH_USER",  # Marker for OAuth users
                full_name=auth_data.full_name or auth_data.email.split("@")[0],
                role="researcher"
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Generate JWT token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role
            },
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        
        return Token(
            access_token=access_token,
            user=UserResponse.model_validate(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )

