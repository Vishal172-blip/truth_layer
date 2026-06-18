from __future__ import annotations

import io
import re
import sys
import os

import pdfplumber

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MAX_PDF_PAGES


class PDFExtractionError(Exception):
    """Raised when PDF text extraction fails for any reason."""


def extract_pages(pdf_bytes: bytes) -> list[dict]:
    pages: list[dict] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                raw_text: str = page.extract_text() or ""

                table_parts: list[str] = []
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        rows = [
                            " | ".join(str(cell) if cell is not None else "" for cell in row)
                            for row in table
                        ]
                        table_parts.append("\n".join(rows))

                combined = raw_text
                if table_parts:
                    combined = combined + "\n\n" + "\n\n".join(table_parts)

                cleaned = re.sub(r"\n{2,}", "\n", combined).strip()
                pages.append({"page": page_num, "text": cleaned})
            except Exception:
                pages.append({"page": page_num, "text": ""})

    return pages


def extract_text(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        raise PDFExtractionError("PDF data is empty or invalid.")

    if not pdf_bytes.startswith(b"%PDF"):
        raise PDFExtractionError("Uploaded file does not appear to be a valid PDF.")

    try:
        all_pages = extract_pages(pdf_bytes)
    except Exception as exc:
        if "password" in str(exc).lower():
            raise PDFExtractionError("PDF is password-protected and cannot be read.")
        raise PDFExtractionError(f"Failed to read PDF: {exc}")

    capped = all_pages[:MAX_PDF_PAGES]
    non_empty = [p for p in capped if p["text"]]

    if not non_empty:
        raise PDFExtractionError(
            "PDF contains no extractable text. It may be a scanned image-only document."
        )

    parts = [f"\n\n--- Page {p['page']} ---\n\n{p['text']}" for p in non_empty]
    return "".join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path_to_pdf>")
        sys.exit(1)

    try:
        with open(sys.argv[1], "rb") as f:
            data = f.read()
        print(extract_text(data))
    except PDFExtractionError as e:
        print(f"PDF extraction error: {e}", file=sys.stderr)
        sys.exit(1)
