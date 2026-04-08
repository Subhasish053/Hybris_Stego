import numpy as np


def split_blocks(image, block_size=8):

    h, w = image.shape

    blocks = []

    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):

            blocks.append(image[i:i+block_size, j:j+block_size])

    return blocks


def merge_blocks(blocks, image_shape, block_size=8):

    h, w = image_shape

    image = np.zeros((h, w), dtype=np.float32)

    idx = 0

    for i in range(0, h - block_size + 1, block_size):
        for j in range(0, w - block_size + 1, block_size):

            if idx >= len(blocks):
                return image

            image[i:i+block_size, j:j+block_size] = blocks[idx]

            idx += 1

    return image