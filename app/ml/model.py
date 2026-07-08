from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.layers import (
    Dense,
    GlobalAveragePooling2D,
    Dropout
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Precision, Recall


IMG_SIZE = (224, 224)
LEARNING_RATE = 0.0001


def build_model( learning_rate=LEARNING_RATE):
    """
    Build and compile the DenseNet121 model
    for binary pneumonia classification.
    """

    # ==========================
    # Load DenseNet121
    # ==========================

    base_model = DenseNet121(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3)
    )

    # Freeze pretrained layers
    base_model.trainable = False

    # ==========================
    # Classification Head
    # ==========================

    x = GlobalAveragePooling2D()(base_model.output)

    x = Dropout(0.3)(x)

    output = Dense(
        1,
        activation="sigmoid"
    )(x)

    model = Model(
        inputs=base_model.input,
        outputs=output
    )

    # ==========================
    # Compile Model
    # ==========================

    model.compile(
        optimizer=Adam(
            learning_rate=LEARNING_RATE
        ),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            Precision(name="precision"),
            Recall(name="recall")
        ]
    )

    return model