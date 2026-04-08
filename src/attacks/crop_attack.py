import numpy as np


def apply_crop(image, crop_ratio=0.1):

    # Handle both grayscale and color images
    if len(image.shape) == 3:
        h, w, c = image.shape
    else:
        h, w = image.shape
        c = None

    crop_h = int(h * crop_ratio)
    crop_w = int(w * crop_ratio)
    
    # Align to 8x8 block boundaries to prevent block desynchronization
    crop_h = (crop_h // 8) * 8
    crop_w = (crop_w // 8) * 8

    cropped = image[crop_h:h-crop_h, crop_w:w-crop_w]

    # Create padded image of same size, keeping the geometry intact
    padded = np.zeros_like(image)

    if c is None:
        padded[crop_h:h-crop_h, crop_w:w-crop_w] = cropped
    else:
        padded[crop_h:h-crop_h, crop_w:w-crop_w, :] = cropped

    return padded.astype(np.float32)