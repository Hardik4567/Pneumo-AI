import os

DATASET_PATH = "dataset/chest_xray"


def count_images(folder_path):

    count = 0

    for root, _, files in os.walk(folder_path):
        count += len([
            file for file in files
            if file.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

    return count


def load_dataset():

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    train_path = os.path.join(DATASET_PATH, "train")
    val_path = os.path.join(DATASET_PATH, "val")
    test_path = os.path.join(DATASET_PATH, "test")

    for path in [train_path, val_path, test_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing folder: {path}"
            )

    total_images = (
        count_images(train_path)
        + count_images(val_path)
        + count_images(test_path)
    )

    return {
        "dataset_path": DATASET_PATH,
        "status": "Dataset loaded successfully",
        "total_images": total_images
    }