FROM python:3.14-slim
WORKDIR /app

RUN apt-get update \
    && apt-get install -y tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY main.py .

ENTRYPOINT ["python", "main.py"]