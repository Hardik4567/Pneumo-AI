from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import date
from sqlalchemy import asc,desc

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

from app.models.history import History
from app.schemas.history_schema import (
    HistoryCreate,
    HistoryUpdate
)


# ----------------------------------------------------------
# Create History
# ----------------------------------------------------------
async def create_history_service(
    db: AsyncSession,
    request: HistoryCreate
):

    history = History(
        user_id=request.user_id,
        patient_name=request.patient_name,
        patient_age=request.patient_age,
        patient_gender=request.patient_gender,
        image_name=request.image_name,
        image_path=request.image_path,
        detected_disease=request.detected_disease,
        confidence=request.confidence
    )

    db.add(history)

    await db.commit()

    await db.refresh(history)

    return history


# ----------------------------------------------------------
# Get All History
# ----------------------------------------------------------
# ----------------------------------------------------------
# Get All History (with filters)
# ----------------------------------------------------------
async def get_all_history_service(
    db: AsyncSession,
    user_id: Optional[int] = None,
    patient_name: Optional[str] = None,
    detected_disease: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_by: str = "newest",
    sort_confidence: Optional[str] = None, 
    limit: int = 10,
    offset: int = 0,
):

    query = select(History)

    if user_id is not None:
        query = query.where(History.user_id == user_id)

    if patient_name:
        query = query.where(
            History.patient_name.ilike(f"%{patient_name}%")
        )

    if detected_disease:
        query = query.where(
            History.detected_disease == detected_disease
        )

    if start_date:
        query = query.where(History.prediction_date >= start_date)

    if end_date:
        query = query.where(History.prediction_date <= end_date)

    order_clauses = []

    # Confidence sorting (optional override)
    if sort_confidence == "asc":
        order_clauses.append(asc(History.confidence))
    elif sort_confidence == "desc":
        order_clauses.append(desc(History.confidence))
    else:
        # Default / date sorting
        if sort_by == "oldest":
            order_clauses.append(asc(History.prediction_date))
        else:
            order_clauses.append(desc(History.prediction_date))

    query = query.order_by(*order_clauses)

    # ---------------- Pagination ----------------
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)

    return result.scalars().all()


# ----------------------------------------------------------
# Get History By ID
# ----------------------------------------------------------
async def get_history_by_id_service(
    db: AsyncSession,
    history_id: int
):

    result = await db.execute(
        select(History).where(
            History.history_id == history_id
        )
    )

    return result.scalar_one_or_none()


# ----------------------------------------------------------
# Update History
# ----------------------------------------------------------
async def update_history_service(
    db: AsyncSession,
    history_id: int,
    request: HistoryUpdate
):

    result = await db.execute(
        select(History).where(
            History.history_id == history_id
        )
    )

    history = result.scalar_one_or_none()

    if history is None:
        return None

    update_data = request.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(history, key, value)

    await db.commit()

    await db.refresh(history)

    return history


# ----------------------------------------------------------
# Delete History
# ----------------------------------------------------------
async def delete_history_service(
    db: AsyncSession,
    history_id: int
):

    result = await db.execute(
        select(History).where(
            History.history_id == history_id
        )
    )

    history = result.scalar_one_or_none()

    if history is None:
        return False

    await db.delete(history)

    await db.commit()

    return True



async def export_history_pdf_service(
    db: AsyncSession,
    user_id: Optional[int] = None
):

    query = select(History)

    if user_id is not None:
        query = query.where(History.user_id == user_id)

    result = await db.execute(query)
    records = result.scalars().all()

    file_path = "history_report.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    # ---------------- TITLE ----------------
    title = Paragraph("PneumoAI - Prediction History Report", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # ---------------- TABLE DATA ----------------
    data = [
        ["Patient", "Age", "Gender", "Disease", "Confidence", "Date"]
    ]

    for r in records:
        data.append([
            r.patient_name,
            str(r.patient_age),
            r.patient_gender,
            r.detected_disease,
            f"{r.confidence:.2f}",
            str(r.prediction_date)
        ])

    # ---------------- TABLE STYLE ----------------
    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)

    # ---------------- BUILD PDF ----------------
    doc.build(elements)

    return file_path