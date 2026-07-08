from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# =========================
# Register
# =========================

class RegisterRequest(BaseModel):
    full_name: str = Field(alias="fullName")
    username: str
    email_id: EmailStr = Field(alias="emailId")
    mobile_number: str = Field(alias="mobileNumber")
    password: str
    role_id: Optional[int] = Field(5, alias="roleId")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Login
# =========================

class LoginRequest(BaseModel):
    email_id: EmailStr = Field(alias="emailId")
    password: str
 
    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Login Response
# =========================

class LoginResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    token_type: str = Field(default="Bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Refresh Token
# =========================

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Logout
# =========================

class LogoutRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Forgot Password
# =========================

class ForgotPasswordRequest(BaseModel):
    email_id: EmailStr = Field(alias="emailId")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Verify OTP
# =========================

class VerifyOTPRequest(BaseModel):
    email_id: EmailStr = Field(alias="emailId")
    otp: str

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Reset Password
# =========================

class ResetPasswordRequest(BaseModel):
    email_id: EmailStr = Field(alias="emailId")
    otp: str
    new_password: str = Field(alias="newPassword")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Change Password
# =========================

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(alias="oldPassword")
    new_password: str = Field(alias="newPassword")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# JWT Payload
# =========================

class TokenPayload(BaseModel):
    sub: str
    user_id: int = Field(alias="userId")
    role_id: int = Field(alias="roleId")
    exp: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Current User
# =========================

class CurrentUserResponse(BaseModel):
    id: int
    full_name: str = Field(alias="fullName")
    username: str
    email_id: EmailStr = Field(alias="emailId")
    mobile_number: str = Field(alias="mobileNumber")
    role_id: int = Field(alias="roleId")
    profile_image: Optional[str] = Field(None, alias="profileImage")

    class Config:
        from_attributes = True
        populate_by_name = True

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    profile_image: Optional[str] = Field(None, alias="profileImage")
 
    class Config:
        from_attributes = True
        populate_by_name = True