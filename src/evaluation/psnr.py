import numpy as np

def calculate_psnr(original, stego):

    mse = np.mean((original - stego) ** 2)

    if mse == 0:
        return 100

    psnr = 10 * np.log10((255 ** 2) / mse)

    return psnr