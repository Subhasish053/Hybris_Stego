from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from src.ecc.hamming_code import decode_hamming, encode_hamming
from src.ecc.repetition_code import decode_repetition, encode_repetition
from src.embedding.embed_dwt_dct import embed_message
from src.evaluation.psnr import calculate_psnr
from src.evaluation.ssim import calculate_ssim
from src.extraction.extract_dwt_dct import extract_message
from src.preprocessing.binary_to_text import binary_to_text
from src.preprocessing.text_to_binary import text_to_binary
from src.transforms.block_processing import split_blocks
from src.transforms.dwt import apply_dwt
from src.utils.config_loader import load_config


EOF_MARKER = "#####EOF#####"
OUTPUT_ROOT = Path("streamlit_outputs")


@dataclass
class EmbeddingResult:
    original_image: np.ndarray
    stego_image: np.ndarray
    stego_png_bytes: bytes
    stego_path: Path
    original_path: Path
    difference_heatmap: np.ndarray
    metrics: dict[str, float | bool]
    encoded_bit_length: int
    payload_capacity_bits: int
    payload_capacity_chars: int
    session_id: str


@dataclass
class ExtractionResult:
    stego_image: np.ndarray
    extracted_text: str
    eof_found: bool
    decoded_bit_length: int
    raw_bit_length: int


def get_default_config() -> dict[str, Any]:
    return load_config()


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(config)
    normalized["block_size"] = int(normalized["block_size"])
    normalized["embedding_strength"] = float(normalized["embedding_strength"])
    normalized["subband"] = str(normalized["subband"]).upper()
    normalized["ecc_method"] = str(normalized.get("ecc_method", "repetition")).lower()
    return normalized


