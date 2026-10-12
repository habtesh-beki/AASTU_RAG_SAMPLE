from pathlib import Path
from rag.config import RAW_DIR


def discover_pdfs(directory: Path = RAW_DIR) -> list[Path]:
    """Return all valid PDF files in the directory, sorted."""
    pdfs = []
    for path in sorted(directory.glob("*.pdf")):
        if path.is_file() and path.stat().st_size > 0:
            pdfs.append(path)
    return pdfs


def make_document_id(path: Path) -> str:
    return path.stem.lower().replace(" ", "-").replace("_", "-")