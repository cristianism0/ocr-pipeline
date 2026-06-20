FROM python:3.14-slim AS base
WORKDIR /app

RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

COPY src/ src/
COPY main.py .

FROM base AS cli
ENTRYPOINT ["python", "main.py"]


FROM base AS api
COPY requirements/api.txt .
RUN pip install --no-cache-dir -r api.txt
COPY api/ api
ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
