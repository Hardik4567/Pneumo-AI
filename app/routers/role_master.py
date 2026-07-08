from typing import List
from app.db.database import get_db
from app.services import role_service
from app.models.user_master import UserMaster
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user 
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_master import APIResponse, DataRequest, DataResponse, eResultCode
from app.schemas.role_master import (
    RoleMasterAddEdit, RoleDeleteRequest, RoleResponse, GetSpecificRoleRequest
)

router = APIRouter()


@router.post("/addEditRole", response_model=APIResponse[RoleResponse])
async def add_edit_role_route(
    request: DataRequest[RoleMasterAddEdit],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
):
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = current_user.id

    try:
        if request.data.id == 0:
            new_role = await role_service.add_edit_role(
                db=db, role_data=request.data, created_by=user_id, updated_by=user_id
            )
            description = "Role created successfully"
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.CREATED,
                    description=description,
                ),
                data=RoleResponse.model_validate(new_role),
            )
        else:
            updated_role = await role_service.add_edit_role(
                db=db, role_data=request.data, updated_by=user_id
            )
            description = "Role updated successfully"
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.SUCCESS,
                    description=description,
                ),
                data=RoleResponse.model_validate(updated_role),
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



@router.post("/deleteRole", response_model=APIResponse)
async def delete_role_route(
    request: DataRequest[RoleDeleteRequest],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
):
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = current_user.id

    try:
        deleted_role = await role_service.delete_role(
            db=db, role_id=request.data.id, deleted_by=user_id
        )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description=f"Role with ID {deleted_role.id} marked as deleted successfully.",
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



@router.post("/getRoleList", response_model=APIResponse[List[RoleResponse]])
async def get_role_list_route(
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user), 
):
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        roles = await role_service.get_all_roles(db)
        if not roles:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description="No roles found.",
                ),
                data=[],
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Roles retrieved successfully.",
            ),
            data=[RoleResponse.model_validate(role) for role in roles],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



@router.post("/getSpecificRole", response_model=APIResponse[RoleResponse])
async def get_specific_role_route(
    request: DataRequest[GetSpecificRoleRequest],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user), 
):
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    role_id = request.data.id

    try:
        role = await role_service.get_role_by_id(db, role_id)
        if not role:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description=f"Role with ID {role_id} not found.",
                ),
                data=None,
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description=f"Role with ID {role_id} retrieved successfully.",
            ),
            data=RoleResponse.model_validate(role),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
