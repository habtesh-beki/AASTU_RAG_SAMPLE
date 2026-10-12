from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# A page with fewer characters than this is flagged as possibly scanned
MIN_TEXT_CHARS = 30