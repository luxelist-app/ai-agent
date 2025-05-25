from sqlmodel import create_engine, Session, select
from backend.models.task import Task
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tasks.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def init_db():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

def add_task(**kwargs) -> Task:
    with Session(engine) as s:
        t = Task(**kwargs)
        s.add(t); s.commit(); s.refresh(t); return t

def all_tasks():
    with Session(engine) as s:
        return s.exec(select(Task)).all()

def sync_from_github(issues):
    """Upsert GitHub issues into DB."""
    with Session(engine) as s:
        for iss in issues:
            t = s.exec(select(Task).where(Task.gh_number == iss["number"])).first()
            if not t:
                t = Task(
                    gh_number=iss["number"],
                    title=iss["title"],
                    status="done" if iss["state"] == "closed" else "backlog",
                    labels=",".join([l["name"] for l in iss["labels"]]),
                )
                s.add(t)
        s.commit()
