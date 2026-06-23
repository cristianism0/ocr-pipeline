import uuid
import json
import magic
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from api.controllers.ocr_controller import create_job, get_job
from api.services.ocr_service import run_job

router = APIRouter()
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/tiff",
    "image/tif",
    "image.gif",
    "image/webp",
    "image/jp2",
    "image/pnm",
    "image/pbm",
    "image/ppm",
    "image/pnm",
]


@router.post("/send")
async def send_input(
    files: Annotated[list[UploadFile], File()],
    background_tasks: BackgroundTasks,
) -> list[dict[str, str | None]]:

    jobs: list[dict[str, str | None]] = []

    for f in files:
        header = await f.read(2048)

        _ = await f.seek(0)

        magic_val = magic.from_buffer(header, mime=True)
        if f.content_type and magic_val not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"File {f.filename} type not allowed. Allowed: {', '.join(ALLOWED_TYPES)}",
            )

        job_id = str(uuid.uuid4())
        file_path = INPUT_DIR / f"{job_id}_{f.filename}"

        _ = file_path.write_bytes(await f.read())

        create_job(job_id)
        background_tasks.add_task(run_job, job_id, file_path, OUTPUT_DIR)
        jobs.append({"job_id": job_id, "filename": f.filename})
    return jobs


@router.get("/jobs/{id}")
def job_status(id: str):
    job = get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail=f"job not found with ID: {id}")
    return {"job_id": id, "status": job["status"], "error": job["error"]}


@router.get("/jobs/{id}/result")
def get_result(id: str) -> dict[str, str]:
    job = get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail=f"job not found with ID: {id}")
    if job["status"] != "done":
        raise HTTPException(status_code=202, detail="job still in progress")

    spath = Path(job["result"]).resolve()
    allowed = OUTPUT_DIR.resolve()

    if not spath.is_relative_to(allowed):
        raise HTTPException(status_code=403, detail="access denied")

    with open(spath, "r", encoding="utf8") as f:
        return {
            "job_id": id,
            "status": job["status"],
            "error": job["error"],
            "result": json.load(f),
        }
