import fitz  # pymupdf


def extract_text_from_pdf(file_bytes: bytes) -> list[dict]:
    """Extract text from a PDF file, returning a list of {page, text} dicts."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({"page": page_num + 1, "text": text})
    doc.close()
    return pages
