import os
from PIL import Image


def clean_dataset(dataset_path):

    removed_files = 0

    for root, _, files in os.walk(dataset_path):

        for file in files:

            if not file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            file_path = os.path.join(root, file)

            try:

                with Image.open(file_path) as img:
                    img.verify()

            except Exception:

                if os.path.exists(file_path):
                    os.remove(file_path)

                removed_files += 1

                print(f"Removed corrupted image: {file_path}")

    return removed_files