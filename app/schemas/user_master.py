from enum import Enum
from datetime import datetime
from typing import Optional, TypeVar, Generic

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# =========================
# User Create
# =========================

class UserCreate(BaseModel):
    full_name: str = Field(alias="fullName")
    username:  Optional[str] = None
    email_id: EmailStr = Field(alias="emailId")
    mobile_number: str = Field(alias="mobileNumber")
    password: str
    role_id: int = Field(alias="roleId")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# User Update
# =========================

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias="fullName")
    username: Optional[str] = None
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    profile_image: Optional[str] = Field(None, alias="profileImage")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# User Add/Edit
# =========================

class UserMasterAddEdit(BaseModel):
    id: int = 0
    full_name: str = Field(alias="fullName")
    username: str
    email_id: EmailStr = Field(alias="emailId")
    mobile_number: str = Field(alias="mobileNumber")
    password: Optional[str] = None
    role_id: int = Field(alias="roleId")
    profile_image: Optional[str] = Field(None, alias="profileImage")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Public User
# =========================

class UserPublic(BaseModel):
    id: int
    full_name: str = Field(alias="fullName")
    username: str
    email_id: EmailStr = Field(alias="emailId")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# User Profile
# =========================

class UserProfile(BaseModel):
    id: int
    full_name: str = Field(alias="fullName")
    username: str
    email_id: EmailStr = Field(alias="emailId")
    mobile_number: str = Field(alias="mobileNumber")
    profile_image: Optional[str] = Field(None, alias="profileImage")
    role_id: int = Field(alias="roleId")
    email_verified: int = Field(alias="emailVerified")
    last_login: Optional[datetime] = Field(None, alias="lastLogin")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# User Response
# =========================

class UserMasterResponse(BaseModel):
    id: int
    role_id: int = Field(alias="roleId")

    full_name: str = Field(alias="fullName")
    username: str
    email_id: EmailStr = Field(alias="emailId")
    mobile_number: str = Field(alias="mobileNumber")

    profile_image: Optional[str] = Field(None, alias="profileImage")

    is_active: int = Field(alias="isActive")
    is_deleted: int = Field(alias="isDeleted")
    email_verified: int = Field(alias="emailVerified")
    failed_login_attempts: int = Field(alias="failedLoginAttempts")

    created_on: datetime = Field(alias="createdOn")
    created_by: Optional[int] = Field(None, alias="createdBy")

    updated_on: Optional[datetime] = Field(None, alias="updatedOn")
    updated_by: Optional[int] = Field(None, alias="updatedBy")

    deleted_on: Optional[datetime] = Field(None, alias="deletedOn")
    deleted_by: Optional[int] = Field(None, alias="deletedBy")

    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    account_locked_until: Optional[datetime] = Field(None, alias="accountLockedUntil")

    class Config:
        from_attributes = True
        populate_by_name = True


# =========================
# Get Specific User
# =========================

class UserGetSpecific(BaseModel):
    id: int



# =========================
# Generic Request Wrapper
# =========================

T = TypeVar("T")


class DataRequest(BaseModel, Generic[T]):
    data: T


# =========================
# Result Codes
# =========================

class eResultCode(Enum):
    SUCCESS = 0
    DB_ERROR = 1
    NO_DATA_FOUND = 2
    AUTHENTICATION_FAILED = 3
    UNAUTHORIZED = 4
    UNKNOWN = 5
    INVALID_LOGIN_ID = 6
    INVALID_PASSWORD = 7
    SERVICE_ERROR = 8
    INVALID_REQUEST = 9
    NOT_FOUND = 10
    NETWORK_ERRORSERVEERROR = 11
    CREATED = 12
    INTERNAL_SERVEERROR = 13
    UNUSED = 14
    MULTIPLE_RECORDS = 15
    BAD_REQUEST = 16
    R_DUPLICATE = 25
    OTP_INVALID = 26


# =========================
# API Response Wrapper
# =========================

class DataResponse(BaseModel):
    returnCode: eResultCode
    responseDateTime: datetime = Field(default_factory=datetime.now)
    description: str


class APIResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataResponse: DataResponse
    data: Optional[T] = None
