from pathlib import Path
import json

def json_from_pdf(file_path: str, output_path: str, pages: list[dict] , ensure_ascii: bool = False):
    """
    pages: list of dicts with page, text, mean_confidence, low_confidence_words
    """
    filename = Path(file_path).name
    template = {
        "filename": filename,
        "pages": pages
    }
    out = Path(output_path) / f"{Path(file_path).stem}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=4, ensure_ascii=ensure_ascii)


def json_from_image(file_path: str, output_path: str, text: str, mean_confidence: float, low_confidence_words: list, ensure_ascii: bool = False):
    """
    Direct image
    """
    filename = Path(file_path).name
    template = {
        "filename": filename,
        "text": text,
        "mean_confidence": mean_confidence,
        "low_confidence_words": low_confidence_words
    }
    
    out = Path(output_path) / f"{Path(file_path).stem}.json"
    
    with open(out, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=4, ensure_ascii=ensure_ascii)
