import pytesseract
from PIL import Image
import csv
import io
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"
    
def page_conf_text(file_path: str, min_word_conf: float = 60.00) -> tuple[list[dict[float,str]], list[dict[float,str]]]:
    data = pytesseract.image_to_data(Image.open(file_path))
    reader = csv.DictReader(io.StringIO(data.replace('\t', ',').strip()))

    ret = []
    word_conf = []
    for line in reader:
        confidence = line.get('conf')
        text = line.get('text')
    
        # already filter -1 conf (no text)
        if confidence and text:
            ret.append({"confidence": float(confidence), "text": text})
            if float(confidence) <= min_word_conf:
                word_conf.append({"confidence": float(confidence), "text": text})
                
    return ret, word_conf
    
def page_text(file_path: str):
    """
    Get the text from a image using Tesseract.
    """    
    data = pytesseract.image_to_string(Image.open(file_path))
    return data

def mean_conf(values: list):
    """
    Calculate the mean value using Numpy.mean() method.
    """
    if not values:
        return 0.0
    # use np instead of manual mean because np has NaN fallback - nonstop pipe
    return np.mean(values)

