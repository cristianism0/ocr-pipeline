from datetime import datetime
from pathlib import Path
import pymupdf

def pdf2img(file_path: Path, output_dir: str, ext: str = "jpeg", dpi: int = 300) -> list[Path]:
    """
    Transform each line of a PDF into a image and return all images path:
    Image extensions: jpeg (default), tiff, png
    """
    ext = ext.strip().lower()
    doc = pymupdf.open(file_path)
    paths = []

    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        out = Path(output_dir) / f"page-{page.number}.{ext}"
        pix.pil_save(out, format=ext, dpi=(dpi, dpi), quality=100)
        paths.append(out)

    return paths

def get_ext(file_path: Path) -> tuple[Path, str]:
    """
    Collect the file extension - PDF or Tesseract/PymuPDF supported image.
    """
    file = Path(file_path)
    # tesseract can read file with no extension
    return file, file.suffix.lower()

def path_collector(input_path: str, recursive: bool) -> list[Path]:
    """
    Walker recursivelly or not if its a directory and return all the files inside of it.
    """
    in_path = Path(input_path)
    
    if not in_path.exists():
        return []
        
    pattern = "**/*" if recursive else "*"
    return [f for f in in_path.glob(pattern) if f.is_file()]


def dir_creator(output_path: str) -> str:
    """
    Create the orc-pipe/input and ocr-pipe/output directories in path.
    """
    o_path = Path(output_path)
    parnt = o_path.parent

    if o_path.exists():
        now = datetime.now()
        ndir_name = parnt / f"{now.strftime('%y-%m-%d-%H-%M-%S')}_ocr-pipe"

        ndir_name.mkdir(parents=True)
        return str(ndir_name)

    ndir_name = parnt / "ocr-pipe"
    ndir_name.mkdir(parents=True)
    
    return str(ndir_name)

def dispatcher(file: Path, input_dir: str, ext: str = "jpeg") -> list[Path]:
    """
    If the file is a PDF -> converts to the select kind of image.
    If its a image, pass directly.
    """
    _, suffix = get_ext(file)
    if suffix == ".pdf":
        return pdf2img(file, input_dir, ext=ext)
    return [file]