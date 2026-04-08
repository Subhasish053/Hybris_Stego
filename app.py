from __future__ import annotations

from html import escape

import streamlit as st

from src.utils.app_service import (
    estimate_text_capacity,
    get_default_config,
    load_image_from_bytes,
    normalize_config,
    run_embedding,
    run_extraction,
)


st.set_page_config(
    page_title="StegaVision | Hybrid DWT-DCT Steganography",
    page_icon=":lock:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-top: #07131a;
            --bg-bottom: #f5efe4;
            --surface: rgba(255, 252, 246, 0.88);
            --surface-strong: rgba(255, 255, 255, 0.96);
            --ink: #10212a;
            --muted: #52636c;
            --line: rgba(16, 33, 42, 0.10);
            --accent: #0f766e;
            --accent-soft: rgba(15, 118, 110, 0.12);
            --accent-2: #c2410c;
            --success: #0f9f6e;
            --warning: #b96b00;
            --danger: #b42318;
            --hero: linear-gradient(135deg, rgba(15,118,110,0.92), rgba(8,47,73,0.92) 55%, rgba(194,65,12,0.88));
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 118, 110, 0.22), transparent 32%),
                radial-gradient(circle at top right, rgba(194, 65, 12, 0.18), transparent 28%),
                linear-gradient(180deg, var(--bg-top) 0%, #17303b 20%, #d9ddd6 55%, var(--bg-bottom) 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 2.5rem 2.6rem 2.2rem 2.6rem;
            background: var(--hero);
            box-shadow: 0 26px 70px rgba(7, 19, 26, 0.30);
            color: #f8fafc;
            margin-bottom: 1.5rem;
        }

        .hero::after {
            content: "";
            position: absolute;
            inset: auto -10% -55% auto;
            width: 340px;
            height: 340px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 65%);
        }

        .hero h1 {
            margin: 0;
            font-size: 3rem;
            line-height: 1.02;
            letter-spacing: -0.04em;
        }

        .hero p {
            max-width: 52rem;
            margin: 0.9rem 0 0 0;
            color: rgba(248, 250, 252, 0.88);
            font-size: 1.03rem;
            line-height: 1.7;
        }

        .hero-strip {
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
            margin-top: 1.25rem;
        }

        .hero-pill {
            padding: 0.42rem 0.82rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.16);
            color: #f8fafc;
            font-size: 0.84rem;
            font-weight: 600;
        }

        .section-card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1.45rem 1.35rem;
            box-shadow: 0 18px 45px rgba(16, 33, 42, 0.08);
            backdrop-filter: blur(10px);
        }

        .info-card {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(16, 33, 42, 0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
        }

        .status-chip {
            display: inline-block;
            margin-bottom: 0.6rem;
            padding: 0.32rem 0.7rem;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            border: 1px solid rgba(15, 118, 110, 0.16);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .copy-box {
            background: rgba(8, 47, 73, 0.96);
            border: 1px solid rgba(15, 118, 110, 0.18);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            color: #eff6ff;
            font-family: "Consolas", "Courier New", monospace;
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.7;
        }

        .summary-box {
            background: rgba(15, 118, 110, 0.07);
            border: 1px solid rgba(15, 118, 110, 0.14);
            border-radius: 18px;
            padding: 1rem 1.1rem;
        }

        .summary-box p {
            margin: 0.35rem 0;
            color: var(--muted);
            line-height: 1.65;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.66);
            border: 1px solid rgba(16, 33, 42, 0.08);
            border-radius: 18px;
            padding: 0.85rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--accent);
            font-weight: 700;
        }

        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(9, 25, 34, 0.98), rgba(16, 46, 58, 0.96));
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        div[data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        div[data-testid="stSidebar"] .stSelectbox label,
        div[data-testid="stSidebar"] .stSlider label {
            color: #d7e5ea;
        }

        div.stButton > button,
        div.stDownloadButton > button {
            border: 0;
            border-radius: 14px;
            font-weight: 700;
            padding: 0.72rem 1.2rem;
            background: linear-gradient(135deg, #0f766e, #115e59);
            color: white;
            box-shadow: 0 10px 24px rgba(15, 118, 110, 0.24);
        }

        div.stDownloadButton > button {
            background: linear-gradient(135deg, #c2410c, #9a3412);
            box-shadow: 0 10px 24px rgba(194, 65, 12, 0.24);
        }

        textarea {
            border-radius: 14px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(config: dict) -> None:
    st.markdown(
        f"""
        <section class="hero">
            <h1>StegaVision</h1>
            <p>
                A deployable Streamlit front end for the repository's real hybrid DWT-DCT
                image steganography pipeline. Hide text inside a cover image, compare the
                result visually, and recover the message through the matching extraction path.
            </p>
            <div class="hero-strip">
                <span class="hero-pill">Wavelet: {config.get("wavelet", "haar").title()}</span>
                <span class="hero-pill">Subband: {config["subband"]}</span>
                <span class="hero-pill">Block size: {config["block_size"]}x{config["block_size"]}</span>
                <span class="hero-pill">ECC: {config["ecc_method"].title()}</span>
                <span class="hero-pill">Strength: {config["embedding_strength"]}</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> dict:
    defaults = normalize_config(get_default_config())

    st.sidebar.markdown("## Control Panel")
    st.sidebar.caption(
        "Use the same settings for extraction that were used during embedding."
    )

    with st.sidebar.expander("Embedding Settings", expanded=True):
        block_size = st.selectbox(
            "Block Size",
            options=[8, 16],
            index=[8, 16].index(defaults["block_size"]) if defaults["block_size"] in [8, 16] else 0,
            help="Smaller blocks increase capacity. Larger blocks reduce available payload.",
        )
        subband = st.selectbox(
            "Subband Mode",
            options=["DUAL", "LH", "HL", "LL"],
            index=["DUAL", "LH", "HL", "LL"].index(defaults["subband"]) if defaults["subband"] in ["DUAL", "LH", "HL", "LL"] else 0,
            help="Expose only modes that map to the current backend.",
        )
        embedding_strength = st.slider(
            "Embedding Strength",
            min_value=5,
            max_value=80,
            value=int(defaults["embedding_strength"]),
            help="Higher values improve separation between embedded coefficients but increase distortion.",
        )
        ecc_method = st.selectbox(
            "Error Correction",
            options=["hamming", "repetition"],
            index=["hamming", "repetition"].index(defaults["ecc_method"]) if defaults["ecc_method"] in ["hamming", "repetition"] else 0,
            help="Choose the ECC method implemented in the repository.",
        )

    with st.sidebar.expander("How it Works", expanded=False):
        st.markdown(
            """
            - `DUAL` mode embeds the same payload across all three color channels.
            - Extraction uses majority voting plus ECC decoding.
            - Hamming is more space efficient.
            - Repetition is simpler and more redundant.
            """
        )

    with st.sidebar.expander("Project Modules", expanded=False):
        st.markdown(
            """
            - `src.embedding.embed_dwt_dct`
            - `src.extraction.extract_dwt_dct`
            - `src.ecc.hamming_code`
            - `src.ecc.repetition_code`
            - `src.evaluation.psnr`
            - `src.evaluation.ssim`
            """
        )

    config = dict(defaults)
    config.update(
        {
            "block_size": block_size,
            "subband": subband,
            "embedding_strength": embedding_strength,
            "ecc_method": ecc_method,
        }
    )
    return normalize_config(config)


def show_capacity_hint(cover_file, config: dict) -> None:
    if not cover_file:
        return

    try:
        image = load_image_from_bytes(cover_file.getvalue(), config["block_size"])
        capacity_bits, capacity_chars = estimate_text_capacity(image, config)
        height, width = image.shape[:2]
        st.info(
            f"Loaded image: {width}x{height} px after block alignment. "
            f"Estimated capacity with current settings: about {capacity_chars:,} characters "
            f"({capacity_bits:,} encoded bits)."
        )
    except Exception as exc:
        st.warning(f"Capacity estimate unavailable: {exc}")


def is_probably_readable_text(value: str) -> bool:
    if not value:
        return False
    printable_count = sum(ch.isprintable() or ch in "\n\r\t" for ch in value)
    return (printable_count / len(value)) >= 0.9


def render_embed_tab(config: dict) -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="status-chip">Embed Workflow</div>', unsafe_allow_html=True)
    st.subheader("Embed Message")
    st.caption(
        "Upload a cover image and provide the secret text. The app uses the repository's"
        " DWT-DCT embedding flow with the selected ECC settings."
    )

    col_left, col_right = st.columns(2)
    with col_left:
        cover_file = st.file_uploader(
            "Cover Image",
            type=["png", "jpg", "jpeg"],
            key="embed_cover",
            help="PNG and JPEG inputs are supported.",
        )
        if cover_file:
            st.image(cover_file.getvalue(), caption="Uploaded cover image", use_container_width=True)

    with col_right:
        secret_text = st.text_area(
            "Secret Message",
            height=180,
            placeholder="Enter the message to hide inside the image.",
            key="embed_secret",
        )
        if secret_text:
            st.caption(f"Message length: {len(secret_text)} characters")

    show_capacity_hint(cover_file, config)
    st.markdown(
        """
        <div class="info-card">
            The stego image should differ from the original at the pixel level while remaining
            visually very close. The quality metrics below help verify that tradeoff.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Embed Message", key="embed_action", use_container_width=True):
        if not cover_file:
            st.error("Please upload a cover image before embedding.")
        elif not secret_text or not secret_text.strip():
            st.error("Please enter a secret message before embedding.")
        else:
            with st.spinner("Running the real embedding pipeline..."):
                try:
                    result = run_embedding(cover_file.getvalue(), secret_text, config)
                    st.session_state["last_embedding"] = result
                    st.session_state["last_secret_text"] = secret_text
                    st.session_state["last_config"] = dict(config)
                    st.session_state["last_extraction"] = None
                except Exception as exc:
                    st.error(f"Embedding failed: {exc}")

    result = st.session_state.get("last_embedding")
    if result:
        st.divider()
        st.success("Stego image generated successfully.")

        metrics = result.metrics
        metric_cols = st.columns(5)
        metric_cols[0].metric("PSNR", f"{metrics['psnr']:.2f} dB")
        metric_cols[1].metric("SSIM", f"{metrics['ssim']:.4f}")
        metric_cols[2].metric("Mean Delta", f"{metrics['mean_abs_diff']:.3f}")
        metric_cols[3].metric("Pixel Match", "No" if not metrics["pixel_identical"] else "Yes")
        metric_cols[4].metric("Bits Used", f"{result.encoded_bit_length:,}")

        image_cols = st.columns(2)
        image_cols[0].image(
            result.original_image[:, :, ::-1],
            caption="Original cover image",
            use_container_width=True,
        )
        image_cols[1].image(
            result.stego_image[:, :, ::-1],
            caption="Generated stego image",
            use_container_width=True,
        )

        st.download_button(
            "Download Stego Image",
            data=result.stego_png_bytes,
            file_name="stego_image.png",
            mime="image/png",
            use_container_width=True,
        )

        compare_cols = st.columns([1.2, 1])
        with compare_cols[0]:
            st.image(
                result.difference_heatmap,
                caption="Difference heatmap",
                use_container_width=True,
            )
        with compare_cols[1]:
            st.markdown(
                """
                <div class="summary-box">
                    <p><strong>Comparison summary</strong></p>
                    <p>The original and stego images are checked for exact pixel equality, and this
                    should be false when embedding succeeds.</p>
                    <p>PSNR and SSIM quantify how little the image changed visually even though data
                    was embedded in the transform-domain coefficients.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("Technical Details", expanded=False):
            left, right = st.columns(2)
            with left:
                st.json(
                    {
                        "encoded_bit_length": result.encoded_bit_length,
                        "payload_capacity_bits": result.payload_capacity_bits,
                        "payload_capacity_chars": result.payload_capacity_chars,
                        "session_id": result.session_id,
                        "stego_path": str(result.stego_path),
                        "original_path": str(result.original_path),
                    }
                )
            with right:
                st.json(
                    {
                        "psnr_db": round(metrics["psnr"], 4),
                        "ssim": round(metrics["ssim"], 6),
                        "mean_abs_diff": round(metrics["mean_abs_diff"], 6),
                        "max_abs_diff": metrics["max_abs_diff"],
                        "pixel_identical": metrics["pixel_identical"],
                        "byte_identical_png": metrics["byte_identical_png"],
                    }
                )

    st.markdown("</div>", unsafe_allow_html=True)


def render_extract_tab(config: dict) -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="status-chip">Extract Workflow</div>', unsafe_allow_html=True)
    st.subheader("Extract Message")
    st.caption(
        "Upload a stego image and run the matching extraction pipeline to recover the hidden text."
    )

    stego_file = st.file_uploader(
        "Stego Image",
        type=["png", "jpg", "jpeg"],
        key="extract_stego",
    )
    if stego_file:
        st.image(stego_file.getvalue(), caption="Uploaded stego image", use_container_width=True)

    if st.button("Extract Message", key="extract_action", use_container_width=True):
        if not stego_file:
            st.error("Please upload a stego image before extraction.")
        else:
            with st.spinner("Running the extraction pipeline..."):
                try:
                    result = run_extraction(stego_file.getvalue(), config)
                    st.session_state["last_extraction"] = result
                except Exception as exc:
                    st.error(f"Extraction failed: {exc}")

    result = st.session_state.get("last_extraction")
    if result:
        st.divider()
        if result.extracted_text:
            st.success("Extraction completed.")
        else:
            st.warning("Extraction completed, but no readable message was recovered.")

        if not result.eof_found:
            st.warning(
                "EOF marker not found. The extraction settings may not match the embedding settings,"
                " or the image may have been modified after embedding."
            )
        elif not is_probably_readable_text(result.extracted_text):
            st.warning("Decoded text contains unusual characters. Review the extraction settings.")

        safe_text = escape(result.extracted_text) if result.extracted_text else "No readable text recovered."
        st.markdown(
            f'<div class="copy-box">{safe_text}</div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "Copy-friendly Text",
            value=result.extracted_text,
            height=150,
            key="recovered_message_box",
        )

        previous_secret = st.session_state.get("last_secret_text")
        if previous_secret and result.extracted_text == previous_secret:
            st.success("Round-trip verified: extracted text matches the last embedded message.")
        elif previous_secret and result.eof_found:
            st.info("A message was recovered, but it does not match the last embedded text in this session.")

        with st.expander("Technical Details", expanded=False):
            st.json(
                {
                    "eof_marker_found": result.eof_found,
                    "decoded_bit_length": result.decoded_bit_length,
                    "raw_bit_length": result.raw_bit_length,
                    "extracted_text_length": len(result.extracted_text) if result.extracted_text else 0,
                }
            )

    st.markdown("</div>", unsafe_allow_html=True)


def render_about_tab() -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("About the Project")
    st.markdown(
        """
        This app is a user-facing wrapper around the repository's existing steganography backend.
        It keeps the real research pipeline intact and exposes it as a deployable Streamlit app.
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            ### Embedding Flow
            1. Text is converted to binary.
            2. ECC is applied.
            3. The image is split into color channels.
            4. DWT generates transform subbands.
            5. DCT coefficient pairs are modified block by block.
            6. Inverse transforms reconstruct the stego image.
            """
        )
    with col2:
        st.markdown(
            """
            ### Extraction Flow
            1. The stego image is decomposed again by channel.
            2. DWT and DCT expose the embedded coefficient relationships.
            3. Channel votes are combined in `DUAL` mode.
            4. ECC decoding reconstructs the payload bits.
            5. Binary data is converted back into text.
            """
        )

    st.markdown(
        """
        ### Backend Modules Used
        - `src.embedding.embed_dwt_dct`
        - `src.extraction.extract_dwt_dct`
        - `src.ecc.hamming_code`
        - `src.ecc.repetition_code`
        - `src.transforms.dwt`
        - `src.transforms.dct`
        - `src.evaluation.psnr`
        - `src.evaluation.ssim`
        - `src.utils.app_service`
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    inject_styles()
    config = render_sidebar()
    render_hero(config)

    tabs = st.tabs(["Embed Message", "Extract Message", "About"])
    with tabs[0]:
        render_embed_tab(config)
    with tabs[1]:
        render_extract_tab(config)
    with tabs[2]:
        render_about_tab()


if __name__ == "__main__":
    main()
