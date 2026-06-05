from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
import json
import uuid
from datetime import datetime

from backend.database import get_session
from backend.models import Workflow, WorkflowRun
from backend.runtime.executor import execute_workflow

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

from pydantic import BaseModel

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    graph_json: str
    is_template: bool = False
    template_name: Optional[str] = None

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graph_json: Optional[str] = None
    is_template: Optional[bool] = None
    template_name: Optional[str] = None

class RunInput(BaseModel):
    message: str

@router.get("", response_model=List[Workflow])
def list_workflows(session: Session = Depends(get_session)):
    return session.exec(select(Workflow)).all()

@router.post("", response_model=Workflow, status_code=status.HTTP_201_CREATED)
def create_workflow(wf_data: WorkflowCreate, session: Session = Depends(get_session)):
    # Validate graph_json is valid JSON
    try:
        json.loads(wf_data.graph_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="graph_json must be valid JSON")

    wf = Workflow(**wf_data.dict())
    session.add(wf)
    session.commit()
    session.refresh(wf)
    return wf

@router.get("/{wf_id}", response_model=Workflow)
def get_workflow(wf_id: str, session: Session = Depends(get_session)):
    wf = session.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return wf

@router.put("/{wf_id}", response_model=Workflow)
def update_workflow(wf_id: str, wf_data: WorkflowUpdate, session: Session = Depends(get_session)):
    wf = session.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    update_dict = wf_data.dict(exclude_unset=True)
    if "graph_json" in update_dict:
        try:
            json.loads(update_dict["graph_json"])
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="graph_json must be valid JSON")

    for key, value in update_dict.items():
        setattr(wf, key, value)
        
    wf.version += 1
    wf.updated_at = datetime.utcnow()
    
    session.add(wf)
    session.commit()
    session.refresh(wf)
    return wf

@router.delete("/{wf_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(wf_id: str, session: Session = Depends(get_session)):
    wf = session.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    session.delete(wf)
    session.commit()
    return None

@router.post("/{wf_id}/run", status_code=status.HTTP_202_ACCEPTED)
def run_workflow(
    wf_id: str, 
    run_input: RunInput, 
    background_tasks: BackgroundTasks, 
    session: Session = Depends(get_session)
):
    wf = session.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    # Generate run_id beforehand
    run_id = str(uuid.uuid4())
    
    # Create workflow run in pending state
    run = WorkflowRun(
        id=run_id,
        workflow_id=wf_id,
        status="pending",
        input_json=json.dumps({"message": run_input.message}),
        started_at=datetime.utcnow()
    )
    session.add(run)
    session.commit()
    
    # Start execution in background task
    background_tasks.add_task(
        execute_workflow,
        workflow_id=wf_id,
        input_data={"message": run_input.message},
        run_id=run_id
    )
    
    return {"run_id": run_id, "status": "pending"}
