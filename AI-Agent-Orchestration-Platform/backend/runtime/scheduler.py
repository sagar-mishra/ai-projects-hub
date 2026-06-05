from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
import json
import logging
import asyncio

import backend.database as db
from backend.models import Agent, Workflow
from backend.runtime.executor import execute_workflow

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def execute_scheduled_agent(agent_id: str):
    """Worker task executed when agent cron triggers."""
    def _find_workflow():
        with Session(db.engine) as session:
            workflows = session.exec(select(Workflow)).all()
            for wf in workflows:
                try:
                    graph = json.loads(wf.graph_json)
                    for node in graph.get("nodes", []):
                        if node.get("type") == "agent" and node.get("agent_id") == agent_id:
                            return wf
                except Exception:
                    pass
            return None

    workflow = await asyncio.to_thread(_find_workflow)
    if not workflow:
        logger.warning(f"Scheduled trigger fired for agent '{agent_id}', but no active workflow contains this agent.")
        return
        
    try:
        logger.info(f"Executing scheduled workflow '{workflow.name}' for agent ID '{agent_id}'.")
        await execute_workflow(workflow.id, {"message": "Scheduled trigger activation."})
    except Exception as e:
        logger.error(f"Error running scheduled workflow '{workflow.id}': {str(e)}")

async def register_scheduled_agents():
    """Locate all agents with active cron definitions and register jobs in APScheduler."""
    # Clear out old jobs to prevent duplications
    for job in list(scheduler.get_jobs()):
        scheduler.remove_job(job.id)

    def _get_agents_with_cron():
        with Session(db.engine) as session:
            statement = select(Agent).where(Agent.schedule_cron != None)
            return session.exec(statement).all()
            
    agents = await asyncio.to_thread(_get_agents_with_cron)
    for agent in agents:
        cron_str = agent.schedule_cron.strip() if agent.schedule_cron else ""
        if not cron_str:
            continue
        try:
            scheduler.add_job(
                func=execute_scheduled_agent,
                trigger=CronTrigger.from_crontab(cron_str),
                args=[agent.id],
                id=f"agent_{agent.id}",
                replace_existing=True
            )
            logger.info(f"Successfully scheduled agent '{agent.name}' with cron: {cron_str}")
        except Exception as e:
            logger.error(f"Failed to compile cron expression '{cron_str}' for agent '{agent.name}': {str(e)}")
