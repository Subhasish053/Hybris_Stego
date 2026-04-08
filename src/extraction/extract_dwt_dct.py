import cv2
import numpy as np

from src.transforms.dwt import apply_dwt
from src.transforms.dct import dct2
from src.transforms.block_processing import split_blocks


def _extract_from_subband(subband, bit_count, indices, block_size):
    """Extract bits from a single subband using coefficient relationship."""
    blocks = split_blocks(subband, block_size)
    bits = []

    for i in range(bit_count):
        block = blocks[indices[i]]
        dct_block = dct2(block)

        C1 = dct_block[0, 1]
        C3 = dct_block[1, 1]

        if abs(C1) < 1e-4 and abs(C3) < 1e-4:
            bits.append("X")
        elif C1 > C3:
            bits.append("1")
        else:
            bits.append("0")

    return bits


def _extract_channel(channel, bit_length, config, channel_seed=0):
    """Extract bits from a single color channel using DWT+DCT across LH and HL."""
    block_size = config["block_size"]

    LL, LH, HL, HH = apply_dwt(channel)

    blocks_lh = split_blocks(LH, block_size)
    blocks_hl = split_blocks(HL, block_size)
    cap_lh = len(blocks_lh)
    cap_hl = len(blocks_hl)
    total_capacity = cap_lh + cap_hl

    if bit_length is None or bit_length > total_capacity:
        bit_length = total_capacity

    n_lh = (bit_length + 1) // 2
    n_hl = bit_length // 2
    n_lh = min(n_lh, cap_lh)
    n_hl = min(n_hl, cap_hl)

    np.random.seed(42 + channel_seed)
    indices_lh = np.random.permutation(cap_lh)
    np.random.seed(84 + channel_seed)
    indices_hl = np.random.permutation(cap_hl)

    bits_lh = _extract_from_subband(LH, n_lh, indices_lh, block_size)
    bits_hl = _extract_from_subband(HL, n_hl, indices_hl, block_size)

    bits = []
    for i in range(max(n_lh, n_hl)):
        if i < n_lh:
            bits.append(bits_lh[i])
        if i < n_hl:
            bits.append(bits_hl[i])

    return bits[:bit_length]


def extract_message(image, bit_length, config):

    block_size = config["block_size"]
    subband_name = config["subband"]

    if len(image.shape) == 3:
        B, G, R = cv2.split(image)
    else:
        B = image
        G = None
        R = None

    if subband_name == "DUAL" and G is not None:
        # Extract from all 3 channels with matching seeds and majority-vote
        bits_b = _extract_channel(B, bit_length, config, channel_seed=0)
        bits_g = _extract_channel(G, bit_length, config, channel_seed=100)
        bits_r = _extract_channel(R, bit_length, config, channel_seed=200)

        # Majority vote across 3 channels
        final_bits = []
        for i in range(min(len(bits_b), len(bits_g), len(bits_r))):
            votes = [bits_b[i], bits_g[i], bits_r[i]]
            valid = [v for v in votes if v != "X"]
            if not valid:
                final_bits.append("X")
            elif valid.count("1") > valid.count("0"):
                final_bits.append("1")
            else:
                final_bits.append("0")

        return "".join(final_bits)

    else:
        # Single subband/channel mode
        LL, LH, HL, HH = apply_dwt(B)

        if subband_name == "LL":
            subband = LL
        elif subband_name == "LH":
            subband = LH
        else:
            subband = HL

        blocks = split_blocks(subband, block_size)

        np.random.seed(42)
        indices = np.random.permutation(len(blocks))

        if bit_length is None or bit_length > len(blocks):
            bit_length = len(blocks)

        bits = _extract_from_subband(subband, bit_length, indices, block_size)
        return "".join(bits[:bit_length])