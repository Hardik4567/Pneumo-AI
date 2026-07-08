from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query
)

from fastapi.responses import FileResponse
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_master import UserMaster
from app.core.dependencies import get_current_user

from app.schemas.user_master import (
    APIResponse,
    DataResponse,
    eResultCode
)

from app.schemas.history_schema import (
    HistoryCreate,
    HistoryUpdate,
    HistoryResponse
)

from app.services.history_service import (
    create_history_service,
    get_all_history_service,
    get_history_by_id_service,
    update_history_service,
    delete_history_service,
    export_history_pdf_service
)

router = APIRouter(
    prefix="/history",
    tags=["History"]
)


# ------------------------------------------------------------------
# Create History
# ------------------------------------------------------------------
@router.post(
    "",
    response_model=APIResponse[HistoryResponse]
)
async def create_history(
    request: HistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    try:
        request.user_id = current_user.id
        history = await create_history_service(db=db, request=request)
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="History created successfully."
            ),
            data=history
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ------------------------------------------------------------------
# Get All History — scoped to current user
# ------------------------------------------------------------------
@router.get(
    "",
    response_model=APIResponse[list[HistoryResponse]]
)
async def get_all_history(
    patient_name: Optional[str] = Query(None),
    detected_disease: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sort_by: str = Query("newest"),
    sort_confidence: str | None = Query(None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    try:
        history = await get_all_history_service(
            db=db,
            user_id=current_user.id,  # always scope to current user
            patient_name=patient_name,
            detected_disease=detected_disease,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_confidence=sort_confidence,
            limit=limit,
            offset=offset,
        )
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="History retrieved successfully."
            ),
            data=history
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ------------------------------------------------------------------
# Export PDF — scoped to current user
# ------------------------------------------------------------------
@router.get("/export/pdf")
async def export_history_pdf(
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    pdf_path = await export_history_pdf_service(db=db, user_id=current_user.id)
    return FileResponse(
        path=pdf_path,
        filename="history_report.pdf",
        media_type="application/pdf"
    )


# ------------------------------------------------------------------
# Get History By ID — ownership check
# ------------------------------------------------------------------
@router.get(
    "/{history_id}",
    response_model=APIResponse[HistoryResponse]
)
async def get_history_by_id(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    try:
        history = await get_history_by_id_service(db, history_id)
        if history is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found.")
        if history.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="History retrieved successfully."
            ),
            data=history
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ------------------------------------------------------------------
# Update History — ownership check
# ------------------------------------------------------------------
@router.put(
    "/{history_id}",
    response_model=APIResponse[HistoryResponse]
)
async def update_history(
    history_id: int,
    request: HistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    try:
        history = await get_history_by_id_service(db, history_id)
        if history is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found.")
        if history.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        updated = await update_history_service(db=db, history_id=history_id, request=request)
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="History updated successfully."
            ),
            data=updated
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ------------------------------------------------------------------
# Delete History — ownership check
# ------------------------------------------------------------------
@router.delete(
    "/{history_id}",
    response_model=APIResponse[None]
)
async def delete_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    try:
        history = await get_history_by_id_service(db, history_id)
        if history is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found.")
        if history.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        await delete_history_service(db, history_id)
        return APIResponse(
            dataResponse=DataResponse(
                returnCode=eResultCode.SUCCESS,
                description="History deleted successfully."
            ),
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))