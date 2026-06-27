import json
import logging
from pathlib import Path

from numpy import floating

logger = logging.getLogger(__name__)


def json_from_pdf(
    file_path: Path,
    output_path: Path,
    pages: list[dict[str, str]],
    ensure_ascii: bool = False,
) -> Path:
    """
    pages: list of dicts with page, text, mean_confidence, low_confidence_words
    """
    filename = Path(file_path).name
    template = {"filename": filename, "pages": pages}
    out = Path(output_path) / f"{Path(file_path).stem}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=4, ensure_ascii=ensure_ascii)
    logger.info(f"JSON log file was created for pdf {filename} at {out}.")

    return out


def json_from_image(
    file_path: Path,
    output_path: Path,
    text: str,
    mean_confidence: float | floating,
    low_confidence_words: list[dict[str, float]],
    ensure_ascii: bool = False,
) -> Path:
    """
    image: returns a JSON file in path with:
        - filename
        - text
        - mean_confidence
        - list of low_confidence_words)
    """
    filename = Path(file_path).name
    extension = Path(file_path).suffix

    template = {
        "filename": filename,
        "filetype": extension,
        "text": text,
        "mean_confidence": mean_confidence,
        "low_confidence_words": low_confidence_words,
    }

    out = Path(output_path) / f"{Path(file_path).stem}.json"

    with open(out, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=4, ensure_ascii=ensure_ascii)
    logger.info(f"JSON log file was created for image {filename} at {out}.")
    return out
