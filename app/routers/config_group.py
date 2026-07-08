from typing import List, Any
from app.db.database import get_db
from app.models.user_master import UserMaster
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.user_master import APIResponse, DataRequest, DataResponse, eResultCode
from app.schemas.config import ConfigGroup, ConfigGroupAddEdit, GetSpecificConfigGroupRequest
from app.services.config_group_service import (
    add_edit_config_group,
    get_all_config_groups,
    get_config_group_by_id,
    delete_config_group
)

router = APIRouter()


# Create or update config group
@router.post("/addEditConfigGroup", response_model=APIResponse[ConfigGroup])
async def create_update_config_group(
    request: DataRequest[ConfigGroupAddEdit],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
    response: Response = None # Add Response as a dependency
) -> Any:
    """Create new config group or update an existing one."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = current_user.id

    try:
        if request.data.id == 0:
            config_group = await add_edit_config_group(db, request.data, created_by=user_id, updated_by=user_id)
            description = "Config group created successfully."
            response.status_code = status.HTTP_200_OK  # Set 200 for creation as per user request
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.SUCCESS, # Set SUCCESS as per user request
                    description=description,
                ),
                data=ConfigGroup.model_validate(config_group),
            )
        else:
            config_group = await add_edit_config_group(db, request.data, updated_by=user_id)
            description = "Config group updated successfully."
            response.status_code = status.HTTP_200_OK  # Set 200 for update
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.SUCCESS,
                    description=description,
                ),
                data=ConfigGroup.model_validate(config_group),
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



# Get all config groups
@router.post("/getAllConfigGroup", response_model=APIResponse[List[ConfigGroup]])
async def read_config_groups(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
) -> Any:
    """Retrieve config groups."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        config_groups = await get_all_config_groups(db, skip=skip, limit=limit)
        if not config_groups:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description="No config groups found.",
                ),
                data=[],
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Config groups retrieved successfully.",
            ),
            data=[ConfigGroup.model_validate(group) for group in config_groups],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



# get specific config group by id 
@router.post("/getSpecificConfigGroup", response_model=APIResponse[ConfigGroup])
async def read_config_group(
    request: DataRequest[GetSpecificConfigGroupRequest],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
) -> Any:
    """Get specific config group by ID."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    group_id = request.data.id

    try:
        config_group = await get_config_group_by_id(db, group_id)
        if not config_group:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description=f"Config group with ID {group_id} not found.",
                ),
                data=None,
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description=f"Config group with ID {group_id} retrieved successfully.",
            ),
            data=ConfigGroup.model_validate(config_group),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



@router.post("/deleteConfigGroup", response_model=APIResponse[ConfigGroup])
async def delete_config_group_route(
    request: DataRequest[int],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
) -> Any:
    """Delete a config group."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = current_user.id
    group_id = request.data

    try:
        config_group = await delete_config_group(db, group_id, deleted_by=user_id)
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description=f"Config group with ID {group_id} marked as deleted successfully.",
            ),
            data=ConfigGroup.model_validate(config_group),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
