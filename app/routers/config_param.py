from typing import List, Any
from app.db.database import get_db
from app.models.user_master import UserMaster
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user
from app.schemas.config import ConfigParam, ConfigParamAddEdit
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.user_master import APIResponse, DataRequest, DataResponse, eResultCode
from app.services.config_param_service import (
    add_edit_config_param,
    get_all_config_params,
    get_config_param_by_id,
    delete_config_param
)

router = APIRouter()


# Create or update config param
@router.post("/addEditConfigParam", response_model=APIResponse[ConfigParam])
async def create_update_config_param(
    request: DataRequest[ConfigParamAddEdit],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
    response: Response = None # Add Response as a dependency
) -> Any:
    """Create new config param or update an existing one."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = current_user.id

    try:
        if request.data.id == 0:
            config_param = await add_edit_config_param(db, request.data, created_by=user_id, updated_by=user_id)
            description = "Config param created successfully."
            response.status_code = status.HTTP_200_OK  # Set 200 for creation as per user request
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.SUCCESS, # Set SUCCESS as per user request
                    description=description,
                ),
                data=ConfigParam.model_validate(config_param),
            )
        else:
            config_param = await add_edit_config_param(db, request.data, updated_by=user_id)
            description = "Config param updated successfully."
            response.status_code = status.HTTP_200_OK  # Set 200 for update
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.SUCCESS,
                    description=description,
                ),
                data=ConfigParam.model_validate(config_param),
            )
    except ValueError as e:
        if str(e) == "Config Name already exist":
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.CREATED,
                    description=str(e),
                ),
                data=None,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


# Get all config params
@router.post("/getAllConfigParam", response_model=APIResponse[List[ConfigParam]])
async def read_config_params(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
) -> Any:
    """Retrieve config params."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        config_params = await get_all_config_params(db, skip=skip, limit=limit)
        if not config_params:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description="No config params found.",
                ),
                data=[],
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Config params retrieved successfully.",
            ),
            data=[ConfigParam.model_validate(param) for param in config_params],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


# Get specific config param by id
@router.post("/getSpecificConfigParam", response_model=APIResponse[ConfigParam])
async def read_config_param(
    request: DataRequest[int],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
) -> Any:
    """Get specific config param by ID."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    param_id = request.data

    try:
        config_param = await get_config_param_by_id(db, param_id)
        if not config_param:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description=f"Config param with ID {param_id} not found.",
                ),
                data=None,
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description=f"Config param with ID {param_id} retrieved successfully.",
            ),
            data=ConfigParam.model_validate(config_param),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


# Delete config param route
@router.post("/deleteConfigParam", response_model=APIResponse[ConfigParam])
async def delete_config_param_route(
    request: DataRequest[int],
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user),
) -> Any:
    """Delete a config param."""
    if not current_user or not hasattr(current_user, "id") or not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_id = current_user.id
    param_id = request.data

    try:
        config_param = await delete_config_param(db, param_id, deleted_by=user_id)
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description=f"Config param with ID {param_id} marked as deleted successfully.",
            ),
            data=ConfigParam.model_validate(config_param),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
