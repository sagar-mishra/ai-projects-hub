from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import json
import os

from backend.database import get_session
from backend.models import Workflow, Agent

router = APIRouter(prefix="/api/templates", tags=["templates"])

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

@router.get("")
def list_templates():
    """List all pre-built workflow templates available in the backend."""
    templates = []
    
    if not os.path.exists(TEMPLATES_DIR):
        return []
        
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                templates.append({
                    "key": filename.replace(".json", ""),
                    "name": data.get("name"),
                    "description": data.get("description")
                })
            except Exception:
                pass
    return templates

@router.post("/{template_key}/load", response_model=Workflow)
def load_template(template_key: str, session: Session = Depends(get_session)):
    """Instantiate a workflow from a template file, creating necessary agents and routing nodes."""
    filename = f"{template_key}.json"
    filepath = os.path.join(TEMPLATES_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"Template '{template_key}' not found.")
        
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")

    # 1. Create or retrieve agents defined in the template
    agent_map = {} # agent_name -> db agent_id
    
    for agent_data in data.get("agents", []):
        # Check if an agent with the same name already exists in the database
        db_agent = session.exec(select(Agent).where(Agent.name == agent_data.get("name"))).first()
        if not db_agent:
            db_agent = Agent(
                name=agent_data.get("name"),
                role=agent_data.get("role"),
                description=agent_data.get("description"),
                system_prompt=agent_data.get("system_prompt"),
                model=agent_data.get("model", "llama-3.1-8b-instant"),
                tools_json=agent_data.get("tools_json", "[]"),
                memory_enabled=agent_data.get("memory_enabled", True),
                temperature=agent_data.get("temperature", 0.7),
                max_tokens=agent_data.get("max_tokens", 1000),
                max_iterations=agent_data.get("max_iterations", 10)
            )
            session.add(db_agent)
            session.commit()
            session.refresh(db_agent)
            
        agent_map[agent_data.get("name")] = db_agent.id

    # 2. Assemble Graph JSON, injecting the correct database agent IDs
    graph_template = data.get("graph_json_template", {})
    nodes = []
    
    for node in graph_template.get("nodes", []):
        new_node = node.copy()
        if node.get("type") == "agent":
            agent_name = node.get("agent_name")
            if agent_name in agent_map:
                new_node["agent_id"] = agent_map[agent_name]
                del new_node["agent_name"]
        nodes.append(new_node)
        
    graph_json = {
        "nodes": nodes,
        "edges": graph_template.get("edges", [])
    }

    # 3. Create Workflow in DB
    wf = Workflow(
        name=data.get("name"),
        description=data.get("description"),
        graph_json=json.dumps(graph_json),
        is_template=False, # Loaded workflows are active instances
        template_name=data.get("name")
    )
    
    session.add(wf)
    session.commit()
    session.refresh(wf)
    
    return wf
