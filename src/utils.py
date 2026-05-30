import pymupdf

def pdf2img(file_path: str, output_dir: str, ext: str = "jpeg", dpi: int = 300) -> list[str]:
    """
    Transform each line of a PDF into a image and return all images path:
    Image extensions: jpeg (default), tiff, png
    """
    ext = ext.strip().lower()
    doc = pymupdf.open(file_path)
    paths = []

    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        out = f"{output_dir}/page-{page.number}.{ext}"
        pix.pil_save(out, format=ext, dpi=(dpi, dpi), quality=100)
        paths.append(out)

    return paths