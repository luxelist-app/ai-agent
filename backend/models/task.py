from sqlmodel import SQLModel, Field
from typing import Optional
import datetime as dt

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gh_number: Optional[int] = None     # GitHub Issue #
    title: str
    status: str = "backlog"             # backlog | progress | done
    labels: str = ""                    # comma list
    estimate_days: int = 0
    created: dt.datetime = Field(default_factory=dt.datetime.utcnow)
