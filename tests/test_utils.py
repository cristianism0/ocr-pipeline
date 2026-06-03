from pathlib import Path
from src.utils import get_ext, path_collector, dispatcher
import pymupdf
from src.utils import pdf2img, dispatcher

def make_pdf(tmp_path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((100, 100), "test document")
    path = tmp_path / "sample.pdf"
    doc.save(str(path))
    return path

def test_pdf2img_creates_images(tmp_path):
    pdf = make_pdf(tmp_path)
    result = pdf2img(pdf, str(tmp_path), ext="jpeg")
    assert len(result) > 0
    for p in result:
        assert Path(p).exists()

def test_pdf2img_returns_paths(tmp_path):
    pdf = make_pdf(tmp_path)
    result = pdf2img(pdf, str(tmp_path), ext="jpeg")
    for p in result:
        assert str(p).endswith(".jpeg")

def test_dispatcher_pdf_branch(tmp_path):
    pdf = make_pdf(tmp_path)
    images, suffix = dispatcher(pdf, str(tmp_path), ext="jpeg")
    assert suffix == ".pdf"
    assert len(images) > 0

def test_dispatcher_image_branch(tmp_path):
    from PIL import Image
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    path = tmp_path / "sample.jpeg"
    img.save(path)
    images, suffix = dispatcher(path, str(tmp_path))
    assert suffix == ".jpeg"
    assert images[0] == path

def test_get_ext_pdf():
    _, suffix = get_ext("document.pdf")
    assert suffix == ".pdf"

def test_get_ext_image():
    _, suffix = get_ext("page-0.jpeg")
    assert suffix == ".jpeg"

def test_get_ext_no_extension():
    _, suffix = get_ext("document")
    assert suffix == ""

def test_path_collector_nonexistent():
    result = path_collector("/nonexistent/path", recursive=False)
    assert result == []

def test_path_collector_empty_dir(tmp_path):
    # tmp_path é fixture do pytest — cria diretório temporário real
    result = path_collector(str(tmp_path), recursive=False)
    assert result == []

def test_path_collector_finds_files(tmp_path):
    (tmp_path / "a.pdf").touch()
    (tmp_path / "b.jpeg").touch()
    result = path_collector(str(tmp_path), recursive=False)
    assert len(result) == 2

def test_path_collector_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.pdf").touch()
    result = path_collector(str(tmp_path), recursive=True)
    assert len(result) == 1

def test_dir_creator_creates_ocr_pipe(tmp_path):
    from src.utils import dir_creator
    input_dir, output_dir = dir_creator(str(tmp_path / "ocr-pipe"))
    assert Path(input_dir).exists()
    assert Path(output_dir).exists()

def test_dir_creator_timestamp_on_existing(tmp_path):
    from src.utils import dir_creator
    # primeira execução
    dir_creator(str(tmp_path / "ocr-pipe"))
    # segunda — deve criar com timestamp
    input_dir, _ = dir_creator(str(tmp_path / "ocr-pipe"))
    assert "_ocr-pipe" in input_dir