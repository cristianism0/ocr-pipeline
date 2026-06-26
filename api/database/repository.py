from sqlalchemy.orm import Session
from typing import Protocol
from api.database.models import Job, State
from api.database.session import DBSession


# Using protocol for scalability -> engine agnostic
class DBRepoTemplate(Protocol):
    def create_job(self, job_id: str, filename: str) -> None: ...
    def update_job(
        self,
        job_id: str,
        status: State,
        result: dict | None = None,
        error: str | None = None,
    ): ...
    def get_job(self, job_id: str) -> Job | None: ...
    def close(self) -> None: ...


class DBJobRepository:
    def __init__(self, db: Session | None = None):
        self._db = db or DBSession()
        self._owns_session = db is None

    def create_job(self, job_id: str, filename: str | None) -> None:
        job = Job(job_id=job_id, filename=filename, status=State.PENDING)
        self._db.add(job)
        self._db.commit()

    def update_job(
        self,
        job_id: str,
        status: State,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:
        job = self._db.get(Job, job_id)
        if job:
            job.status = status
            job.result = result
            job.error = error
            self._db.commit()

    def get_job(self, job_id: str) -> Job | None:
        return self._db.get(Job, job_id)

    def close(self) -> None:
        if self._owns_session:
            self._db.close()
