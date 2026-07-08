from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_master import UserMaster
from app.core.dependencies import get_current_user
from app.services.report_service import ReportService

router = APIRouter()


# =====================================================
# Generate / Download Report By History ID
# =====================================================

@router.get("/download/{history_id}")
async def download_report(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    """
    Generate (or re-generate) a PDF report for a specific prediction history.
    Scoped to the currently authenticated user — cannot access other users' reports.
    """
    try:
        result = await ReportService.generate_report(
            db=db,
            history_id=history_id,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =====================================================
# Generate Latest Report
# =====================================================

@router.get("/latest")
async def download_latest_report(
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    """
    Generate a PDF report for the authenticated user's most recent prediction.
    """
    try:
        result = await ReportService.generate_latest_report(
            db=db,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )