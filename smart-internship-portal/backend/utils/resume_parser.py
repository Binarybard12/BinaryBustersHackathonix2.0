import io
import docx2txt
from pdfminer.high_level import extract_text

def parse_resume(filename: str, content: bytes) -> str:
    """Parses PDF/DOCX content into text."""
    if filename.endswith(".pdf"):
        with io.BytesIO(content) as fh:
            text = extract_text(fh)
        return text
    elif filename.endswith(".docx"):
        with io.BytesIO(content) as fh:
            text = docx2txt.process(fh)
        return text
    else:
        # Fallback to plain text if possible
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return ""
