from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.densenet import preprocess_input

# Image configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42


def get_data_generators(
    train_dir: str,
    val_dir: str,
    test_dir: str
):
    """
    Creates train, validation, and test data generators
    for the Kaggle Chest X-ray dataset.
    """

    # Training data augmentation
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=15,
        width_shift_range=0.10,
        height_shift_range=0.10,
        shear_range=0.10,
        zoom_range=0.20,
        horizontal_flip=True,
        fill_mode="nearest"
    )

    # Validation & Test (No augmentation)
    val_test_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )

    # Training Generator
    train_generator = train_datagen.flow_from_directory(
        directory=train_dir,
        target_size=IMG_SIZE,
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=True,
        seed=SEED
    )

    # Validation Generator
    validation_generator = val_test_datagen.flow_from_directory(
        directory=val_dir,
        target_size=IMG_SIZE,
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=False,
        seed=SEED
    )

    # Test Generator
    test_generator = val_test_datagen.flow_from_directory(
        directory=test_dir,
        target_size=IMG_SIZE,
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=False,
        seed=SEED
    )

    return (
        train_generator,
        validation_generator,
        test_generator
    )