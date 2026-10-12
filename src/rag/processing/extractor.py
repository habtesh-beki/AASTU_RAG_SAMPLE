import json
from pathlib import Path

import pymupdf

from rag.config import MIN_TEXT_CHARS, PROCESSED_DIR
from rag.ingestion.loader import make_document_id


def extract_pdf(pdf_path: Path) -> list[dict]:
    """Extract one record per page, with layout blocks, tables and warnings."""
    document_id = make_document_id(pdf_path)
    records = []

    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc):          # index is 0-based
            warnings = []

            # sort=True orders blocks top-to-bottom, left-to-right
            text = page.get_text("text", sort=True).strip()

            blocks = []
            for b in page.get_text("blocks", sort=True):
                x0, y0, x1, y1, btext, _, btype = b[:7]
                if btype == 0 and btext.strip():     # 0 = text block
                    blocks.append({
                        "type": "text",
                        "text": btext.strip(),
                        "bbox": [round(v, 1) for v in (x0, y0, x1, y1)],
                    })

            tables = []
            try:
                for t in page.find_tables().tables:
                    tables.append({
                        "bbox": [round(v, 1) for v in t.bbox],
                        "rows": t.extract(),
                    })
            except Exception as e:
                warnings.append(f"table_extraction_failed: {e}")

            if len(text) < MIN_TEXT_CHARS:
                warnings.append("low_text_possible_scan_needs_ocr")
            if tables:
                warnings.append("tables_found_verify_manually")

            records.append({
                "document_id": document_id,
                "source_file": pdf_path.name,
                "page_number": index + 1,            # 1-based for citations
                "extraction_method": "pymupdf",
                "text": text,
                "blocks": blocks,
                "tables": tables,
                "warnings": warnings,
                "status": "needs_ocr" if "low_text_possible_scan_needs_ocr" in warnings else "success",
            })
    return records


def save_extraction(pdf_path: Path, records: list[dict]) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / f"{make_document_id(pdf_path)}.json"
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return out