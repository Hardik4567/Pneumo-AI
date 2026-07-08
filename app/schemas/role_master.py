from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Role specific schemas
class RoleMasterAddEdit(BaseModel):
    id: Optional[int] = 0
    name: str
    description: str
    is_restricted: Optional[int] = Field(0, alias="isRestricted") # Maps to is_restricted in model

class RoleDeleteRequest(BaseModel):
    id: int

class GetSpecificRoleRequest(BaseModel):
    id: int

class RoleResponse(BaseModel):
    id: int
    role_unique_id: str = Field(alias="roleUniqueId")
    name: str
    description: str
    is_restricted: int = Field(alias="isRestricted")
    is_deleted: int = Field(alias="isDeleted")
    created_on: datetime = Field(alias="createdOn")
    created_by: Optional[int] = Field(None, alias="createdBy")
    updated_on: datetime = Field(alias="updatedOn")
    updated_by: Optional[int] = Field(None, alias="updatedBy")
    deleted_on: Optional[datetime] = Field(None, alias="deletedOn")
    deleted_by: Optional[int] = Field(None, alias="deletedBy")

    class Config:
        from_attributes = True
        populate_by_name = True
