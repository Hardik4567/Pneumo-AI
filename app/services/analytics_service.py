from collections import defaultdict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import History


async def get_analytics_data(
    db: AsyncSession,
    user_id: int
):
    """
    Returns analytics for the logged-in user.
    """

    # ---------------------------------
    # Fetch all predictions
    # ---------------------------------

    result = await db.execute(
        select(History)
        .where(History.user_id == user_id)
        .order_by(History.prediction_date.desc())
    )

    predictions = result.scalars().all()

    total_scans = len(predictions)

    pneumonia = sum(
        1
        for p in predictions
        if p.detected_disease.lower() == "pneumonia"
    )

    healthy = total_scans - pneumonia

    average_confidence = (
        round(
            sum(p.confidence for p in predictions) / total_scans,
            2
        )
        if total_scans
        else 0
    )

    # ---------------------------------
    # Monthly Trend
    # ---------------------------------

    monthly = defaultdict(int)

    for p in predictions:
        month = p.prediction_date.strftime("%b")
        monthly[month] += 1

    monthly_trend = [
        {
            "month": k,
            "count": v
        }
        for k, v in monthly.items()
    ]

    # ---------------------------------
    # Disease Distribution
    # ---------------------------------

    distribution = {
        "Healthy": healthy,
        "Pneumonia": pneumonia
    }

    # ---------------------------------
    # Confidence Trend
    # ---------------------------------

    confidence_trend = [
        {
            "date": p.prediction_date.strftime("%d %b"),
            "confidence": p.confidence
        }
        for p in reversed(predictions)
    ]

    # ---------------------------------
    # Latest Reports
    # ---------------------------------

    latest_reports = []

    for p in predictions[:10]:

        latest_reports.append({

            "id": p.history_id,

            "patientName": p.patient_name,

            "age": p.patient_age,

            "gender": p.patient_gender,

            "disease": p.detected_disease,

            "confidence": p.confidence,

            "date": p.prediction_date.strftime("%d %b %Y")

        })

    # ---------------------------------
    # Response
    # ---------------------------------

    return {

        "summary": {

            "totalScans": total_scans,

            "healthy": healthy,

            "pneumonia": pneumonia,

            "averageConfidence": average_confidence

        },

        "distribution": distribution,

        "monthlyTrend": monthly_trend,

        "confidenceTrend": confidence_trend,

        "latestReports": latest_reports

    }