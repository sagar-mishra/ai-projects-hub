from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import logging
import os
import json
import asyncio

from backend.config import settings
import backend.database as db
from backend.models import Workflow, Agent
from backend.routers import agents, workflows, runs, approvals, templates, logs
from backend.runtime.scheduler import scheduler, register_scheduled_agents
from backend.channels.telegram import register_webhook, handle_telegram_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

def seed_templates():
    """Seed the database with pre-built workflow templates on startup."""
    with Session(db.engine) as session:
        for key in ["research_pipeline", "support_triage"]:
            existing_template = session.exec(
                select(Workflow).where(Workflow.template_name == key, Workflow.is_template == True)
            ).first()
            
            if not existing_template:
                filename = f"{key}.json"
                filepath = os.path.join(TEMPLATES_DIR, filename)
                if not os.path.exists(filepath):
                    continue
                    
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    # 1. Seed template agents
                    agent_map = {}
                    for agent_data in data.get("agents", []):
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
                    
                    # 2. Build graph template
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
                    
                    # Save template workflow
                    template_wf = Workflow(
                        name=data.get("name"),
                        description=data.get("description"),
                        graph_json=json.dumps(graph_json),
                        is_template=True,
                        template_name=key
                    )
                    session.add(template_wf)
                    session.commit()
                    logger.info(f"Seeded template workflow: {data.get('name')}")
                except Exception as e:
                    logger.error(f"Error seeding template '{key}': {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    logger.info("Initializing SQLite database...")
    db.init_db()
    
    logger.info("Seeding workflow templates...")
    seed_templates()
    
    logger.info("Starting scheduler...")
    if not scheduler.running:
        try:
            scheduler.start()
        except Exception as e:
            logger.warning(f"Scheduler could not be started: {e}")
    await register_scheduled_agents()
    
    logger.info("Configuring Telegram bot webhook...")
    # Run async webhook registration
    asyncio.create_task(register_webhook())
    
    yield
    
    # Shutdown Events
    logger.info("Shutting down scheduler...")
    if scheduler.running:
        try:
            scheduler.shutdown(wait=False)
        except Exception as e:
            logger.warning(f"Scheduler could not be shut down: {e}")

app = FastAPI(
    title="AI Agent Orchestration Platform API",
    description="Backend API for building and monitoring multi-agent state machines.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(runs.router)
app.include_router(approvals.router)
app.include_router(templates.router)
app.include_router(logs.router)

# Health endpoint
@app.get("/health", tags=["system"])
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running" if scheduler.running else "stopped"
    }

# Telegram Webhook Endpoint
@app.post("/webhook/telegram", tags=["channels"])
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        update = await request.json()
        background_tasks.add_task(handle_telegram_update, update)
    except Exception as e:
        logger.error(f"Error processing Telegram webhook payload: {str(e)}")
    return {"status": "ok"}
