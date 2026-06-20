from fastapi import FastAPI

from api.routes.ocr_router import router

app = FastAPI(title="OCR Pipeline", version="0.1")

app.include_router(router)
