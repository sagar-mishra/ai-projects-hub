import asyncio
from datetime import datetime
from sqlmodel import Session, select
import json
from typing import Dict, Any

import backend.database as db
from backend.models import Workflow, WorkflowRun, Agent, Message
from backend.runtime.graph_builder import build_graph
from backend.runtime.event_bus import event_bus
from langchain_core.messages import HumanMessage, AIMessage


# Helper to estimate cost and tokens
def estimate_metrics(run_messages: list):
    input_tokens = 0
    output_tokens = 0
    
    for msg in run_messages:
        # Try to extract actual metadata from LangChain responses
        metadata = getattr(msg, "response_metadata", {})
        token_usage = metadata.get("token_usage") or {}
        
        if token_usage:
            input_tokens += token_usage.get("prompt_tokens", 0)
            output_tokens += token_usage.get("completion_tokens", 0)
        else:
            # Fallback to character-based heuristic: ~4 chars per token
            token_count = len(msg.content) // 4
            if msg.type == "human" or msg.type == "system" or msg.type == "tool":
                input_tokens += token_count
            else:
                output_tokens += token_count

    total_tokens = input_tokens + output_tokens
    # Llama 3 8B Pricing: $0.05/1M input, $0.08/1M output
    cost = (input_tokens * 0.05 + output_tokens * 0.08) / 1000000.0
    return total_tokens, cost

async def execute_workflow(workflow_id: str, input_data: Dict[str, Any], run_id: str = None) -> str:
    """Asynchronously compile and run a visual workflow state machine."""
    
    # 1. Fetch Workflow from DB
    def _fetch_workflow():
        with Session(db.engine) as session:
            wf = session.get(Workflow, workflow_id)
            if not wf:
                return None, {}
            
            # Extract agent IDs from workflow nodes
            try:
                graph_json = json.loads(wf.graph_json)
            except Exception:
                graph_json = {}
                
            agent_ids = []
            for node in graph_json.get("nodes", []):
                if node.get("type") == "agent":
                    aid = node.get("agent_id") or node.get("data", {}).get("agent_id")
                    if aid:
                        agent_ids.append(aid)
            
            # Fetch all agents involved in this workflow
            agents = {}
            if agent_ids:
                statement = select(Agent).where(Agent.id.in_(agent_ids))
                for agent in session.exec(statement).all():
                    agents[agent.id] = agent
                    
            return wf, agents

    workflow, agents = await asyncio.to_thread(_fetch_workflow)
    if not workflow:
        raise ValueError(f"Workflow with ID {workflow_id} not found.")

    # 2. Initialize Run Record in DB
    def _init_run():
        with Session(db.engine) as session:
            nonlocal run_id
            if run_id:
                run = session.get(WorkflowRun, run_id)
                if run:
                    run.status = "running"
                    run.started_at = datetime.utcnow()
                    session.add(run)
                    session.commit()
                    return run.id
            
            run = WorkflowRun(
                id=run_id or None,
                workflow_id=workflow_id,
                status="running",
                input_json=json.dumps(input_data),
                output_json="{}",
                started_at=datetime.utcnow()
            )
            session.add(run)
            session.commit()
            session.refresh(run)
            return run.id

    run_id = await asyncio.to_thread(_init_run)

    await event_bus.publish(run_id, {
        "event_type": "info",
        "level": "info",
        "message": f"Starting workflow run '{run_id}' for workflow '{workflow.name}'."
    })

    try:
        # 3. Build Compiled LangGraph State
        compiled_graph = build_graph(json.loads(workflow.graph_json), agents)

        # 4. Prepare initial state
        initial_message = input_data.get("message", "")
        initial_messages = [HumanMessage(content=initial_message)] if initial_message else []

        state = {
            "messages": initial_messages,
            "last_output": "",
            "run_id": run_id,
            "approval_status": ""
        }

        # 5. Run the Graph
        result = await compiled_graph.ainvoke(state)
        
        # Extract messages from result state
        final_messages = result.get("messages", [])
        final_output = result.get("last_output", "")

        # Persist messages and calculate tokens/cost metrics
        total_tokens, run_cost = estimate_metrics(final_messages)

        # 6. Save final messages and update run record
        def _save_messages_and_complete():
            with Session(db.engine) as session:
                # Save inter-agent messages to messages table
                for msg in final_messages:
                    sender = "human" if msg.type == "human" else (msg.name if getattr(msg, "name", None) else "agent")
                    db_msg = Message(
                        run_id=run_id,
                        sender_agent=sender,
                        content=msg.content,
                        role=msg.type,
                        timestamp=datetime.utcnow()
                    )
                    session.add(db_msg)
                
                # Update WorkflowRun status
                run = session.get(WorkflowRun, run_id)
                if run:
                    run.status = "completed"
                    run.completed_at = datetime.utcnow()
                    run.output_json = json.dumps({"output": final_output})
                    run.token_count = total_tokens
                    run.cost_usd = run_cost
                    session.add(run)
                
                session.commit()

        await asyncio.to_thread(_save_messages_and_complete)

        await event_bus.publish(run_id, {
            "event_type": "run_completed",
            "level": "info",
            "message": f"Workflow run '{run_id}' completed successfully.",
            "output": final_output,
            "token_count": total_tokens,
            "cost_usd": run_cost
        })

        return final_output

    except Exception as e:
        error_msg = str(e)
        
        # Update database on run failure
        def _fail_run():
            with Session(db.engine) as session:
                run = session.get(WorkflowRun, run_id)
                if run:
                    run.status = "failed"
                    run.completed_at = datetime.utcnow()
                    run.error_message = error_msg
                    session.add(run)
                session.commit()

        await asyncio.to_thread(_fail_run)

        await event_bus.publish(run_id, {
            "event_type": "error",
            "level": "error",
            "message": f"Workflow run failed: {error_msg}"
        })
        
        # Publish final failure terminal event
        await event_bus.publish(run_id, {
            "event_type": "run_completed", # Terminate client listening
            "level": "error",
            "message": f"Workflow finished with failure."
        })

        raise e