def load_image_from_bytes(image_bytes: bytes, block_size: int) -> np.ndarray:
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode the uploaded image.")

    image = image.astype(np.float32)
    height, width = image.shape[:2]
    trimmed_h = (height // block_size) * block_size
    trimmed_w = (width // block_size) * block_size

    if trimmed_h == 0 or trimmed_w == 0:
        raise ValueError(f"Image is too small for block size {block_size}.")

    return image[:trimmed_h, :trimmed_w]


def image_to_png_bytes(image: np.ndarray) -> bytes:
    image_uint8 = np.clip(image, 0, 255).astype(np.uint8)
    ok, buffer = cv2.imencode(".png", image_uint8)
    if not ok:
        raise ValueError("Failed to encode image as PNG.")
    return buffer.tobytes()


def save_png(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(path), np.clip(image, 0, 255).astype(np.uint8))
    if not ok:
        raise ValueError(f"Failed to save image to {path}.")


def create_session_paths(prefix: str = "session") -> tuple[str, Path]:
    session_id = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    session_dir = OUTPUT_ROOT / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_id, session_dir


def get_embedding_capacity_bits(image: np.ndarray, config: dict[str, Any]) -> int:
    blue_channel = image[:, :, 0]
    _, lh, hl, _ = apply_dwt(blue_channel)
    block_size = config["block_size"]

    if config["subband"] == "DUAL":
        return len(split_blocks(lh, block_size)) + len(split_blocks(hl, block_size))

    if config["subband"] == "LH":
        return len(split_blocks(lh, block_size))

    if config["subband"] == "HL":
        return len(split_blocks(hl, block_size))

    ll, _, _, _ = apply_dwt(blue_channel)
    return len(split_blocks(ll, block_size))


def encode_bits(bits: str, ecc_method: str) -> str:
    if ecc_method == "hamming":
        return encode_hamming(bits)
    return encode_repetition(bits)


def decode_bits(bits: str, ecc_method: str) -> str:
    if ecc_method == "hamming":
        cleaned = bits.replace("X", "0")
        return decode_hamming(cleaned)
    return decode_repetition(bits)


def estimate_text_capacity(image: np.ndarray, config: dict[str, Any]) -> tuple[int, int]:
    capacity_bits = get_embedding_capacity_bits(image, config)
    ecc_method = config["ecc_method"]

    if ecc_method == "hamming":
        usable_bits = (capacity_bits // 7) * 4
    else:
        usable_bits = capacity_bits // 3

    usable_chars = max(0, (usable_bits // 8) - len(EOF_MARKER))
    return capacity_bits, usable_chars


def build_difference_heatmap(original: np.ndarray, stego: np.ndarray) -> np.ndarray:
    original_uint8 = np.clip(original, 0, 255).astype(np.uint8)
    stego_uint8 = np.clip(stego, 0, 255).astype(np.uint8)

    diff = cv2.absdiff(original_uint8, stego_uint8)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    normalized = cv2.normalize(diff_gray, None, 0, 255, cv2.NORM_MINMAX)
    heatmap = cv2.applyColorMap(normalized.astype(np.uint8), cv2.COLORMAP_INFERNO)
    return cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)


def compare_images(original: np.ndarray, stego: np.ndarray) -> dict[str, float | bool]:
    original_uint8 = np.clip(original, 0, 255).astype(np.uint8)
    stego_uint8 = np.clip(stego, 0, 255).astype(np.uint8)
    abs_diff = cv2.absdiff(original_uint8, stego_uint8)

    return {
        "psnr": float(calculate_psnr(original_uint8.astype(np.float32), stego_uint8.astype(np.float32))),
        "ssim": float(calculate_ssim(original_uint8, stego_uint8)),
        "mean_abs_diff": float(abs_diff.mean()),
        "max_abs_diff": int(abs_diff.max()),
        "pixel_identical": bool(np.array_equal(original_uint8, stego_uint8)),
        "byte_identical_png": image_to_png_bytes(original_uint8.astype(np.float32)) == image_to_png_bytes(stego_uint8.astype(np.float32)),
    }


def run_embedding(cover_bytes: bytes, secret_text: str, config: dict[str, Any]) -> EmbeddingResult:
    config = normalize_config(config)
    image = load_image_from_bytes(cover_bytes, config["block_size"])
    session_id, session_dir = create_session_paths("embed")

    payload_capacity_bits, payload_capacity_chars = estimate_text_capacity(image, config)
    prepared_text = secret_text + EOF_MARKER
    raw_bits = text_to_binary(prepared_text)
    encoded_bits = encode_bits(raw_bits, config["ecc_method"])

    if len(encoded_bits) > payload_capacity_bits:
        raise ValueError(
            f"Message is too large for this image and configuration. "
            f"Capacity is about {payload_capacity_chars} characters."
        )

    stego_image = embed_message(image, encoded_bits, config)
    original_path = session_dir / "original.png"
    stego_path = session_dir / "stego.png"
    save_png(original_path, image)
    save_png(stego_path, stego_image)

    return EmbeddingResult(
        original_image=np.clip(image, 0, 255).astype(np.uint8),
        stego_image=np.clip(stego_image, 0, 255).astype(np.uint8),
        stego_png_bytes=image_to_png_bytes(stego_image),
        stego_path=stego_path,
        original_path=original_path,
        difference_heatmap=build_difference_heatmap(image, stego_image),
        metrics=compare_images(image, stego_image),
        encoded_bit_length=len(encoded_bits),
        payload_capacity_bits=payload_capacity_bits,
        payload_capacity_chars=payload_capacity_chars,
        session_id=session_id,
    )


def run_extraction(stego_bytes: bytes, config: dict[str, Any]) -> ExtractionResult:
    config = normalize_config(config)
    image = load_image_from_bytes(stego_bytes, config["block_size"])
    extracted_bits = extract_message(image, None, config)
    decoded_bits = decode_bits(extracted_bits, config["ecc_method"])
    recovered_text = binary_to_text(decoded_bits)

    eof_found = EOF_MARKER in recovered_text
    if eof_found:
        recovered_text = recovered_text.split(EOF_MARKER)[0]

    return ExtractionResult(
        stego_image=np.clip(image, 0, 255).astype(np.uint8),
        extracted_text=recovered_text,
        eof_found=eof_found,
        decoded_bit_length=len(decoded_bits),
        raw_bit_length=len(extracted_bits),
    )
