from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class ConfigGroupBase(BaseModel):
    name: str
    description: str
    group_unique_id: str = Field(alias="groupUniqueId")

    class Config:
        from_attributes = True
        populate_by_name = True


# New base class for AddEdit operations where group_unique_id is optional
class ConfigGroupBaseForAddEdit(BaseModel):
    name: str
    description: str
    group_unique_id: Optional[str] = Field(None, alias="groupUniqueId")

    class Config:
        from_attributes = True
        populate_by_name = True


# Properties to receive on ConfigGroup creation
class ConfigGroupCreate(ConfigGroupBase):
    pass


# Properties to receive on ConfigGroup update
class ConfigGroupUpdate(ConfigGroupBaseForAddEdit):
    name: Optional[str] = None
    description: Optional[str] = None
    group_unique_id: Optional[str] = Field(None, alias="groupUniqueId")
    is_deleted: Optional[int] = Field(0, alias="isDeleted")


# Properties shared by models stored in DB
class ConfigGroupInDBBase(ConfigGroupBase):
    id: int
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


# Properties to return to client
class ConfigGroup(ConfigGroupInDBBase):
    pass


# AddEdit schema for ConfigGroup
class ConfigGroupAddEdit(ConfigGroupBaseForAddEdit):
    id: Optional[int] = 0
    is_deleted: Optional[int] = Field(0, alias="isDeleted")


# Shared properties
class GetSpecificConfigGroupRequest(BaseModel):
    id: int


# Shared properties
class ConfigParamBase(BaseModel):
    name: str
    description: str
    config_group_id: int = Field(alias="configGroupId")
    param_unique_id: str = Field(alias="paramUniqueId")

    class Config:
        from_attributes = True
        populate_by_name = True


# New base class for AddEdit operations where param_unique_id is optional
class ConfigParamBaseForAddEdit(BaseModel):
    name: str
    description: str
    config_group_id: int = Field(alias="configGroupId")
    param_unique_id: Optional[str] = Field(None, alias="paramUniqueId")

    class Config:
        from_attributes = True
        populate_by_name = True


# Properties to receive on ConfigParam creation
class ConfigParamCreate(ConfigParamBaseForAddEdit):
    pass


# Properties to receive on ConfigParam update
class ConfigParamUpdate(ConfigParamBaseForAddEdit):
    name: Optional[str] = None
    description: Optional[str] = None
    config_group_id: Optional[int] = Field(None, alias="configGroupId")
    param_unique_id: Optional[str] = Field(None, alias="paramUniqueId")
    is_deleted: Optional[int] = Field(0, alias="isDeleted")


# Properties shared by models stored in DB
class ConfigParamInDBBase(ConfigParamBase):
    id: int
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


# Properties to return to client
class ConfigParam(ConfigParamInDBBase):
    pass


# AddEdit schema for ConfigParam
class ConfigParamAddEdit(ConfigParamBaseForAddEdit):
    id: Optional[int] = 0
    is_deleted: Optional[int] = Field(0, alias="isDeleted")
