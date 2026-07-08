from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.schemas.user_master import (
    APIResponse, UserPublic, DataResponse, eResultCode,
    DataRequest, UserMasterAddEdit, UserMasterResponse,
    UserGetSpecific,
)
from app.services.user_service import (
    add_edit_user,
    get_user_by_id,
    get_user_by_email,
    delete_user_service,
    get_all_active_users,
)

router = APIRouter()


# =====================================================
# Add / Edit User
# =====================================================

@router.post("/addEditUser", response_model=APIResponse[UserMasterResponse])
async def add_edit_user_route(
    request: DataRequest[UserMasterAddEdit],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not current_user or not hasattr(current_user, "id"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if request.data.id == 0:
        existing_active_user = await get_user_by_email(db, request.data.email_id, is_deleted=0)
        if existing_active_user:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.BAD_REQUEST,
                    description="User with this email already exists and is active",
                )
            )

    new_user = await add_edit_user(db=db, user_data=request.data)
    if new_user is None:
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.NOT_FOUND,
                description="User not found",
            )
        )

    description = "User updated successfully" if request.data.id != 0 else "User created successfully"

    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description=description,
        ),
        data=new_user,
    )


# =====================================================
# Get Current User
# =====================================================

@router.post("/getCurrentUser", response_model=APIResponse[UserPublic])
async def read_users_me(current_user=Depends(get_current_user)):
    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description="Current user retrieved successfully"
        ),
        data=current_user
    )


# =====================================================
# Get All Users
# =====================================================

@router.post("/getAllUsers", response_model=APIResponse[list[UserMasterResponse]])
async def get_all_active_users_route(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not current_user or not hasattr(current_user, "id"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    users = await get_all_active_users(session=db)
    if not users:
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.NOT_FOUND,
                description="No active users found",
            )
        )
    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description="Active users retrieved successfully",
        ),
        data=[UserMasterResponse.model_validate(user) for user in users],
    )


# =====================================================
# Get Specific User
# =====================================================

@router.post("/getSpecificUser", response_model=APIResponse[UserMasterResponse])
async def get_specific_user_route(
    request: DataRequest[UserGetSpecific],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not current_user or not hasattr(current_user, "id"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = await get_user_by_id(session=db, id=request.data.id)
    if user is None:
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.NOT_FOUND,
                description="User not found",
            )
        )
    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description="User retrieved successfully",
        ),
        data=UserMasterResponse.model_validate(user),
    )


# =====================================================
# Delete User
# =====================================================

@router.post("/deleteUser", response_model=APIResponse)
async def delete_user_route(
    request: DataRequest[UserGetSpecific],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not current_user or not hasattr(current_user, "id"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    deleted_user = await delete_user_service(db=db, user_id=request.data.id, deleted_by=current_user.id)
    if deleted_user is None:
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.NOT_FOUND,
                description="User not found or already deleted",
            )
        )
    return APIResponse(
        dataResponse=DataResponse(
            returnCode=eResultCode.SUCCESS,
            description="User deleted successfully",
        )
    )