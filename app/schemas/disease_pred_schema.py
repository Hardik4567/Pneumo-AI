from pydantic import BaseModel
from typing import List, Optional


class LoadDatasetResponse(BaseModel):
    dataset_path: str
    status: str
    total_images: int


class CleanDatasetResponse(BaseModel):
    removed_files: int
    status: str


class PreprocessResponse(BaseModel):
    status: str
    train_samples: int
    validation_samples: int
    test_samples: int


class EDAResponse(BaseModel):
    train_normal: int
    train_pneumonia: int
    val_normal: Optional[int] = 0
    val_pneumonia: Optional[int] = 0
    test_normal: int
    test_pneumonia: int
    total_images: int


class TrainRequest(BaseModel):
    epochs: int = 10
    batch_size: int = 32
    learning_rate: float = 0.001


class TrainResponse(BaseModel):
    status: str
    accuracy: float
    loss: float
    model_path: str


class EvaluationResponse(BaseModel):
    accuracy: float
    loss: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    heatmap: Optional[str] = None
    report_path: Optional[str] = None
    report_name: Optional[str] = None
    history_id: Optional[int] = None