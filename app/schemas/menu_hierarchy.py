from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MenuHierarchyBase(BaseModel):
    name: str
    disp_name: str = Field(alias="dispName")
    parent_id: Optional[int] = Field(None, alias="parentId")
    parent_unique_id: Optional[str] = Field(None, alias="parentUniqueId")
    entity_url: str = Field(alias="entityUrl")
    menu_icon: Optional[str] = Field(None, alias="menuIcon")
    description: Optional[str] = None
    is_active: int = Field(alias="isActive")
    enable_for_others: Optional[int] = Field(None, alias="enableForOthers")
    icon_name: Optional[str] = Field(None, alias="iconName") 
    display_order: Optional[int] = Field(None, alias="displayOrder")
    menu_unique_id: Optional[str] = Field(None, alias="menuUniqueId")
    request_date_time: Optional[datetime] = Field(None, alias="requestDateTime")
    request_source: Optional[int] = Field(None, alias="requestSource")
    is_deleted: int = Field(alias="isDeleted")
    created_on: Optional[datetime] = Field(None, alias="createdOn")
    created_by: Optional[int] = Field(None, alias="createdBy")
    updated_on: Optional[datetime] = Field(None, alias="updatedOn")
    updated_by: Optional[int] = Field(None, alias="updatedBy")
    deleted_on: Optional[datetime] = Field(None, alias="deletedOn")
    deleted_by: Optional[int] = Field(None, alias="deletedBy")

    class Config:
        from_attributes = True
        populate_by_name = True

class MenuHierarchyCreate(MenuHierarchyBase):
    pass

class MenuHierarchyUpdate(MenuHierarchyBase):
    pass

class MenuHierarchySchema(MenuHierarchyBase):
    id: int

    class Config:
        from_attributes = True

class PrivilegeSchema(BaseModel):
    id: int
    privilege_unique_id: str = Field(alias="privilegeUniqueId")
    name: str
    description: str
    menu_id: int = Field(alias="menuId")
    is_deleted: int = Field(alias="isDeleted")
    created_on: Optional[datetime] = Field(None, alias="createdOn")
    created_by: Optional[int] = Field(None, alias="createdBy")
    updated_on: Optional[datetime] = Field(None, alias="updatedOn")
    updated_by: Optional[int] = Field(None, alias="updatedBy")
    deleted_on: Optional[datetime] = Field(None, alias="deletedOn")
    deleted_by: Optional[int] = Field(None, alias="deletedBy")

    class Config:
        from_attributes = True
        populate_by_name = True

