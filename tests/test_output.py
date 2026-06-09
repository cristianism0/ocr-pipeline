import json
from pathlib import Path

from src.output import json_from_image, json_from_pdf


def test_json_from_image_creates_file(tmp_path):
    json_from_image(
        file_path="sample.jpeg",
        output_path=str(tmp_path),
        text="texto extraído",
        mean_confidence=85.0,
        low_confidence_words=[{"confidence": 40.0, "text": "obscvro"}],
    )
    output = tmp_path / "sample.json"
    assert output.exists()


def test_json_from_image_structure(tmp_path):
    json_from_image(
        file_path="sample.jpeg",
        output_path=str(tmp_path),
        text="texto extraído",
        mean_confidence=85.0,
        low_confidence_words=[],
    )
    with open(tmp_path / "sample.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "filename" in data
    assert "text" in data
    assert "mean_confidence" in data
    assert isinstance(data["mean_confidence"], float)


def test_json_from_pdf_structure(tmp_path):
    pages = [{"page": "page-0.tiff", "mean_page": 87.3, "low_words": []}]
    json_from_pdf("doc.pdf", str(tmp_path), pages)
    with open(tmp_path / "doc.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "filename" in data
    assert "pages" in data
    assert isinstance(data["pages"], list)
