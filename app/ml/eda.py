import os

DATASET_PATH = "dataset/chest_xray"


def count_images(folder_path: str) -> int:
    """
    Count valid image files in a folder.
    """

    if not os.path.exists(folder_path):
        return 0

    return len([
        file for file in os.listdir(folder_path)
        if file.lower().endswith((".jpg", ".jpeg", ".png"))
    ])


def get_dataset_stats():
    """
    Returns dataset statistics for train, validation, and test sets.
    """

    train_normal = count_images(
        os.path.join(DATASET_PATH, "train", "NORMAL")
    )

    train_pneumonia = count_images(
        os.path.join(DATASET_PATH, "train", "PNEUMONIA")
    )

    val_normal = count_images(
        os.path.join(DATASET_PATH, "val", "NORMAL")
    )

    val_pneumonia = count_images(
        os.path.join(DATASET_PATH, "val", "PNEUMONIA")
    )

    test_normal = count_images(
        os.path.join(DATASET_PATH, "test", "NORMAL")
    )

    test_pneumonia = count_images(
        os.path.join(DATASET_PATH, "test", "PNEUMONIA")
    )

    total_images = (
        train_normal +
        train_pneumonia +
        val_normal +
        val_pneumonia +
        test_normal +
        test_pneumonia
    )

    return {
        "train_normal": train_normal,
        "train_pneumonia": train_pneumonia,
        "val_normal": val_normal,
        "val_pneumonia": val_pneumonia,
        "test_normal": test_normal,
        "test_pneumonia": test_pneumonia,
        "total_images": total_images
    }