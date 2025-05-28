from sqlmodel import create_engine, Session, select
from pathlib import Path
from models.project import Project, ProjectTask

_engine = create_engine(f"sqlite:///{Path(__file__).parents[1] / 'data' / 'tasks.db'}")

def init_db():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(_engine)

# ---------- Project helpers ----------
def create_project(pid, target, objective, score=0):
    with Session(_engine) as s:
        proj = Project(id=pid, target=target, objective=objective, score=score)
        s.add(proj); s.commit(); return proj

def list_projects():
    with Session(_engine) as s:
        return s.exec(select(Project)).all()

# ---------- Task helpers -------------
def add_task(title, project_id, status="backlog"):
    with Session(_engine) as s:
        t = ProjectTask(title=title, project_id=project_id, status=status)
        s.add(t); s.commit(); s.refresh(t); return t

def tasks_for_project(pid):
    with Session(_engine) as s:
        return s.exec(select(ProjectTask).where(ProjectTask.project_id == pid)).all()
