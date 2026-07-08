import os
import json

from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau
)

from app.ml.model import build_model

MODEL_PATH = "app/models/pneumonia_model.keras"
HISTORY_PATH = "app/models/history.json"


def train_model(
    train_generator,
    val_generator,
    epochs=10,
    learning_rate=0.0001
):
    """
    Train the DenseNet121 model and save best model as .h5
    """

    # Create directory if not exists
    os.makedirs("app/models", exist_ok=True)

    # Build model
    model = build_model(learning_rate=learning_rate)

    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
            verbose=1
        ),

        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=2,
            verbose=1
        ),

        ModelCheckpoint(
            filepath="app/models/best_model.h5",  # ✅ saves best model
            monitor="val_accuracy",
            save_best_only=True,
            save_weights_only=False,
            verbose=1
        )
    ]

    # Train model
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1
    )

    # Save training history
    with open("app/models/history.json", "w") as file:
        json.dump(history.history, file)

    # ✅ ALSO save final model (last epoch) as .h5
    model.save("app/models/final_model.h5")

    return model, history