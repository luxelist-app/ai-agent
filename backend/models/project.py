from typing import Optional
import datetime as dt
from sqlmodel import SQLModel, Field

class Project(SQLModel, table=True):
    id: str = Field(primary_key=True)          # e.g. 8-char UUID
    target: str                                # url / path / repo
    objective: str                             # release / audit / …
    score: int = 0                             # aggregate score (0-100)
    created: dt.datetime = Field(default_factory=dt.datetime.utcnow)

class ProjectTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: str                            # FK to Project.id
    title: str
    status: str = "backlog"                    # backlog | progress | done
    created: dt.datetime = Field(default_factory=dt.datetime.utcnow)
