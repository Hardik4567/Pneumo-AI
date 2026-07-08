"""
ML Prediction Service

Responsibilities:
- Load the trained model once (cached at module level)
- Run prediction on uploaded images
- Save prediction history to DB
- Generate PDF report
- Save report record to DB
"""

import os
import time
import asyncio
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.load_dataset import load_dataset
from app.ml.clean_dataset import clean_dataset
from app.ml.eda import get_dataset_stats
from app.ml.preprocessing import get_data_generators
from app.ml.training import train_model
from app.ml.evaluation import evaluate_model
from app.ml.prediction import predict_image
from app.models.history import History
from app.models.report import Report
from app.utils.pdf_generator import generate_prediction_report

logger = logging.getLogger(__name__)

# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = "app/models/best_model.h5"

# ============================================================
# Model Singleton Cache
# Prevents loading the 30MB model on every request.
# ============================================================

_cached_model = None


def _get_model():
    """
    Load and cache the Keras model.
    Called once at first prediction, then reused.
    """
    global _cached_model
    if _cached_model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at '{MODEL_PATH}'. "
                "Please place the trained model file there or train the model first."
            )
        logger.info(f"Loading model from {MODEL_PATH} ...")
        from tensorflow.keras.models import load_model  # lazy import
        _cached_model = load_model(MODEL_PATH)
        logger.info("Model loaded and cached successfully.")
    return _cached_model


# ============================================================
# Dataset Services (admin utilities)
# ============================================================

async def load_dataset_service():
    return load_dataset()


async def clean_dataset_service():
    removed_files = clean_dataset(dataset_path="dataset/chest_xray")
    return {
        "removed_files": removed_files,
        "status": "dataset cleaned successfully"
    }


async def preprocess_dataset_service():
    train_gen, val_gen, test_gen = get_data_generators(
        train_dir="dataset/chest_xray/train",
        val_dir="dataset/chest_xray/val",
        test_dir="dataset/chest_xray/test"
    )
    return {
        "status": "preprocessing completed successfully",
        "train_samples": train_gen.samples,
        "validation_samples": val_gen.samples,
        "test_samples": test_gen.samples
    }


async def eda_service():
    return get_dataset_stats()


async def train_model_service(request):
    train_gen, val_gen, _ = get_data_generators(
        train_dir="dataset/chest_xray/train",
        val_dir="dataset/chest_xray/val",
        test_dir="dataset/chest_xray/test"
    )
    model, history = train_model(
        train_generator=train_gen,
        val_generator=val_gen,
        epochs=request.epochs,
        learning_rate=request.learning_rate
    )
    return {
        "status": "Training completed successfully",
        "accuracy": float(max(history.history["accuracy"])),
        "loss": float(min(history.history["loss"])),
        "model_path": MODEL_PATH
    }


async def evaluate_model_service():
    model = _get_model()
    _, _, test_gen = get_data_generators(
        train_dir="dataset/chest_xray/train",
        val_dir="dataset/chest_xray/val",
        test_dir="dataset/chest_xray/test"
    )
    return evaluate_model(model=model, test_generator=test_gen)


# ============================================================
# Prediction Service
# ============================================================

async def predict_service(
    file,
    db: AsyncSession,
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    user_id: int | None = None
) -> dict:
    
    """
Full prediction pipeline:
1. Load (cached) model
2. Run inference
3. Generate Grad-CAM heatmap
4. Save History record
5. Generate PDF report
6. Save Report record
7. Update History.report_path
8. Return result dict
    """

    start_time = time.perf_counter()

    # ── Load model (cached) ──
    model = _get_model()

    # ── Run inference ──
    result = await predict_image(
        file=file,
        model=model  # pass cached model — no re-loading
    )

    elapsed = round(time.perf_counter() - start_time, 3)

    # ── Save History ──
    history_record = History(
        user_id=user_id,
        patient_name=patient_name,
        patient_age=patient_age,
        patient_gender=patient_gender,
        image_name=file.filename,
        image_path=None,
        detected_disease=result["prediction"],
        confidence=float(result["confidence"]),
        processing_time=elapsed,
    )

    db.add(history_record)
    await db.commit()
    await db.refresh(history_record)

    # ── Load user for PDF ──
    user = None
    if user_id is not None:
        from app.models.user_master import UserMaster
        user = await db.get(UserMaster, user_id)

    # ── Generate PDF Report ──
    report_path = None
    report_name = None

    try:
        report_path = await generate_prediction_report(history_record, user)
        report_name = Path(report_path).name

        # ── Save Report record ──
        report_record = Report(
            history_id=history_record.history_id,
            user_id=user_id,
            report_name=report_name,
            report_path=report_path,
            report_type="PDF"
        )
        db.add(report_record)

        # ── Update History.report_path ──
        history_record.report_path = report_path

        await db.commit()
        await db.refresh(report_record)

    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        # Don't fail the whole prediction — just omit the report

    return {
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "heatmap": result.get("heatmap"),
        "history_id": history_record.history_id,
        "report_path": report_path,
        "report_name": report_name,
        "processing_time": elapsed,
    }
