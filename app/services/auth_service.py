from datetime import datetime, timezone
import random

from fastapi import HTTPException, status

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_master import UserMaster
from app.models.user_token import UserToken

from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    VerifyOTPRequest,
    UpdateProfileRequest
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

class AuthService:

    # =====================================================
    # Generate OTP
    # =====================================================

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    # =====================================================
    # Register
    # =====================================================

    @staticmethod
    async def register(
        db: AsyncSession,
        request: RegisterRequest
    ):

        email = await db.execute(
            select(UserMaster).where(
                UserMaster.email_id == request.email_id
            )
        )

        if email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        username = await db.execute(
            select(UserMaster).where(
                UserMaster.username == request.username
            )
        )

        if username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        mobile = await db.execute(
            select(UserMaster).where(
                UserMaster.mobile_number == request.mobile_number
            )
        )

        if mobile.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mobile number already exists"
            )

        user = UserMaster(
            role_id=5,
            full_name=request.full_name,
            username=request.username,
            email_id=request.email_id,
            mobile_number=request.mobile_number,
            password_hash=hash_password(request.password),
            email_verified=0,
            is_active=1,
            failed_login_attempts=0,
        )

        db.add(user)

        await db.commit()
        await db.refresh(user)

        otp = AuthService.generate_otp()

        token = UserToken(
            user_id=user.id,
            otp=otp
        )

        db.add(token)

        await db.commit()

        # TODO
        # send otp email here

        return {
            "message": "Registration successful",
            "userId": user.id
        }

    # =====================================================
    # Login
    # =====================================================

    @staticmethod
    async def login(
        db: AsyncSession,
        request: LoginRequest
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.email_id == request.email_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email"
            )

        if user.is_active == 0:

            raise HTTPException(
                status_code=403,
                detail="Account disabled"
            )

        if not verify_password(
             request.password,
             user.password_hash
            ):
             user.failed_login_attempts += 1
             await db.commit()

             raise HTTPException(
             status_code=401,
             detail="Invalid password"
            )

        user.failed_login_attempts = 0

        user.last_login = datetime.now(timezone.utc)

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email_id
            }
        )

        refresh_token = create_refresh_token(
            {
                "sub": str(user.id)
            }
        )

        old_token = await db.execute(
            select(UserToken).where(
                UserToken.user_id == user.id
            )
        )

        token = old_token.scalar_one_or_none()

        if token:

            token.token = refresh_token

        else:

            token = UserToken(
                user_id=user.id,
                otp="000000",
                token=refresh_token
            )

            db.add(token)

        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": {
                "id": user.id,
                "fullName": user.full_name,
                "username": user.username,
                "emailId": user.email_id,
                "mobileNumber": user.mobile_number,
                "roleId": user.role_id,
                "profileImage": user.profile_image,
                "emailVerified": user.email_verified,
                "lastLogin": user.last_login.isoformat() if user.last_login else None,
            }
        }
    
    # =====================================================
    # Refresh Token
    # =====================================================

    @staticmethod
    async def refresh_token(
        db: AsyncSession,
        request: RefreshTokenRequest
    ):

        payload = decode_token(request.refresh_token)

        if not payload:

            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        user_id = int(payload.get("sub"))

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        token_result = await db.execute(
            select(UserToken).where(
                UserToken.user_id == user.id,
                UserToken.token == request.refresh_token
            )
        )

        token = token_result.scalar_one_or_none()

        if not token:

            raise HTTPException(
                status_code=401,
                detail="Refresh token expired"
            )

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email_id
            }
        )

        return {
            "accessToken": access_token,
            "tokenType": "Bearer"
        }

    # =====================================================
    # Logout
    # =====================================================

    @staticmethod
    async def logout(
        db: AsyncSession,
        user_id: int
    ):

        await db.execute(
            delete(UserToken).where(
                UserToken.user_id == user_id
            )
        )

        await db.commit()

        return {
            "message": "Logout successful"
        }

    # =====================================================
    # Forgot Password
    # =====================================================

    @staticmethod
    async def forgot_password(
        db: AsyncSession,
        request: ForgotPasswordRequest
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.email_id == request.email_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        otp = AuthService.generate_otp()

        token_result = await db.execute(
            select(UserToken).where(
                UserToken.user_id == user.id
            )
        )

        token = token_result.scalar_one_or_none()

        if token:

            token.otp = otp

        else:

            token = UserToken(
                user_id=user.id,
                otp=otp
            )

            db.add(token)

        await db.commit()

        # TODO
        # Send OTP email here

        return {
            "message": "OTP sent successfully"
        }

    # =====================================================
    # Verify OTP
    # =====================================================

    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        request: VerifyOTPRequest
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.email_id == request.email_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        token_result = await db.execute(
            select(UserToken).where(
                UserToken.user_id == user.id
            )
        )

        token = token_result.scalar_one_or_none()

        if not token:

            raise HTTPException(
                status_code=404,
                detail="OTP not found"
            )

        if token.otp != request.otp:

            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        return {
            "message": "OTP verified successfully"
        }
    
    # =====================================================
    # Reset Password
    # =====================================================

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        request: ResetPasswordRequest
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.email_id == request.email_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        token_result = await db.execute(
            select(UserToken).where(
                UserToken.user_id == user.id
            )
        )

        token = token_result.scalar_one_or_none()

        if not token:

            raise HTTPException(
                status_code=404,
                detail="OTP not found"
            )

        if token.otp != request.otp:

            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        user.password_hash = hash_password(
            request.new_password
        )

        token.otp = None

        await db.commit()

        return {
            "message": "Password reset successfully"
        }

    # =====================================================
    # Change Password
    # =====================================================

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: int,
        request: ChangePasswordRequest
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if not verify_password(
            request.old_password,
            user.password_hash
        ):

            raise HTTPException(
                status_code=400,
                detail="Old password is incorrect"
            )

        user.password_hash = hash_password(
            request.new_password
        )

        await db.commit()

        return {
            "message": "Password changed successfully"
        }

    # =====================================================
    # Get Profile
    # =====================================================

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user

    # =====================================================
    # Update Profile
    # =====================================================

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: int,
        request: UpdateProfileRequest
    ):

        result = await db.execute(
            select(UserMaster).where(
                UserMaster.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if request.full_name is not None:
            user.full_name = request.full_name

        if request.mobile_number is not None:
            user.mobile_number = request.mobile_number

        if request.profile_image is not None:
            user.profile_image = request.profile_image

        await db.commit()

        await db.refresh(user)

        return user