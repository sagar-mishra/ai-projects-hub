from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

class Agent(SQLModel, table=True):
    __tablename__ = "agents"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: str
    model: str = "llama-3.1-8b-instant"
    tools_json: str = "[]"  # JSON array of enabled tool names
    memory_enabled: bool = True
    channel: Optional[str] = None  # "telegram" | None
    schedule_cron: Optional[str] = None  # cron string | None
    max_tokens: int = 1000
    temperature: float = 0.7
    max_iterations: int = 10
    guardrails_json: str = "{}"  # JSON: {forbidden_topics: []}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Workflow(SQLModel, table=True):
    __tablename__ = "workflows"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    graph_json: str  # nodes[], edges[]
    version: int = 1
    is_template: bool = False
    template_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowRun(SQLModel, table=True):
    __tablename__ = "workflow_runs"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    workflow_id: str = Field(foreign_key="workflows.id")
    status: str = "pending"  # pending|running|waiting_approval|completed|failed
    input_json: Optional[str] = "{}"
    output_json: Optional[str] = "{}"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    token_count: int = 0
    cost_usd: float = 0.0
    error_message: Optional[str] = None

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    run_id: str = Field(foreign_key="workflow_runs.id")
    sender_agent: str  # agent name | "human" | "telegram"
    receiver_agent: Optional[str] = None
    content: str
    role: str  # user | assistant | tool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Log(SQLModel, table=True):
    __tablename__ = "logs"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    run_id: str = Field(foreign_key="workflow_runs.id")
    agent_id: Optional[str] = None
    level: str = "info"  # info | warning | error
    event_type: str  # llm_call|tool_call|tool_result|agent_message|error|approval_requested
    payload_json: Optional[str] = "{}"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Memory(SQLModel, table=True):
    __tablename__ = "memory"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    agent_id: str = Field(foreign_key="agents.id")
    key: str
    value_json: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    agent_id: str = Field(foreign_key="agents.id")
    channel: str = "telegram"
    user_id: str  # telegram chat_id
    user_message: str
    agent_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Approval(SQLModel, table=True):
    __tablename__ = "approvals"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    run_id: str = Field(foreign_key="workflow_runs.id")
    node_id: str
    question: str
    status: str = "pending"  # pending | approved | rejected
    decided_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
