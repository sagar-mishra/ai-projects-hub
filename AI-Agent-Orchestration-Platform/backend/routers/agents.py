from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from backend.database import get_session
from backend.models import Agent, Memory
from datetime import datetime
import json

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Pydantic schema for Agent creation
from pydantic import BaseModel

class AgentCreate(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: str
    model: str = "llama-3.1-8b-instant"
    tools_json: str = "[]"
    memory_enabled: bool = True
    channel: Optional[str] = None
    schedule_cron: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    max_iterations: int = 10
    guardrails_json: str = "{}"

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    tools_json: Optional[str] = None
    memory_enabled: Optional[bool] = None
    channel: Optional[str] = None
    schedule_cron: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    max_iterations: Optional[int] = None
    guardrails_json: Optional[str] = None

@router.get("", response_model=List[Agent])
def list_agents(session: Session = Depends(get_session)):
    return session.exec(select(Agent)).all()

@router.post("", response_model=Agent, status_code=status.HTTP_201_CREATED)
def create_agent(agent_data: AgentCreate, session: Session = Depends(get_session)):
    # Validate tools_json is valid JSON
    try:
        json.loads(agent_data.tools_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="tools_json must be a valid JSON array")
    
    # Validate guardrails_json is valid JSON
    try:
        json.loads(agent_data.guardrails_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="guardrails_json must be a valid JSON object")

    agent = Agent(**agent_data.dict())
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent

@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: str, session: Session = Depends(get_session)):
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=Agent)
def update_agent(agent_id: str, agent_data: AgentUpdate, session: Session = Depends(get_session)):
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    update_dict = agent_data.dict(exclude_unset=True)
    
    if "tools_json" in update_dict:
        try:
            json.loads(update_dict["tools_json"])
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="tools_json must be a valid JSON array")

    if "guardrails_json" in update_dict:
        try:
            json.loads(update_dict["guardrails_json"])
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="guardrails_json must be a valid JSON object")

    for key, value in update_dict.items():
        setattr(agent, key, value)
    
    agent.updated_at = datetime.utcnow()
    session.add(agent)
    session.commit()
    session.refresh(agent)
    
    # If schedule changed, we may need to reschedule. We handle it in main/scheduler
    # For now, we update it in the database.
    return agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, session: Session = Depends(get_session)):
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    # Also delete associated memories
    memories = session.exec(select(Memory).where(Memory.agent_id == agent_id)).all()
    for memory in memories:
        session.delete(memory)
        
    session.delete(agent)
    session.commit()
    return None

@router.get("/{agent_id}/memory")
def get_agent_memory(agent_id: str, session: Session = Depends(get_session)):
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    memories = session.exec(select(Memory).where(Memory.agent_id == agent_id)).all()
    return [{ "key": mem.key, "value": json.loads(mem.value_json), "updated_at": mem.updated_at } for mem in memories]

@router.delete("/{agent_id}/memory", status_code=status.HTTP_204_NO_CONTENT)
def clear_agent_memory(agent_id: str, session: Session = Depends(get_session)):
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    memories = session.exec(select(Memory).where(Memory.agent_id == agent_id)).all()
    for mem in memories:
        session.delete(mem)
    session.commit()
    return None
