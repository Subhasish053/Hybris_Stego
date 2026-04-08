import os
import numpy as np


def _plt():
    import matplotlib.pyplot as plt
    return plt


def visualize_dwt(LL, LH, HL, HH, folder):
    plt = _plt()

    os.makedirs(folder, exist_ok=True)

    plt.figure(figsize=(8,8))

    plt.subplot(221)
    plt.title("LL")
    plt.imshow(LL, cmap="gray")

    plt.subplot(222)
    plt.title("LH")
    plt.imshow(LH, cmap="gray")

    plt.subplot(223)
    plt.title("HL")
    plt.imshow(HL, cmap="gray")

    plt.subplot(224)
    plt.title("HH")
    plt.imshow(HH, cmap="gray")

    plt.tight_layout()

    path = os.path.join(folder,"dwt_subbands.png")

    plt.savefig(path)
    plt.close()

    print("Saved:", path)


def visualize_dct(block, folder, name):
    plt = _plt()

    os.makedirs(folder, exist_ok=True)

    plt.figure()

    plt.imshow(np.log(np.abs(block)+1), cmap="hot")

    plt.title(name)

    plt.colorbar()

    path = os.path.join(folder,f"{name}.png")

    plt.savefig(path)

    plt.close()

    print("Saved:", path)


def visualize_difference(cover, stego, folder):
    plt = _plt()

    os.makedirs(folder, exist_ok=True)

    diff = np.abs(cover.astype(np.float32) - stego.astype(np.float32))

    plt.figure()

    plt.imshow(diff, cmap="hot")

    plt.title("Difference")

    plt.colorbar()

    path = os.path.join(folder,"difference.png")

    plt.savefig(path)

    plt.close()

    print("Saved:", path)
    
def visualize_embedding_heatmap(original_subband, modified_subband, folder):
    plt = _plt()

    os.makedirs(folder, exist_ok=True)

    # difference between original and modified subband
    diff = np.abs(modified_subband - original_subband)

    # normalize for visualization
    diff = diff / np.max(diff)

    plt.figure(figsize=(6,6))

    plt.imshow(diff, cmap="hot")

    plt.title("Embedding Heatmap")

    plt.colorbar()

    path = os.path.join(folder, "embedding_heatmap.png")

    plt.savefig(path)

    plt.close()

    print("Saved:", path)

def visualize_histogram(cover, stego, folder):

    import os
    plt = _plt()

    os.makedirs(folder, exist_ok=True)

    plt.figure()

    plt.hist(cover.ravel(), bins=256, alpha=0.5, label="Cover")
    plt.hist(stego.ravel(), bins=256, alpha=0.5, label="Stego")

    plt.legend()

    plt.title("Histogram Comparison")

    path = os.path.join(folder, "histogram.png")

    plt.savefig(path)

    plt.close()

    print("Saved:", path)
    
    
def visualize_blocks(image, block_size, folder):

    import cv2
    import numpy as np
    import os

    os.makedirs(folder, exist_ok=True)

    vis = image.copy()

    if len(vis.shape) == 2:
        vis = cv2.cvtColor(vis.astype(np.uint8), cv2.COLOR_GRAY2BGR)

    h, w = vis.shape[:2]

    for i in range(0, h, block_size):
        cv2.line(vis, (0, i), (w, i), (255, 255, 255), 1)

    for j in range(0, w, block_size):
        cv2.line(vis, (j, 0), (j, h), (255, 255, 255), 1)

    path = os.path.join(folder, "block_grid.png")

    cv2.imwrite(path, vis)

    print("Saved:", path)
