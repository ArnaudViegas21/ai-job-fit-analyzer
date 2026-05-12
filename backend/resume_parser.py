from io import BytesIO
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text).strip()


def parse_docx(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))

    return "\n".join(
        [paragraph.text for paragraph in document.paragraphs]
    ).strip()


def parse_resume(filename: str, file_bytes: bytes) -> str:
    filename = filename.lower()

    if filename.endswith(".pdf"):
        return parse_pdf(file_bytes)

    if filename.endswith(".docx"):
        return parse_docx(file_bytes)

    if filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()

    raise ValueError(
        "Unsupported file type. Please upload PDF, DOCX, or TXT."
    )