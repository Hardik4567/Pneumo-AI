from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user_master import UserMaster

from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    UpdateProfileRequest,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =====================================================
# Register
# =====================================================

@router.post("/register")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.register(db, request)


# =====================================================
# Login
# =====================================================

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):

    request = LoginRequest(
        email_id=form_data.username,
        password=form_data.password
    )

    return await AuthService.login(db, request)


# =====================================================
# Refresh Token
# =====================================================

@router.post("/refresh-token")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.refresh_token(db, request)


# =====================================================
# Logout
# =====================================================

@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    return await AuthService.logout(db, current_user.id)


# =====================================================
# Forgot Password
# =====================================================

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.forgot_password(db, request)


# =====================================================
# Verify OTP
# =====================================================

@router.post("/verify-otp")
async def verify_otp(
    request: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.verify_otp(db, request)


# =====================================================
# Reset Password
# =====================================================

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.reset_password(db, request)


# =====================================================
# Change Password
# =====================================================

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    return await AuthService.change_password(
        db,
        current_user.id,   # ← FIXED: was current_user.user_id (AttributeError)
        request
    )


# =====================================================
# Get Profile
# =====================================================

@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    return await AuthService.get_profile(db, current_user.id)


# =====================================================
# Update Profile
# =====================================================

@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    return await AuthService.update_profile(db, current_user.id, request)
