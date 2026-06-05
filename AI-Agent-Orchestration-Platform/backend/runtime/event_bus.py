import asyncio
from typing import Dict, List, Any
from sqlmodel import Session

from backend.models import Log
import json

class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, run_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subs.setdefault(run_id, []).append(q)
        return q

    def unsubscribe(self, run_id: str, q: asyncio.Queue):
        if run_id in self._subs:
            try:
                self._subs[run_id].remove(q)
                if not self._subs[run_id]:
                    del self._subs[run_id]
            except ValueError:
                pass

    async def publish(self, run_id: str, event: Dict[str, Any]):
        # Save event to SQLite database
        log_entry = Log(
            run_id=run_id,
            agent_id=event.get("agent_id"),
            level=event.get("level", "info"),
            event_type=event.get("event_type"),
            payload_json=json.dumps(event)
        )
        
        # Run SQLite sync DB write in a threadpool to prevent blocking the async loop
        def save_log():
            import backend.database as db
            with Session(db.engine) as session:
                session.add(log_entry)
                session.commit()

                
        await asyncio.to_thread(save_log)

        # Distribute to all websocket subscribers
        if run_id in self._subs:
            for q in list(self._subs[run_id]):
                await q.put(event)

event_bus = EventBus()
