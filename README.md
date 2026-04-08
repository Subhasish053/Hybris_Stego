# StegaVision: Hybrid DWT-DCT Image Steganography App

StegaVision is a Streamlit application built on top of the repository's real image steganography backend. It embeds secret text into a cover image with a hybrid DWT-DCT pipeline, then extracts the hidden text through the matching reverse process.

## What the app does

- Embeds text into uploaded PNG, JPG, or JPEG images
- Extracts hidden text from generated stego images
- Compares original and stego images with PSNR, SSIM, and a difference heatmap
- Supports the repository's existing ECC options: Hamming and repetition coding
- Saves generated outputs to `streamlit_outputs/` for repeatable runs

## Backend entry points used

- `src.embedding.embed_dwt_dct.embed_message`
- `src.extraction.extract_dwt_dct.extract_message`
- `src.utils.app_service.run_embedding`
- `src.utils.app_service.run_extraction`

The Streamlit app does not replace the underlying math. It wraps the existing pipeline so uploaded files and user-entered text can flow through the actual backend.

## Install

```bash
pip install -r requirements.txt
```

If you are using the included virtual environment on Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run locally

```bash
streamlit run app.py
```

If you are using the included virtual environment on Windows:

```bash
.venv\Scripts\streamlit.exe run app.py
```

## Expected user workflow

### Embed

1. Open the `Embed Message` tab.
2. Upload a cover image.
3. Enter the secret text.
4. Click `Embed Message`.
5. Review the original vs stego comparison, PSNR, SSIM, and difference heatmap.
6. Download the generated stego PNG.

### Extract

1. Open the `Extract Message` tab.
2. Upload the stego image.
3. Use the same settings that were used during embedding.
4. Click `Extract Message`.
5. Review the recovered text and technical details.

## Configuration

Default settings are loaded from `configs/config.yaml`:

- `block_size`
- `wavelet`
- `embedding_strength`
- `subband`
- `ecc_method`

The sidebar only exposes settings that map to the current backend implementation.

## Testing

Run the end-to-end verification suite with:

```bash
python test_roundtrip.py
```

Using the included virtual environment on Windows:

```bash
.venv\Scripts\python.exe test_roundtrip.py
```

The test suite covers:

- Round-trip embedding and extraction with exact text match
- JPG and PNG cover images
- Hamming and repetition ECC modes
- Oversized-message validation
- Re-run stability
- Pixel-level difference between cover and stego images

## Deployment notes

The app is structured to run from the repository root with:

```bash
streamlit run app.py
```

That layout is suitable for local use and for later deployment on platforms such as Streamlit Community Cloud or Render.
