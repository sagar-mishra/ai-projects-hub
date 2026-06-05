from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, desc
from typing import List, Optional
import json

from backend.database import get_session
from backend.models import WorkflowRun, Message, Log

router = APIRouter(prefix="/api/runs", tags=["runs"])

@router.get("")
def list_runs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    session: Session = Depends(get_session)
):
    offset = (page - 1) * limit
    statement = select(WorkflowRun).order_by(desc(WorkflowRun.started_at))
    
    if status_filter:
        statement = statement.where(WorkflowRun.status == status_filter)
        
    runs = session.exec(statement.offset(offset).limit(limit)).all()
    
    # We can also fetch the total count for pagination info
    total_statement = select(WorkflowRun)
    if status_filter:
        total_statement = total_statement.where(WorkflowRun.status == status_filter)
    total = len(session.exec(total_statement).all()) # Or select(func.count(WorkflowRun.id))
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "runs": runs
    }

@router.get("/{run_id}", response_model=WorkflowRun)
def get_run(run_id: str, session: Session = Depends(get_session)):
    run = session.get(WorkflowRun, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run

@router.get("/{run_id}/messages", response_model=List[Message])
def get_run_messages(run_id: str, session: Session = Depends(get_session)):
    # Verify run exists
    run = session.get(WorkflowRun, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
        
    statement = select(Message).where(Message.run_id == run_id).order_by(Message.timestamp)
    return session.exec(statement).all()

@router.get("/{run_id}/logs")
def get_run_logs(run_id: str, session: Session = Depends(get_session)):
    # Verify run exists
    run = session.get(WorkflowRun, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
        
    statement = select(Log).where(Log.run_id == run_id).order_by(Log.timestamp)
    logs = session.exec(statement).all()
    
    formatted_logs = []
    for log in logs:
        try:
            payload = json.loads(log.payload_json)
        except Exception:
            payload = {}
        formatted_logs.append({
            "id": log.id,
            "run_id": log.run_id,
            "agent_id": log.agent_id,
            "level": log.level,
            "event_type": log.event_type,
            "payload": payload,
            "timestamp": log.timestamp
        })
    return formatted_logs
