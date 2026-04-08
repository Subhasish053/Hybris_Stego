import pywt
import numpy as np


def apply_dwt(image, wavelet="haar"):

    image = image.astype(np.float32)

    coeffs = pywt.dwt2(image, wavelet)

    LL, (LH, HL, HH) = coeffs

    return LL, LH, HL, HH


def inverse_dwt(LL, LH, HL, HH, wavelet="haar"):

    coeffs = (LL, (LH, HL, HH))

    image = pywt.idwt2(coeffs, wavelet)

    return image.astype(np.float32)