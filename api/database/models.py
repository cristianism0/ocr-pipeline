from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, DateTime, String
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from .session import Base


class State(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class Job(Base):
    __tablename__: str = "jobs"
    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[State] = mapped_column(
        PgEnum(State, name="jobstatus"), default=State.PENDING
    )
    error: Mapped[str | None] = mapped_column(String, nullable=True)
    result: Mapped[str | None] = mapped_column(JSON, nullable=True)
    time: Mapped[datetime] = mapped_column(
        "created_at",  # time is reserved
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
