import numpy as np


def apply_gaussian_noise(image, mean=0, sigma=10):

    noise = np.random.normal(mean, sigma, image.shape)

    noisy = image + noise

    noisy = np.clip(noisy, 0, 255)

    return noisy.astype(np.float32)