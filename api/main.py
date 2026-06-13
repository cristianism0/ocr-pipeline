import uuid
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI(title="OCR Pipeline", version="0.1")


@app.get("/")
async def main():
    content = """
    <body>
    <form action="/send" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>

    """
    return HTMLResponse(content=content)


@app.post("/send")
async def send_input(files: Annotated[list[UploadFile], File()]):
    job_id = str(uuid.uuid4())

    return {
        "filename": [f.filename for f in files],
        "job_id": job_id,
        "content_type": [f.content_type for f in files],
    }


async def send_batch_input(input: UploadFile):
    job_id = str(uuid.uuid4())
    return {
        "filename": input.filename,
        "job_id": job_id,
        "content_type": input.content_type,
    }
