from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta

from app.models.history import History


async def get_dashboard_stats(db: AsyncSession, user_id: int):

    # ── Base query scoped to current user ──
    base = select(History).where(History.user_id == user_id)

    # ── Total scans ──
    total_result = await db.execute(
        select(func.count()).select_from(
            select(History).where(History.user_id == user_id).subquery()
        )
    )
    total_scans = total_result.scalar() or 0

    # ── Pneumonia cases ──
    pneumonia_result = await db.execute(
        select(func.count()).select_from(
            select(History).where(
                History.user_id == user_id,
                History.detected_disease == "PNEUMONIA"
            ).subquery()
        )
    )
    pneumonia_cases = pneumonia_result.scalar() or 0

    # ── Healthy cases ──
    healthy_cases = total_scans - pneumonia_cases

    # ── Average confidence ──
    avg_result = await db.execute(
        select(func.avg(History.confidence)).where(
            History.user_id == user_id
        )
    )
    average_confidence = avg_result.scalar()
    average_confidence = round(float(average_confidence), 1) if average_confidence else 0.0

    # ── Scans this month ──
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month_result = await db.execute(
        select(func.count()).select_from(
            select(History).where(
                History.user_id == user_id,
                History.prediction_date >= month_start
            ).subquery()
        )
    )
    scans_this_month = month_result.scalar() or 0

    # ── Pneumonia cases this week ──
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    week_result = await db.execute(
        select(func.count()).select_from(
            select(History).where(
                History.user_id == user_id,
                History.detected_disease == "PNEUMONIA",
                History.prediction_date >= week_start
            ).subquery()
        )
    )
    pneumonia_this_week = week_result.scalar() or 0

    # ── Healthy cases this month ──
    healthy_month_result = await db.execute(
        select(func.count()).select_from(
            select(History).where(
                History.user_id == user_id,
                History.detected_disease == "NORMAL",
                History.prediction_date >= month_start
            ).subquery()
        )
    )
    healthy_this_month = healthy_month_result.scalar() or 0

    # ── Distribution percentages ──
    pneumonia_pct = round((pneumonia_cases / total_scans) * 100, 1) if total_scans > 0 else 0.0
    healthy_pct = round((healthy_cases / total_scans) * 100, 1) if total_scans > 0 else 0.0

    # ── Recent scans (last 5) ──
    recent_result = await db.execute(
        select(History)
        .where(History.user_id == user_id)
        .order_by(History.prediction_date.desc())
        .limit(5)
    )
    recent_scans = recent_result.scalars().all()

    recent = [
        {
            "historyId": r.history_id,
            "patientName": r.patient_name,
            "patientAge": r.patient_age,
            "patientGender": r.patient_gender,
            "detectedDisease": r.detected_disease,
            "confidence": round(r.confidence, 1),
            "predictionDate": r.prediction_date.isoformat() if r.prediction_date else None,
            "imageName": r.image_name,
        }
        for r in recent_scans
    ]

    return {
        "totalScans": total_scans,
        "pneumoniaCases": pneumonia_cases,
        "healthyCases": healthy_cases,
        "averageConfidence": average_confidence,
        "scansThisMonth": scans_this_month,
        "pneumoniaThisWeek": pneumonia_this_week,
        "healthyThisMonth": healthy_this_month,
        "pneumoniaPercentage": pneumonia_pct,
        "healthyPercentage": healthy_pct,
        "recentScans": recent,
    }