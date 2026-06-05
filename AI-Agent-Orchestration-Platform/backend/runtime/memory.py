import asyncio
from sqlmodel import Session, select
import backend.database as db
from backend.models import Memory
from datetime import datetime
import json
from langchain_core.messages import messages_from_dict, messages_to_dict

class AgentMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    async def load(self) -> list:
        """Load message history from the SQLite memory table for this agent."""
        def _load():
            with Session(db.engine) as session:
                statement = select(Memory).where(
                    Memory.agent_id == self.agent_id, 
                    Memory.key == "chat_history"
                )
                mem = session.exec(statement).first()
                if not mem:
                    return []
                try:
                    dicts = json.loads(mem.value_json)
                    return messages_from_dict(dicts)
                except Exception:
                    return []
        
        return await asyncio.to_thread(_load)

    async def save(self, messages: list):
        """Save message history to the SQLite memory table for this agent."""
        def _save():
            # Serialize LangChain messages to standard dicts
            dicts = messages_to_dict(messages)
            with Session(db.engine) as session:
                statement = select(Memory).where(
                    Memory.agent_id == self.agent_id, 
                    Memory.key == "chat_history"
                )
                mem = session.exec(statement).first()
                if not mem:
                    mem = Memory(
                        agent_id=self.agent_id,
                        key="chat_history",
                        value_json=json.dumps(dicts),
                        updated_at=datetime.utcnow()
                    )
                else:
                    mem.value_json = json.dumps(dicts)
                    mem.updated_at = datetime.utcnow()
                session.add(mem)
                session.commit()
                
        await asyncio.to_thread(_save)
