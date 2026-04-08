import cv2
import numpy as np

from src.transforms.dwt import apply_dwt, inverse_dwt
from src.transforms.dct import dct2, idct2
from src.transforms.block_processing import split_blocks, merge_blocks



def _embed_in_subband(subband, bits, indices, delta, block_size):
    """Embed bits into a single subband using adaptive coefficient relationship."""
    blocks = split_blocks(subband, block_size)
    base_margin = 3 * delta

    for i, bit in enumerate(bits):
        idx = indices[i]
        block = blocks[idx]
        dct_block = dct2(block)

        margin = base_margin

        C1 = dct_block[0, 1]
        C3 = dct_block[1, 1]
        mid = (C1 + C3) / 2.0

        if bit == "1":
            if (C1 - C3) < margin:
                C1 = mid + margin / 2
                C3 = mid - margin / 2
        else:
            if (C3 - C1) < margin:
                C1 = mid - margin / 2
                C3 = mid + margin / 2

        dct_block[0, 1] = C1
        dct_block[1, 1] = C3

        blocks[idx] = idct2(dct_block)

    return merge_blocks(blocks, subband.shape, block_size)


def _embed_channel(channel, bits, config, channel_seed=0):
    """Embed bits into a single color channel using DWT+DCT across LH and HL."""
    block_size = config["block_size"]
    delta = config["embedding_strength"]

    LL, LH, HL, HH = apply_dwt(channel)

    blocks_lh = split_blocks(LH, block_size)
    blocks_hl = split_blocks(HL, block_size)
    cap_lh = len(blocks_lh)
    cap_hl = len(blocks_hl)
    total_capacity = cap_lh + cap_hl

    bits = bits[:total_capacity]

    # Interleave bits: even -> LH, odd -> HL
    bits_lh = [bits[i] for i in range(0, len(bits), 2)]
    bits_hl = [bits[i] for i in range(1, len(bits), 2)]
    bits_lh = bits_lh[:cap_lh]
    bits_hl = bits_hl[:cap_hl]

    # Different seeds per channel to decorrelate errors across channels
    np.random.seed(42 + channel_seed)
    indices_lh = np.random.permutation(cap_lh)
    np.random.seed(84 + channel_seed)
    indices_hl = np.random.permutation(cap_hl)

    LH = _embed_in_subband(LH, bits_lh, indices_lh, delta, block_size)
    HL = _embed_in_subband(HL, bits_hl, indices_hl, delta, block_size)

    modified = inverse_dwt(LL, LH, HL, HH)
    modified = modified[:channel.shape[0], :channel.shape[1]]
    return modified


def embed_message(image, bits, config):

    block_size = config["block_size"]
    subband_name = config["subband"]
    delta = config["embedding_strength"]

    B, G, R = cv2.split(image)

    LL, LH, HL, HH = apply_dwt(B)

    if subband_name == "DUAL":
        # Embed same bits across ALL 3 color channels (B, G, R) for 3x redundancy
        # Each channel uses dual subband (LH + HL) with different permutations
        modified_B = _embed_channel(B, bits, config, channel_seed=0)
        modified_G = _embed_channel(G, bits, config, channel_seed=100)
        modified_R = _embed_channel(R, bits, config, channel_seed=200)

        pass  # visualizations handled by experiment runner

        stego = cv2.merge((modified_B, modified_G, modified_R))

    else:
        # Single subband mode (original behavior)
        if subband_name == "LL":
            subband = LL
        elif subband_name == "LH":
            subband = LH
        else:
            subband = HL

        blocks = split_blocks(subband, block_size)
        capacity = len(blocks)
        bits = bits[:capacity]

        np.random.seed(42)
        indices = np.random.permutation(len(blocks))

        modified_subband = _embed_in_subband(subband, bits, indices, delta, block_size)

        if subband_name == "LL":
            LL = modified_subband
        elif subband_name == "LH":
            LH = modified_subband
        else:
            HL = modified_subband

        modified_B = inverse_dwt(LL, LH, HL, HH)
        modified_B = modified_B[:B.shape[0], :B.shape[1]]

        stego = cv2.merge((modified_B, G, R))

    return stego