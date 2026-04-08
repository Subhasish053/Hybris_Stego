from skimage.metrics import structural_similarity as ssim
import numpy as np


def calculate_ssim(original, stego):

    # Ensure same dtype
    original = original.astype(np.float32)
    stego = stego.astype(np.float32)

    value = ssim(
        original,
        stego,
        data_range=255,
        channel_axis=2,
        win_size=7
    )

    return value