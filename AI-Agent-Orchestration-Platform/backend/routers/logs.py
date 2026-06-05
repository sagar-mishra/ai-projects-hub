from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
import asyncio
import json

import backend.database as db
from backend.runtime.event_bus import event_bus
from backend.models import Log

router = APIRouter(prefix="/api/ws", tags=["websockets"])

@router.websocket("/logs/{run_id}")
async def log_stream(websocket: WebSocket, run_id: str):
    """WebSocket endpoint to stream live execution logs for a workflow run."""
    await websocket.accept()
    
    # Send historical logs first (catch-up phase)
    def _fetch_history():
        with Session(db.engine) as session:
            statement = select(Log).where(Log.run_id == run_id).order_by(Log.timestamp)
            return session.exec(statement).all()
            
    historical_logs = await asyncio.to_thread(_fetch_history)
    for log in historical_logs:
        try:
            payload = json.loads(log.payload_json)
        except Exception:
            payload = {}
            
        await websocket.send_json({
            "id": log.id,
            "run_id": log.run_id,
            "agent_id": log.agent_id,
            "level": log.level,
            "event_type": log.event_type,
            "payload": payload,
            "timestamp": log.timestamp.isoformat()
        })

    # Subscribe to live updates
    queue = event_bus.subscribe(run_id)
    try:
        while True:
            event = await asyncio.wait_for(queue.get(), timeout=30.0)
            
            # Format payload for unified structure if it's not a dict
            if not isinstance(event.get("payload"), dict):
                # Ensure the broadcast is formatted like the database schema
                ws_payload = {
                    "event_type": event.get("event_type"),
                    "level": event.get("level", "info"),
                    "message": event.get("message"),
                    **{k: v for k, v in event.items() if k not in ["event_type", "level", "message"]}
                }
            else:
                ws_payload = event.get("payload")

            await websocket.send_json({
                "run_id": run_id,
                "agent_id": event.get("agent_id"),
                "level": event.get("level", "info"),
                "event_type": event.get("event_type"),
                "payload": ws_payload,
                "timestamp": datetime.utcnow().isoformat() if "timestamp" not in event else event["timestamp"]
            })
            
            # Close the socket when run completes
            if event.get("event_type") == "run_completed":
                break
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        event_bus.unsubscribe(run_id, queue)

# We must import datetime for timestamp fallback
from datetime import datetime
