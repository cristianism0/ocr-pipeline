from pathlib import Path

import pymupdf
from PIL import Image

from src.utils import dir_creator, dispatcher, get_ext, path_collector, pdf2img


def make_pdf(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((100, 100), "test document")
    path = tmp_path / "sample.pdf"
    doc.save(str(path))
    return path


def test_pdf2img_creates_images(tmp_path):
    pdf = make_pdf(tmp_path)
    result = pdf2img(pdf, tmp_path, ext="jpeg")
    assert len(result) > 0
    for p in result:
        assert p.exists()


def test_pdf2img_returns_jpeg_paths(tmp_path):
    pdf = make_pdf(tmp_path)
    result = pdf2img(pdf, tmp_path, ext="jpeg")
    for p in result:
        assert p.suffix == ".jpeg"


def test_pdf2img_returns_png_paths(tmp_path):
    pdf = make_pdf(tmp_path)
    result = pdf2img(pdf, tmp_path, ext="png")
    for p in result:
        assert p.suffix == ".png"


def test_get_ext_pdf():
    _, suffix = get_ext("document.pdf")
    assert suffix == ".pdf"


def test_get_ext_image():
    _, suffix = get_ext("page-0.jpeg")
    assert suffix == ".jpeg"


def test_get_ext_no_extension():
    _, suffix = get_ext("document")
    assert suffix == ""


def test_get_ext_returns_path(tmp_path):
    file = tmp_path / "sample.pdf"
    result, _ = get_ext(file)
    assert isinstance(result, Path)


def test_path_collector_nonexistent():
    result = path_collector(Path("/nonexistent/path"), recursive=False)
    assert result == []


def test_path_collector_empty_dir(tmp_path):
    result = path_collector(tmp_path, recursive=False)
    assert result == []


def test_path_collector_finds_files(tmp_path):
    (tmp_path / "a.pdf").touch()
    (tmp_path / "b.jpeg").touch()
    result = path_collector(tmp_path, recursive=False)
    assert len(result) == 2


def test_path_collector_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.pdf").touch()
    result = path_collector(tmp_path, recursive=True)
    assert len(result) == 1


def test_path_collector_single_file(tmp_path):
    f = tmp_path / "doc.pdf"
    f.touch()
    result = path_collector(f, recursive=False)
    assert result == [f]


def test_dir_creator_creates_output_dir(tmp_path):
    output = dir_creator(tmp_path / "output")
    assert output.exists()
    assert output.name == "output"


def test_dir_creator_returns_path(tmp_path):
    output = dir_creator(tmp_path / "output")
    assert isinstance(output, Path)


def test_dir_creator_timestamp_on_existing(tmp_path):
    dir_creator(tmp_path / "output")
    second = dir_creator(tmp_path / "output")
    assert "output_" in second.name


def test_dispatcher_pdf_branch(tmp_path):
    pdf = make_pdf(tmp_path)
    images, suffix = dispatcher(pdf, tmp_path, ext="jpeg")
    assert suffix == ".pdf"
    assert len(images) > 0
    for p in images:
        assert p.exists()


def test_dispatcher_image_branch(tmp_path):
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    path = tmp_path / "sample.jpeg"
    img.save(path)
    images, suffix = dispatcher(path, tmp_path)
    assert suffix == ".jpeg"
    assert images[0] == path


def test_dispatcher_returns_list(tmp_path):
    pdf = make_pdf(tmp_path)
    images, _ = dispatcher(pdf, tmp_path)
    assert isinstance(images, list)
