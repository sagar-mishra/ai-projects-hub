from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.database import get_session
from backend.models import Approval

router = APIRouter(prefix="/api/approvals", tags=["approvals"])

class ApprovalDecision(BaseModel):
    action: str  # "approve" | "reject"

@router.get("", response_model=List[Approval])
def list_approvals(
    status_filter: Optional[str] = "pending", 
    session: Session = Depends(get_session)
):
    statement = select(Approval)
    if status_filter:
        statement = statement.where(Approval.status == status_filter)
    return session.exec(statement).all()

@router.post("/{approval_id}/decide")
def decide_approval(
    approval_id: str, 
    decision: ApprovalDecision, 
    session: Session = Depends(get_session)
):
    approval = session.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
        
    if approval.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Approval request has already been decided: {approval.status}"
        )
        
    action = decision.action.lower()
    if action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Decision action must be 'approve' or 'reject'"
        )
        
    approval.status = "approved" if action == "approve" else "rejected"
    approval.decided_at = datetime.utcnow()
    
    session.add(approval)
    session.commit()
    session.refresh(approval)
    
    return {"status": approval.status, "decided_at": approval.decided_at}
