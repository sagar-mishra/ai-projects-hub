import pytest
import asyncio
from backend.runtime.event_bus import event_bus
from backend.runtime.tools.calculator import calculator
from backend.runtime.tools.http_request import http_request
from backend.runtime.tools import load_tools
from backend.runtime.graph_builder import build_graph, WorkflowState
from backend.models import Agent
import json

def test_calculator_tool():
    result = calculator("2 + 3 * 4")
    assert result == "14"
    
    result_invalid = calculator("invalid expression")
    assert "Error" in result_invalid

@pytest.mark.asyncio
async def test_event_bus(session):
    run_id = "test-run-123"

    q = event_bus.subscribe(run_id)
    
    test_event = {"event_type": "test_info", "message": "hello", "level": "info"}
    await event_bus.publish(run_id, test_event)
    
    received = await asyncio.wait_for(q.get(), timeout=1.0)
    assert received["event_type"] == "test_info"
    assert received["message"] == "hello"
    
    event_bus.unsubscribe(run_id, q)

def test_load_tools():
    tools = load_tools("[\"calculator\", \"web_search\"]")
    assert len(tools) == 2
    tool_names = [t.name for t in tools]
    assert "calculator" in tool_names
    assert "web_search" in tool_names

def test_build_graph():
    workflow_json = {
        "nodes": [
            { "id": "trigger", "type": "trigger" },
            { "id": "researcher", "type": "agent", "agent_id": "agent-uuid-1" },
            { "id": "end", "type": "end" }
        ],
        "edges": [
            { "from": "trigger", "to": "researcher" },
            { "from": "researcher", "to": "end" }
        ]
    }
    
    agent = Agent(
        id="agent-uuid-1",
        name="Researcher",
        system_prompt="You are a researcher",
        tools_json="[]"
    )
    
    agents_map = {"agent-uuid-1": agent}
    
    compiled = build_graph(workflow_json, agents_map)
    assert compiled is not None
    assert hasattr(compiled, "ainvoke")
