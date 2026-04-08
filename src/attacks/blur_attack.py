import cv2


def apply_blur(image, kernel_size=3):

    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    return blurred.astype("float32")