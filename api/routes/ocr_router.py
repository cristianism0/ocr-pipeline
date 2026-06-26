import uuid
import magic
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from api.database.session import get_db
from api.database.repository import DBJobRepository
from api.services.ocr_service import run_job
from api.database.session import Base, psql_engine
import api.database.models

router = APIRouter()

# for while - will change to MinIO in the future
INPUT_DIR = Path("api/data/input")
OUTPUT_DIR = Path("api/data/output")
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=psql_engine)

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
    db: Session = Depends(get_db),
) -> list[dict[str, str | None]]:

    repo = DBJobRepository(db)
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

        repo.create_job(job_id, f.filename)
        background_tasks.add_task(run_job, job_id, file_path, OUTPUT_DIR, repo)
        jobs.append({"job_id": job_id, "filename": f.filename})
    return jobs


@router.get("/jobs/{id}")
def job_status(id: str, db: Session = Depends(get_db)):
    repo = DBJobRepository(db)
    job = repo.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail=f"job not found with ID: {id}")
    return {"job_id": id, "status": job.status, "error": job.error}


@router.get("/jobs/{id}/result")
def get_result(id: str, db: Session = Depends(get_db)):
    repo = DBJobRepository(db)
    job = repo.get_job(id)

    if not job:
        raise HTTPException(status_code=404, detail=f"job not found with ID: {id}")
    if job.status.value != "done":
        raise HTTPException(status_code=202, detail="job still in progress")
    return {
        "job_id": id,
        "status": job.status,
        "error": job.error,
        "result": job.result,
    }
