import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from api.database.models import State
from api.database.repository import DBRepoTemplate
from src.output import json_from_image, json_from_pdf
from src.pipe import mean_conf, page_conf_text, page_text
from src.utils import dispatcher

DISPATCH_PATH = Path("api/data/dispatch")
DISPATCH_PATH.mkdir(parents=True, exist_ok=True)


def _run_pipeline(job_id: str, file_path: Path, output_path: Path) -> dict:
    img_p, suffix = dispatcher(file=file_path, dispatch_dir=DISPATCH_PATH)
    if suffix == ".pdf":
        pdf_content = []
        for i, page in enumerate(img_p):
            conf, low_words = page_conf_text(file_path=page)
            conf_values = [item["confidence"] for item in conf]
            mean = mean_conf(conf_values)
            text = page_text(page)
            pdf_content.append(
                {
                    "page": i,
                    "text": text,
                    "mean_page": mean,
                    "low_words": low_words,
                }
            )
        json_p = json_from_pdf(
            file_path=file_path,
            output_path=output_path,
            pages=pdf_content,
        )
    else:
        conf, low_words = page_conf_text(file_path=file_path)
        conf_values = [item["confidence"] for item in conf]
        mean = mean_conf(conf_values)
        text = page_text(file_path)
        json_p = json_from_image(
            file_path=file_path,
            output_path=output_path,
            text=text,
            mean_confidence=mean,
            low_confidence_words=low_words,
        )
    return json.loads(json_p.read_text())


async def run_job(
    job_id: str,
    file_path: Path,
    output_path: Path,
    repo: DBRepoTemplate,
    executor: ProcessPoolExecutor,
):
    repo.update_job(job_id, State.RUNNING)
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            executor, _run_pipeline, job_id, file_path, output_path
        )
        repo.update_job(job_id, State.DONE, result=result)
    except Exception as e:
        repo.update_job(job_id, State.ERROR, error=str(e))
    finally:
        repo.close()
