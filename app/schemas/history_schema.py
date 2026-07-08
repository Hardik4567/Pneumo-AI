from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class HistoryCreate(BaseModel):
    user_id: Optional[int] = None

    patient_name: str
    patient_age: int
    patient_gender: str

    image_name: str
    image_path: Optional[str] = None

    detected_disease: str
    confidence: float

    heatmap_path: Optional[str] = None
    report_path: Optional[str] = None
    processing_time: Optional[float] = None


class HistoryUpdate(BaseModel):      
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None


class HistoryResponse(BaseModel):
    history_id: int
    user_id: Optional[int]

    patient_name: str
    patient_age: int
    patient_gender: str

    image_name: str
    image_path: Optional[str]

    detected_disease: str
    confidence: float

    heatmap_path: Optional[str]
    report_path: Optional[str]
    processing_time: Optional[float]

    prediction_date: datetime

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int

    items: List[HistoryResponse]

    class Config:
        from_attributes = True


class HistoryDeleteRequest(BaseModel):
    history_ids: List[int]


class HistoryStatistics(BaseModel):
    total_records: int
    total_patients: int

    disease_counts: dict[str, int]

    average_confidence: float

    earliest_prediction_date: Optional[datetime] = None
    latest_prediction_date: Optional[datetime] = None