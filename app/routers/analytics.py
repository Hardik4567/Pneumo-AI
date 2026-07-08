from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user_master import UserMaster
from app.core.dependencies import get_current_user
from app.services.analytics_service import get_analytics_data

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/")
async def analytics(
    db: AsyncSession = Depends(get_db),
    current_user: UserMaster = Depends(get_current_user)
):
    """
    Returns analytics data for the logged-in user.
    """
    try:
        return await get_analytics_data(
            db=db,
            user_id=current_user.id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )