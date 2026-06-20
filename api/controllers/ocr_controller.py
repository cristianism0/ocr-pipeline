from enum import Enum


class State(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


_jobs = {}


def create_job(id: str) -> None:
    _jobs[id] = {"status": State.PENDING, "result": None, "error": None}


def update_job(id: str, status: State, result=None, error=None) -> None:
    _jobs[id]["status"] = status
    _jobs[id]["result"] = result
    _jobs[id]["error"] = error


def get_job(id: str) -> dict | None:
    return _jobs.get(id)
