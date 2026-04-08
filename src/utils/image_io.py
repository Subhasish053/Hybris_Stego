import cv2
import numpy as np


def load_image(path, block_size=8):

    image = cv2.imread(path, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Image not found: {path}")

    image = image.astype(np.float32)

    h, w, _ = image.shape

    h = (h // block_size) * block_size
    w = (w // block_size) * block_size

    image = image[:h, :w]

    return image


def save_image(path, image):

    image = np.clip(image, 0, 255).astype(np.uint8)

    cv2.imwrite(path, image)