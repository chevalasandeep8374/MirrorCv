import os
import shutil
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Candidate paths for LibreOffice across Windows, Linux, and macOS
LIBREOFFICE_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/usr/bin/libreoffice",
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_libreoffice_executable() -> Optional[str]:
    """Locates the LibreOffice executable across standard operating system paths."""
    # 1. Check PATH
    for cmd in ["soffice", "libreoffice"]:
        p = shutil.which(cmd)
        if p and os.path.exists(p):
            return p

    # 2. Check candidate filesystem paths
    for p in LIBREOFFICE_PATHS:
        if os.path.exists(p):
            return p

    return None


def convert_docx_to_pdf(
    docx_path: str,
    output_pdf_path: Optional[str] = None,
    allow_fallback: Optional[bool] = None,
) -> str:
    """Converts a DOCX file to PDF using LibreOffice headless.

    Fails closed: raises RuntimeError unless ALLOW_FALLBACK_RENDERER=1 is explicitly set.
    """
    path, _ = convert_docx_to_pdf_with_metadata(docx_path, output_pdf_path, allow_fallback)
    return path


def convert_docx_to_pdf_with_metadata(
    docx_path: str,
    output_pdf_path: Optional[str] = None,
    allow_fallback: Optional[bool] = None,
) -> tuple[str, str]:
    """Converts a DOCX file to PDF and returns (pdf_path, renderer_name)."""
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"Input DOCX file not found: {docx_path}")

    docx_dir = os.path.dirname(os.path.abspath(docx_path))
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    expected_pdf = os.path.join(docx_dir, f"{base_name}.pdf")

    if output_pdf_path is None:
        output_pdf_path = expected_pdf

    if allow_fallback is None:
        env_flag = os.environ.get("ALLOW_FALLBACK_RENDERER", "").lower()
        allow_fallback = env_flag in ("1", "true", "yes")

    soffice_bin = find_libreoffice_executable()

    if soffice_bin:
        from app.services.process_concurrency import libreoffice_sync_limit
        import tempfile
        user_profile_dir = tempfile.mkdtemp(prefix="lo_user_profile_")
        user_uri = f"file:///{user_profile_dir.replace(os.sep, '/')}"
        logger.info(f"Converting {docx_path} to PDF using LibreOffice at {soffice_bin}")
        cmd = [
            soffice_bin,
            f"-env:UserInstallation={user_uri}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            os.path.dirname(os.path.abspath(output_pdf_path)),
            docx_path,
        ]
        try:
            with libreoffice_sync_limit(timeout=30.0):
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            if res.returncode != 0:
                logger.warning(f"LibreOffice conversion warning: {res.stderr.decode('utf-8', errors='ignore')}")
        finally:
            shutil.rmtree(user_profile_dir, ignore_errors=True)

        if os.path.exists(expected_pdf) and expected_pdf != output_pdf_path:
            shutil.move(expected_pdf, output_pdf_path)

        if os.path.exists(output_pdf_path):
            return output_pdf_path, "libreoffice"

    # Fails closed if LibreOffice is missing or conversion failed
    if not allow_fallback:
        raise RuntimeError(
            "Production render failed: LibreOffice executable not found and fallback renderer is disabled. "
            "Real LibreOffice is required for production rendering. Set ALLOW_FALLBACK_RENDERER=1 only for offline unit test mocks."
        )

    logger.info("ALLOW_FALLBACK_RENDERER is enabled; generating test fallback PDF via PyMuPDF...")
    pdf_path = _generate_fallback_pdf_from_docx(docx_path, output_pdf_path)
    return pdf_path, "pymupdf_fallback"


def _generate_fallback_pdf_from_docx(docx_path: str, output_pdf_path: str) -> str:
    """Fallback generator using docx content and PyMuPDF to create a valid multi-page PDF."""
    from docx import Document
    import fitz  # PyMuPDF

    doc = Document(docx_path)
    pdf = fitz.open()

    # A4 dimensions in points: 595 x 842
    page_width, page_height = 595.0, 842.0
    page = pdf.new_page(width=page_width, height=page_height)

    margin_x = 40.0
    y_pos = 40.0
    line_height = 14.0

    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            y_pos += 6.0
            continue

        if y_pos > (page_height - 50.0):
            page = pdf.new_page(width=page_width, height=page_height)
            y_pos = 40.0

        # Determine styling
        is_bold = any(r.bold for r in p.runs)
        font_size = 10.0
        if p.runs and p.runs[0].font.size:
            try:
                font_size = p.runs[0].font.size.pt
            except Exception:
                pass

        if font_size >= 16.0:
            font_size = 18.0
            line_height = 22.0
        elif font_size >= 12.0:
            line_height = 16.0
        else:
            line_height = 13.0

        fontname = "helv"
        color = (0.05, 0.1, 0.2)
        if is_bold:
            fontname = "hebo"

        page.insert_text(
            fitz.Point(margin_x, y_pos),
            txt[:100],  # insert first line
            fontsize=font_size,
            fontname=fontname,
            color=color,
        )
        y_pos += line_height

    pdf.save(output_pdf_path)
    pdf.close()
    return output_pdf_path
