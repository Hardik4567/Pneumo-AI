from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import History
from app.models.user_master import UserMaster

from app.utils.pdf_generator import generate_prediction_report


class ReportService:

    @staticmethod
    async def generate_report(
        db: AsyncSession,
        history_id: int,
        user_id: int
    ):

        result = await db.execute(
            select(History).where(
                History.history_id == history_id,
                History.user_id == user_id
            )
        )

        history = result.scalar_one_or_none()

        if history is None:
            raise Exception("Prediction history not found.")

        user_result = await db.execute(
            select(UserMaster).where(
                UserMaster.id == user_id
            )
        )

        user = user_result.scalar_one_or_none()

        if user is None:
            raise Exception("User not found.")

        pdf_path = await generate_prediction_report(
            history=history,
            user=user
        )

        return {
            "historyId": history.history_id,
            "fileName": Path(pdf_path).name,
            "downloadUrl": f"/static/reports/{Path(pdf_path).name}"
        }

    @staticmethod
    async def generate_latest_report(
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(History)
            .where(
                History.user_id == user_id
            )
            .order_by(History.prediction_date.desc())
        )

        history = result.scalars().first()

        if history is None:
            raise Exception("No prediction history found.")

        return await ReportService.generate_report(
            db=db,
            history_id=history.history_id,
            user_id=user_id
        )