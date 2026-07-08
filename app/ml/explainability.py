"""
Grad-CAM (Gradient-weighted Class Activation Mapping) module for PneumoAI.

Generates visual explanations for predictions made by the DenseNet121-based
pneumonia detection model by highlighting discriminative image regions.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow import keras

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEATMAP_DIR: Path = Path("static") / "heatmaps"
COLORMAP: int = cv2.COLORMAP_JET
ALPHA: float = 0.4          # heatmap blend weight
BETA: float = 1.0 - ALPHA   # original image blend weight
OUTPUT_FORMAT: str = "PNG"
FILENAME_PREFIX: str = "overlay"
UUID_SHORT_LEN: int = 8


# ---------------------------------------------------------------------------
# Layer detection
# ---------------------------------------------------------------------------

def get_last_conv_layer(model: keras.Model) -> keras.layers.Layer:
    """Return the last Conv2D layer in the model, traversing nested models.

    Iterates over the model's layers in reverse order and returns the first
    Conv2D layer encountered.  For Functional API models that wrap sub-models
    (e.g. DenseNet121 as a nested Model), the function recurses into each
    sub-model so that the search is exhaustive.

    Args:
        model: A compiled or uncompiled ``keras.Model`` instance.

    Returns:
        The last ``Conv2D`` layer found in the model graph.

    Raises:
        ValueError: If no ``Conv2D`` layer exists anywhere in the model.
    """
    def _find_last_conv(layers: list) -> keras.layers.Layer | None:
        for layer in reversed(layers):
            if isinstance(layer, keras.layers.Conv2D):
                return layer
            # Recurse into nested Model / Sequential blocks
            if isinstance(layer, keras.Model):
                result = _find_last_conv(layer.layers)
                if result is not None:
                    return result
        return None

    last_conv = _find_last_conv(model.layers)
    if last_conv is None:
        raise ValueError(
            "No Conv2D layer found in the provided model.  "
            "Grad-CAM requires at least one convolutional layer."
        )
    return last_conv


# ---------------------------------------------------------------------------
# Heatmap computation
# ---------------------------------------------------------------------------

def make_gradcam_heatmap(
    preprocessed_image: np.ndarray,
    model: keras.Model,
    last_conv_layer: keras.layers.Layer,
) -> np.ndarray:
    """Compute the Grad-CAM heatmap for a single preprocessed image.

    Builds a sub-model that outputs both the activations of ``last_conv_layer``
    and the final model prediction.  Gradients of the predicted class score
    with respect to the convolutional feature maps are used to weight each
    feature map, producing a single 2-D heatmap.

    Args:
        preprocessed_image: A ``(1, H, W, C)`` float32 array produced by the
            same preprocessing pipeline used during training.
        model: The full ``keras.Model`` used for inference.
        last_conv_layer: The ``Conv2D`` layer whose activations are visualised.

    Returns:
        A 2-D ``numpy.ndarray`` of shape ``(h, w)`` with values in ``[0, 1]``,
        where higher values indicate regions more influential to the prediction.

    Raises:
        tf.errors.InvalidArgumentError: If ``preprocessed_image`` has an
            unexpected shape or dtype.
        RuntimeError: If gradient computation fails.
    """
    # Build an intermediate model: input → [conv activations, predictions]
    grad_model = keras.Model(
        inputs=model.inputs,
        outputs=[last_conv_layer.output, model.output],
    )

    with tf.GradientTape() as tape:
        inputs = tf.cast(preprocessed_image, tf.float32)
        conv_outputs, predictions = grad_model(inputs, training=False)
        # For binary sigmoid output, the score is the single logit
        class_score = predictions[:, 0]

    # Gradients of the class score w.r.t. the conv feature maps
    grads: tf.Tensor = tape.gradient(class_score, conv_outputs)

    if grads is None:
        raise RuntimeError(
            "Gradient computation returned None.  Ensure the model is built "
            "with a differentiable graph and that the target layer is reachable."
        )

    # Global-average-pool the gradients over the spatial dimensions → (batch, channels)
    pooled_grads: tf.Tensor = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Weight each feature map by its corresponding pooled gradient
    conv_outputs_squeezed: tf.Tensor = conv_outputs[0]           # (h, w, channels)
    weighted_maps: tf.Tensor = conv_outputs_squeezed * pooled_grads  # broadcast

    # Sum across the channel dimension and ReLU to keep only positive influence
    heatmap: np.ndarray = tf.reduce_sum(weighted_maps, axis=-1).numpy()
    heatmap = np.maximum(heatmap, 0)

    # Normalise to [0, 1]; guard against a zero-range map
    heatmap_max: float = float(heatmap.max())
    if heatmap_max > 0:
        heatmap /= heatmap_max

    return heatmap


# ---------------------------------------------------------------------------
# Heatmap application
# ---------------------------------------------------------------------------

def apply_heatmap(
    heatmap: np.ndarray,
    original_image: np.ndarray,
) -> np.ndarray:
    """Resize the heatmap and overlay it on the original image.

    Resizes ``heatmap`` to match ``original_image``, applies the JET colormap,
    and blends the result with the original image.

    Args:
        heatmap: A 2-D float ``numpy.ndarray`` in ``[0, 1]`` as returned by
            :func:`make_gradcam_heatmap`.
        original_image: An ``(H, W, 3)`` uint8 RGB array representing the
            original (non-preprocessed) image at its native resolution.

    Returns:
        An ``(H, W, 3)`` uint8 RGB array containing the blended overlay.

    Raises:
        ValueError: If ``original_image`` is not a 3-channel array.
    """
    if original_image.ndim != 3 or original_image.shape[2] != 3:
        raise ValueError(
            f"original_image must have shape (H, W, 3), "
            f"got {original_image.shape}."
        )

    target_h, target_w = original_image.shape[:2]

    # Scale heatmap to uint8 for OpenCV colormap
    heatmap_uint8: np.ndarray = np.uint8(heatmap * 255)

    # Resize to original image dimensions
    heatmap_resized: np.ndarray = cv2.resize(
        heatmap_uint8,
        (target_w, target_h),
        interpolation=cv2.INTER_LINEAR,
    )

    # Apply JET colormap → BGR uint8
    colormap_bgr: np.ndarray = cv2.applyColorMap(heatmap_resized, COLORMAP)

    # Convert original image from RGB to BGR for OpenCV blending
    original_bgr: np.ndarray = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)

    # Blend heatmap with original image
    overlay_bgr: np.ndarray = cv2.addWeighted(
        colormap_bgr, ALPHA,
        original_bgr, BETA,
        gamma=0,
    )

    # Return as RGB
    overlay_rgb: np.ndarray = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)
    return overlay_rgb


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_heatmap(overlay_image: np.ndarray) -> str:
    """Persist the overlay image to disk and return its relative path.

    Creates ``static/heatmaps/`` if it does not already exist, generates a
    UUID-based filename, and saves the image as a PNG file.

    Args:
        overlay_image: An ``(H, W, 3)`` uint8 RGB array to be saved.

    Returns:
        A relative path string of the form ``"static/heatmaps/overlay_<uuid8>.png"``.

    Raises:
        OSError: If the directory cannot be created or the file cannot be written.
        ValueError: If ``overlay_image`` cannot be converted to a ``PIL.Image``.
    """
    try:
        HEATMAP_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(
            f"Failed to create heatmap directory '{HEATMAP_DIR}': {exc}"
        ) from exc

    short_uuid: str = uuid.uuid4().hex[:UUID_SHORT_LEN]
    filename: str = f"{FILENAME_PREFIX}_{short_uuid}.png"
    output_path: Path = HEATMAP_DIR / filename

    try:
        pil_image: Image.Image = Image.fromarray(overlay_image)
        pil_image.save(output_path, format=OUTPUT_FORMAT)
    except (OSError, ValueError) as exc:
        raise OSError(
            f"Failed to save heatmap to '{output_path}': {exc}"
        ) from exc

    return "/" + str(output_path).replace("\\", "/")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_gradcam(
    model: keras.Model,
    preprocessed_image: np.ndarray,
    original_image: np.ndarray,
) -> str:
    """Generate a Grad-CAM overlay image and save it to disk.

    Orchestrates the full Grad-CAM pipeline:

    1. Detect the last Conv2D layer in ``model``.
    2. Compute the gradient-weighted heatmap.
    3. Overlay the heatmap onto ``original_image``.
    4. Save the result as a PNG and return the relative path.

    The model is **not** reloaded; it must be passed in already initialised.

    Args:
        model: The trained ``keras.Model`` used for pneumonia detection.
            Expected to accept ``(1, 224, 224, 3)`` float32 inputs and output
            a ``(1, 1)`` sigmoid-activated tensor.
        preprocessed_image: A ``(1, 224, 224, 3)`` float32 array produced by
            ``tensorflow.keras.applications.densenet.preprocess_input``.
        original_image: An ``(H, W, 3)`` uint8 RGB array of the original image
            at any resolution.  The overlay will preserve this resolution.

    Returns:
        Relative path to the saved PNG overlay, e.g.
        ``"static/heatmaps/overlay_f31c8f7d.png"``.

    Raises:
        ValueError: If no Conv2D layer is found or image shapes are invalid.
        RuntimeError: If gradient computation fails.
        OSError: If the overlay image cannot be saved.

    Example::

        from app.ml.gradcam import generate_gradcam

        overlay_path = generate_gradcam(
            model=loaded_model,
            preprocessed_image=img_array,   # shape (1, 224, 224, 3)
            original_image=original_rgb,    # shape (H, W, 3) uint8
        )
        print(overlay_path)  # "static/heatmaps/overlay_a3f9c12b.png"
    """
    if preprocessed_image.ndim != 4 or preprocessed_image.shape[0] != 1:
        raise ValueError(
            f"preprocessed_image must have shape (1, H, W, C), "
            f"got {preprocessed_image.shape}."
        )

    if original_image.ndim != 3 or original_image.shape[2] != 3:
        raise ValueError(
            f"original_image must have shape (H, W, 3), "
            f"got {original_image.shape}."
        )

    last_conv_layer: keras.layers.Layer = get_last_conv_layer(model)

    heatmap: np.ndarray = make_gradcam_heatmap(
        preprocessed_image=preprocessed_image,
        model=model,
        last_conv_layer=last_conv_layer,
    )

    overlay: np.ndarray = apply_heatmap(
        heatmap=heatmap,
        original_image=original_image,
    )

    return save_heatmap(overlay)