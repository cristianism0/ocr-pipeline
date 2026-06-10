from PIL import Image, ImageDraw

from src.pipe import mean_conf, page_conf_text, page_text


def make_image(tmp_path, text="hello world"):
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), text, fill=(0, 0, 0))
    path = tmp_path / "sample.png"
    img.save(path)
    return path


def test_page_conf_text_returns_tuple(tmp_path):
    img = make_image(tmp_path)
    result = page_conf_text(img)
    assert isinstance(result, tuple) and len(result) == 2


def test_page_conf_text_words_have_keys(tmp_path):
    img = make_image(tmp_path)
    ret, _ = page_conf_text(img)
    for item in ret:
        assert "confidence" in item and "text" in item


def test_page_conf_text_no_negative_confidence(tmp_path):
    img = make_image(tmp_path)
    ret, _ = page_conf_text(img)
    for item in ret:
        assert item["confidence"] >= 0


def test_page_conf_text_low_words_below_threshold(tmp_path):
    img = make_image(tmp_path)
    _, word_conf = page_conf_text(img, min_word_conf=60.0)
    for item in word_conf:
        assert item["confidence"] <= 60.0


def test_page_conf_text_blank_image(tmp_path):
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    path = tmp_path / "blank.png"
    img.save(path)
    ret, word_conf = page_conf_text(path)
    assert ret == [] and word_conf == []


def test_page_text_returns_string(tmp_path):
    img = make_image(tmp_path)
    result = page_text(img)
    assert isinstance(result, str)


def test_mean_conf_normal():
    result = mean_conf([80.0, 90.0, 70.0])
    assert result == 80.0


def test_mean_conf_empty():
    assert mean_conf([]) == 0.0


def test_mean_conf_single():
    assert mean_conf([75.0]) == 75.0


def test_mean_conf_all_same():
    assert mean_conf([60.0, 60.0, 60.0]) == 60.0
