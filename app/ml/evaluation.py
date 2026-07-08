import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


def evaluate_model(
    model,
    test_generator
):
    """
    Evaluate the trained model on the test dataset.
    """

    # Reset generator
    test_generator.reset()

    # Predict probabilities
    predictions = model.predict(
        test_generator,
        verbose=0
    )

    # Convert probabilities to binary labels
    y_pred = (predictions.flatten() > 0.5).astype(int)

    # Ground truth labels
    y_true = test_generator.classes

    # Metrics
    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred
    )

    return {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "confusion_matrix": cm.tolist()
    }