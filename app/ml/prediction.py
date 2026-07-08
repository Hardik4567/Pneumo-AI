"""
app/ml/prediction.py
Runs inference on an uploaded chest X-ray image.
Accepts a pre-loaded (cached) model to avoid re-loading on every call.
"""

import numpy as np
from io import BytesIO
from PIL import Image

from fastapi import UploadFile, HTTPException
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.densenet import preprocess_input

from app.ml.explainability import generate_gradcam


IMG_SIZE = (224, 224)


async def predict_image(file: UploadFile, model) -> dict:
    """
    Predict whether an uploaded chest X-ray is NORMAL or PNEUMONIA.

    Args:
        file:  FastAPI UploadFile object
        model: Pre-loaded Keras model (passed from service cache)

    Returns:
        dict with 'prediction' and 'confidence' keys
    """

    # ── Read & decode image ──
    image_bytes = await file.read()

    try:
        original_image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read image. Please upload a valid PNG or JPEG file."
        )
    
    original_array = img_to_array(original_image).astype(np.uint8)

    # ── Preprocess ──
    image = original_image.resize(IMG_SIZE)
    image = img_to_array(image)
    image = preprocess_input(image)          # DenseNet-121 normalization
    image = np.expand_dims(image, axis=0)   # Add batch dimension: (1, 224, 224, 3)

    # ── Inference ──
    try:
        probability = float(model.predict(image, verbose=0)[0][0])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model inference failed: {str(e)}"
        )

    # ── Map probability to label ──
    # Model output: sigmoid — 1.0 = PNEUMONIA, 0.0 = NORMAL
    if probability >= 0.5:
        prediction = "PNEUMONIA"
        confidence = probability * 100
    else:
        prediction = "NORMAL"
        confidence = (1.0 - probability) * 100


    # ─────────────────────────────
    # Generate Grad-CAM heatmap
    # ─────────────────────────────

    try:
        heatmap_path = generate_gradcam(
            model=model,
            preprocessed_image=image,
            original_image=original_array
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grad-CAM generation failed: {str(e)}"
        )


    return {
        "prediction": prediction,
        "confidence": round(confidence, 2),
        "heatmap": heatmap_path
    }