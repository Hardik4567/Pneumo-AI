from typing import List
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import menu_hierarchy_service
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_master import APIResponse, DataResponse, eResultCode
from app.schemas.menu_hierarchy import MenuHierarchySchema, PrivilegeSchema

router = APIRouter()

@router.post("/getMenuHierarchy", response_model=APIResponse[List[MenuHierarchySchema]], tags=["Menu Hierarchy"])
async def get_menu_hierarchy(
    db: AsyncSession = Depends(get_db)
):
    try:
        menu_items = await menu_hierarchy_service.get_all_active_menu_hierarchy(db=db)
        if not menu_items:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description="No menu hierarchy found.",
                ),
                data=[],
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Menu hierarchy retrieved successfully.",
            ),
            data=[MenuHierarchySchema.model_validate(item) for item in menu_items],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.post("/getAllPrivileges", response_model=APIResponse[List[PrivilegeSchema]], tags=["Privileges"])
async def get_all_privileges_route(
    db: AsyncSession = Depends(get_db)
):
    try:
        privileges = await menu_hierarchy_service.get_all_privileges(db=db)
        if not privileges:
            return APIResponse(
                dataResponse=DataResponse(
                    returnCode=eResultCode.NO_DATA_FOUND,
                    description="No privileges found.",
                ),
                data=[],
            )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="Privileges retrieved successfully.",
            ),
            data=[PrivilegeSchema.model_validate(privilege) for privilege in privileges],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")



