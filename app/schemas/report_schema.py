from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# =====================================================
# Report Response
# =====================================================

class ReportResponse(BaseModel):

    history_id: int

    patient_name: str

    detected_disease: str

    confidence: float

    report_name: str

    report_path: str

    generated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# Report Download Response
# =====================================================

class ReportDownloadResponse(BaseModel):

    filename: str

    download_url: str

    class Config:
        from_attributes = True


# =====================================================
# Latest Report Response
# =====================================================

class LatestReportResponse(BaseModel):

    history_id: int

    report_name: str

    report_path: str

    prediction_date: datetime

    class Config:
        from_attributes = True


# =====================================================
# Report Delete Response (Future)
# =====================================================

class ReportDeleteResponse(BaseModel):

    message: str

    success: bool = True

    