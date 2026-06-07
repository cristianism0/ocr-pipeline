# OCR Pipeline

A pipeline that extracts text from PDFs and images using Tesseract OCR, returning structured JSON output with confidence metrics per word and page.

## What it does

Accepts a directory of PDFs or images, runs OCR via pyTesseract, and produces one JSON file per document with extracted text and confidence metrics.

```
input/
├── document.pdf
└── scan.jpeg
└── plaintext.txt

output/
├── document.json
└── scan.json
└── plaintext.json
└── pipeline.log
```

## Pipeline
```
                                          ┌-> IMG            -> tesseract ┐
directory -> path_collector -> dispatcher                                JSON
                                          └-> PDF -> pdf2img -> tesseract ┘
```

1. **path_collector** — walks the input directory (recursively or not).
2. **dispatcher** — routes each file: PDF goes through `pdf2img`, images go
   directly to OCR.
3. **pdf2img** — converts each PDF page to an image via `pymupdf`.
4. **tesseract** — runs OCR via `pytesseract`, returning text and per-word
   confidence.
5. **output** — structures results and writes JSON to the output directory.

## JSON output structure

**PDF:**
```json
{
  "filename": "document.pdf",
  "pages": [
    {
      "page": 0,
      "text": "extracted text here",
      "mean_confidence": 87.3,
      "low_confidence_words": [
        {"confidence": 42.0, "text": "obscvro"}
      ]
    }
  ]
}
```

**Image:**
```json
{
  "filename": "scan.jpeg",
  "text": "extracted text here",
  "mean_confidence": 91.2,
  "low_confidence_words": []
}
```

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (*optional*)
- Tesseract — install via package manager:

```bash
# Debian/Ubuntu
sudo apt install tesseract-ocr

# Arch
sudo pacman -S tesseract-ocr 

# macOS
brew install tesseract
```

## Installation

```bash
git clone https://github.com/cristianism0/ocr-pipeline
cd ocr-pipeline

# for uv
uv sync

# for python
pip install requirements.txt
```

## Usage
Using `uv`: 
```bash
uv run main.py -d <input_directory> [options]
```

Using `python`:
```bash
python main.py -d <input_directory> [options]
```

| Argument | Description | Default |
|---|---|---|
| `-d`, `--directory` | Input directory (required) | — |
| `-o`, `--output` | Output directory for JSON files | `data/output` |
| `--dispatch` | Directory for PDF page images | `data/dispatch` |
| `-r`, `--recursive` | Scan subdirectories recursively | `False` |
| `--ext` | Image format for PDF conversion | `jpeg` |
| `-p`, `--precision` | Confidence threshold for low-confidence words | `60.0` |
| `-w`, `--workers` | Number of cores for multiprocessing | `4` |
| `--ascii` | Write JSON with ASCII encoding | `False` |


Use `-h` or `--help` flag to help.


**Examples:**

```bash
# single directory
uv run main.py -d data/input

# recursive, custom output, png conversion
uv run main.py -d documents/ -o results/ -r --ext png

# lower confidence threshold
uv run main.py -d data/input -p 75.0
```

## Project structure

```
.
├── src/
│   ├── pipe.py       # OCR functions: text extraction and confidence
│   ├── utils.py      # I/O handlers: path collection, dispatch, pdf2img
│   └── output.py     # JSON construction and writing
├── data/
│   ├── input/        # place input files here (gitignored)
│   ├── dispatch/     # intermediate PDF page images (gitignored)
│   └── output/       # JSON results (gitignored)
├── tests/
│   ├── fixtures/
│   ├── test_pipe.py
│   ├── test_utils.py
│   └── test_output.py
├── main.py
├── pyproject.toml
├── .python-version
├── requirements.txt  # for python setup
└── uv.lock
```

## Running tests

```bash
# all tests
uv run pytest tests/ -v

# with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing
```

Current coverage: **100%** across all modules.

## Architecture decisions

**Procedural over object-oriented**
The pipeline is a linear data transformation — each step receives input and
returns output with no shared state.

**One JSON per document, not per page**
PDFs are aggregated into a single JSON file with a `pages` array. Processing
pages as individual files would scatter the output and make downstream
consumption harder.

**Separate dispatch directory**
PDF-converted images are written to `data/dispatch/`, not to the input
directory. This prevents `path_collector` from picking up intermediate files
on the next run.

**`--precision` as a CLI argument**
The confidence threshold for flagging low-confidence words defaults to `60.0`
but is exposed via CLI. Documents from different periods and digitization
quality require different thresholds.


## Known limitations

- **Manuscripts and HTR** — Tesseract was not trained for handwritten text recognition. For HTR, see [Kraken](https://kraken.re) or [Calamari](https://github.com/Calamari-OCR/calamari).
- **Low DPI scans** — images below 200 DPI produce consistently low confidence. Rescan at 300 DPI minimum for better results.
- **18th and 19th century documents** — mean confidence below 60 is common due to ink degradation and non-standard typefaces.
- **Multi-column layouts** — Tesseract reads left-to-right across the full page width, mixing columns. Layout analysis is not implemented.
- **Native digital PDFs** — PDFs with a text layer do not need OCR. The pipeline converts them to images anyway; confidence will be high but the step is unnecessary.

## What's next

- [x] Multiprocessing with `ProcessPoolExecutor` and process-safe logging
  via `QueueHandler`
- [ ] Containerization and Makefile integration.
