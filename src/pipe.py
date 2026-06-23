import csv
import io
import logging
from pathlib import Path
from typing import TypedDict

import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"


class WordConf(TypedDict):
    confidence: float
    text: str


def page_conf_text(
    file_path: Path, min_word_conf: float = 60.00
) -> tuple[list[WordConf], list[WordConf]]:
    """
    Collect the text and word's confidence and return.
    """

    data = pytesseract.image_to_data(Image.open(file_path))
    reader = csv.DictReader(io.StringIO(data.replace("\t", ",").strip()))

    ret: list[WordConf] = []
    word_conf: list[WordConf] = []
    for line in reader:
        confidence = line.get("conf")
        text = line.get("text")

        # already filter -1 conf (no text)
        if confidence and text:
            ret.append({"confidence": float(confidence), "text": text})
            if float(confidence) <= min_word_conf:
                word_conf.append({"confidence": float(confidence), "text": text})
    logger.info(f"text and confidence collected succesfully for {file_path.name}")
    return ret, word_conf


def page_text(file_path: Path):
    """
    Get the text from a image using Tesseract.
    """
    data: str | bytes | dict[str, str | bytes] = pytesseract.image_to_string(
        Image.open(file_path)
    )
    return data


def mean_conf(values: list[float]) -> float | np.floating:
    """
    Calculate the mean value using Numpy.mean() method.
    """
    if not values:
        return 0.0
    # use np instead of manual mean because np has NaN fallback - nonstop pipe
    return np.mean(values)
