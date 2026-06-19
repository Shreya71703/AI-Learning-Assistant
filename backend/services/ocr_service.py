import os
import pytesseract
from pypdf import PdfReader
from pdf2image import convert_from_path
from typing import Tuple

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\poppler-26.02.0\Library\bin"

if os.name == "nt" and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_pdf(pdf_path: str) -> Tuple[str, int]:
    """
    Extract text from a PDF. Try extracting text instantly first.
    Falls back to slow OCR only if the PDF is scanned (contains no text layer).
    """
    # 1. Try instant text extraction via pypdf
    try:
        reader = PdfReader(pdf_path)
        pages_text = []
        page_count = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(f"[Page {i + 1}]\n{text.strip()}")
                
        full_text = "\n\n".join(pages_text)
        if full_text.strip():
            return full_text, page_count
    except Exception:
        # Fallback to OCR on failure
        pass

    # 2. Slow OCR Fallback (for scanned images)
    try:
        pages = convert_from_path(
            pdf_path,
            dpi=150,  # Reduced DPI to speed up OCR slightly
            poppler_path=POPPLER_PATH if os.name == "nt" else None
        )
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to images: {str(e)}")

    all_text = []
    for i, page_image in enumerate(pages):
        try:
            text = pytesseract.image_to_string(
                page_image,
                lang="eng",
                config="--psm 6"
            )
            if text.strip():
                all_text.append(f"[Page {i + 1}]\n{text.strip()}")
        except Exception as e:
            all_text.append(f"[Page {i + 1}] OCR failed: {str(e)}")

    return "\n\n".join(all_text), len(pages)
