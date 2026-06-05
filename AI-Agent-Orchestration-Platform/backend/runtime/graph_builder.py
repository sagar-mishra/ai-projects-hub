from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Annotated, List, Dict, Any
import operator
import json
import asyncio
from datetime import datetime

from backend.runtime.llm import get_llm
from backend.runtime.tools import load_tools
from backend.runtime.memory import AgentMemory
from backend.runtime.event_bus import event_bus
from backend.models import Agent
from backend.config import settings

# Define the State of the graph
class WorkflowState(TypedDict):
    messages: Annotated[List[Any], operator.add]
    last_output: str
    run_id: str
    approval_status: str

def make_agent_node(agent_cfg: Agent):
    llm = get_llm(
        model_name=agent_cfg.model, 
        temperature=agent_cfg.temperature, 
        max_tokens=agent_cfg.max_tokens
    )
    tools = load_tools(agent_cfg.tools_json)
    
    if agent_cfg.memory_enabled:
        from langchain_core.tools import StructuredTool
        from sqlmodel import Session, select
        import backend.database as db
        from backend.models import Memory
        from datetime import datetime
        
        async def save_fact(key: str, value: str) -> str:
            """Save a key-value fact to the agent's long-term memory. Use this to remember important details (like user preferences, facts, configurations, previous findings) across workflow runs."""
            def _save():
                with Session(db.engine) as session:
                    statement = select(Memory).where(
                        Memory.agent_id == agent_cfg.id,
                        Memory.key == f"lt_{key}"
                    )
                    mem = session.exec(statement).first()
                    if not mem:
                        mem = Memory(
                            agent_id=agent_cfg.id,
                            key=f"lt_{key}",
                            value_json=json.dumps(value),
                            updated_at=datetime.utcnow()
                        )
                    else:
                        mem.value_json = json.dumps(value)
                        mem.updated_at = datetime.utcnow()
                    session.add(mem)
                    session.commit()
            await asyncio.to_thread(_save)
            return f"Successfully saved fact '{key}' = '{value}' to long-term memory."

        async def recall_fact(key: str) -> str:
            """Recall a key-value fact from the agent's long-term memory."""
            def _recall():
                with Session(db.engine) as session:
                    statement = select(Memory).where(
                        Memory.agent_id == agent_cfg.id,
                        Memory.key == f"lt_{key}"
                    )
                    mem = session.exec(statement).first()
                    if not mem:
                        return f"No fact found for key '{key}' in long-term memory."
                    try:
                        return json.loads(mem.value_json)
                    except Exception:
                        return mem.value_json
            val = await asyncio.to_thread(_recall)
            return f"Fact '{key}': {val}"

        tools.append(StructuredTool.from_function(
            coroutine=save_fact,
            name="save_fact",
            description="Save a key-value fact to the agent's long-term memory. Use this to remember important details (like user preferences, facts, configurations, previous findings) across workflow runs."
        ))
        tools.append(StructuredTool.from_function(
            coroutine=recall_fact,
            name="recall_fact",
            description="Recall a key-value fact from the agent's long-term memory."
        ))

    memory = AgentMemory(agent_cfg.id)

    async def node_fn(state: WorkflowState):
        run_id = state["run_id"]
        
        # Load agent history from DB if memory is enabled
        history = []
        if agent_cfg.memory_enabled:
            history = await memory.load()

        # Build prompt using state modifier or system prompt
        system_prompt = agent_cfg.system_prompt
        
        # Append strict instructions to prevent hallucinated tool calls (e.g. ask_user, human_input)
        system_prompt += (
            "\n\nCRITICAL: You are only allowed to invoke the specific tools that are explicitly provided to you in your toolbelt. "
            "Never attempt to invoke tools that are not in your list (such as 'ask_user', 'human_input', 'ask_human', or any others). "
            "If you need to ask the user for more information or follow-up questions, ask them directly by writing your response as plain text; "
            "DO NOT attempt to call any tool or function to communicate with the user."
        )
        
        # Create React Agent
        agent = create_react_agent(llm, tools, prompt=system_prompt)
        
        await event_bus.publish(run_id, {
            "event_type": "llm_call",
            "agent_id": agent_cfg.id,
            "agent_name": agent_cfg.name,
            "level": "info",
            "message": f"Agent {agent_cfg.name} (Role: {agent_cfg.role}) is starting execution."
        })

        # Calculate recursion limit based on max_iterations
        # 1 iteration = 1 LLM call + 1 tool call. Recursion limit is total graph steps, usually 2 * iterations + 2
        config = {"recursion_limit": max(2, agent_cfg.max_iterations * 2)}
        
        # Filter out raw tool messages and intermediate AI messages with tool calls to save tokens
        clean_history = []
        for msg in history:
            m_type = getattr(msg, "type", None)
            tool_calls = getattr(msg, "tool_calls", None)
            if m_type is None and isinstance(msg, dict):
                m_type = msg.get("type")
                tool_calls = msg.get("tool_calls")
            if m_type == "tool":
                continue
            if m_type == "ai" and tool_calls:
                continue
            clean_history.append(msg)

        clean_state_messages = []
        for msg in state["messages"]:
            m_type = getattr(msg, "type", None)
            tool_calls = getattr(msg, "tool_calls", None)
            if m_type is None and isinstance(msg, dict):
                m_type = msg.get("type")
                tool_calls = msg.get("tool_calls")
            if m_type == "tool":
                continue
            if m_type == "ai" and tool_calls:
                continue
            clean_state_messages.append(msg)

        input_messages = clean_history + clean_state_messages
        
        # Execute agent with a configured timeout limit
        try:
            result = await asyncio.wait_for(
                agent.ainvoke({"messages": input_messages}, config=config),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            error_msg = f"Agent {agent_cfg.name} execution timed out after {settings.AGENT_TIMEOUT_SECONDS} seconds."
            await event_bus.publish(run_id, {
                "event_type": "error",
                "agent_id": agent_cfg.id,
                "agent_name": agent_cfg.name,
                "level": "error",
                "message": error_msg
            })
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Agent {agent_cfg.name} encountered an error: {str(e)}"
            await event_bus.publish(run_id, {
                "event_type": "error",
                "agent_id": agent_cfg.id,
                "agent_name": agent_cfg.name,
                "level": "error",
                "message": error_msg
            })
            raise e

        # Extract output and log new messages generated during this step
        output = result["messages"][-1].content
        
        # Publish inter-agent messages and tool calls to event bus
        input_len = len(input_messages)
        new_msgs = result["messages"][input_len:]
        
        for msg in new_msgs:
            if msg.type == "ai" and getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    await event_bus.publish(run_id, {
                        "event_type": "tool_call",
                        "agent_id": agent_cfg.id,
                        "agent_name": agent_cfg.name,
                        "level": "info",
                        "tool_name": tc.get("name"),
                        "tool_input": tc.get("args"),
                        "message": f"Agent {agent_cfg.name} is executing tool '{tc.get('name')}' with input: {tc.get('args')}"
                    })
            elif msg.type == "tool":
                await event_bus.publish(run_id, {
                    "event_type": "tool_result",
                    "agent_id": agent_cfg.id,
                    "agent_name": agent_cfg.name,
                    "level": "info",
                    "tool_name": msg.name,
                    "tool_output": msg.content,
                    "message": f"Tool '{msg.name}' completed execution."
                })

        # Broadcast the final agent message
        await event_bus.publish(run_id, {
            "event_type": "agent_message",
            "agent_id": agent_cfg.id,
            "agent_name": agent_cfg.name,
            "level": "info",
            "content": output,
            "message": f"Agent {agent_cfg.name}: {output}"
        })

        # Save history if memory is enabled
        if agent_cfg.memory_enabled:
            # Save the new AI and tool messages generated in this run to memory
            await memory.save(result["messages"])

        # Return only the new messages to be appended to state
        return {
            "messages": new_msgs, 
            "last_output": output
        }

    return node_fn

def make_condition_node(node_id: str):
    async def condition_fn(state: WorkflowState):
        # Pass-through node, routing occurs dynamically on edges
        return {"messages": []}
    return condition_fn

def make_approval_node(node_id: str, question: str):
    from sqlmodel import Session, select
    import backend.database as db
    from backend.models import Approval, WorkflowRun

    async def approval_fn(state: WorkflowState):
        run_id = state["run_id"]
        
        # Create approval request in DB
        def _create():
            with Session(db.engine) as session:
                appr = Approval(
                    run_id=run_id,
                    node_id=node_id,
                    question=question,
                    status="pending"
                )
                session.add(appr)
                
                # Update run status to waiting_approval
                run = session.get(WorkflowRun, run_id)
                if run:
                    run.status = "waiting_approval"
                    session.add(run)
                
                session.commit()
                return appr.id

        approval_id = await asyncio.to_thread(_create)

        await event_bus.publish(run_id, {
            "event_type": "approval_requested",
            "level": "warning",
            "approval_id": approval_id,
            "question": question,
            "message": f"Approval required at node '{node_id}': {question}"
        })

        # Poll DB for decision (timeout after 5 minutes / 300 seconds)
        for _ in range(300):
            await asyncio.sleep(1)
            
            def _check():
                with Session(db.engine) as session:
                    appr = session.get(Approval, approval_id)
                    return appr.status if appr else "pending"
                    
            status = await asyncio.to_thread(_check)
            if status != "pending":
                # Decision was made (approved | rejected)
                # Update status back to running
                def _resume():
                    with Session(db.engine) as session:
                        run = session.get(WorkflowRun, run_id)
                        if run:
                            run.status = "running"
                            session.add(run)
                            session.commit()
                await asyncio.to_thread(_resume)
                
                await event_bus.publish(run_id, {
                    "event_type": "info",
                    "level": "info",
                    "message": f"Approval decision received for node '{node_id}': {status.upper()}"
                })
                return {"approval_status": status}

        # Auto-reject on timeout
        def _timeout():
            with Session(db.engine) as session:
                appr = session.get(Approval, approval_id)
                if appr:
                    appr.status = "rejected"
                    session.add(appr)
                run = session.get(WorkflowRun, run_id)
                if run:
                    run.status = "running"
                    session.add(run)
                session.commit()
        await asyncio.to_thread(_timeout)
        
        await event_bus.publish(run_id, {
            "event_type": "info",
            "level": "warning",
            "message": f"Approval request at node '{node_id}' timed out. Auto-rejecting."
        })
        return {"approval_status": "rejected"}

    return approval_fn

def make_node_router(node_id: str, edges_cfg: List[Dict[str, Any]]):
    # Find all outgoing edges from this node that have a conditional routing 'when'
    node_edges = [e for e in edges_cfg if e.get("from") == node_id and e.get("when") is not None]

    def router_fn(state: WorkflowState) -> str:
        last_output = state.get("last_output", "").lower()
        approval_status = state.get("approval_status", "")

        # Check approval decisions first
        if approval_status:
            for edge in node_edges:
                if edge.get("when", "").lower() == approval_status.lower():
                    return edge.get("when")

        # Evaluate based on conditional outcomes
        for edge in node_edges:
            when_val = edge.get("when", "").lower()
            if when_val == "true" and ("error" in last_output or "fail" in last_output):
                return edge.get("when")
            if when_val == "false" and not ("error" in last_output or "fail" in last_output):
                return edge.get("when")
            if when_val in last_output:
                return edge.get("when")

        # Fallback to the first matching conditional path or standard default
        if node_edges:
            return node_edges[0].get("when")
        return "default"

    return router_fn

def build_graph(workflow_json: Dict[str, Any], agents_map: Dict[str, Agent]):
    """Dynamic LangGraph compiler that takes workflow JSON and compiles a StateGraph."""
    nodes_cfg = workflow_json.get("nodes", [])
    edges_cfg = workflow_json.get("edges", [])

    # Initialize stateful graph
    graph = StateGraph(WorkflowState)

    # 1. Add all nodes
    for node in nodes_cfg:
        node_id = node.get("id")
        node_type = node.get("type")

        if node_type == "agent":
            agent_id = node.get("agent_id") or node.get("data", {}).get("agent_id")
            if not agent_id:
                raise ValueError(f"Agent ID not specified for node {node_id}")
            if agent_id not in agents_map:
                raise ValueError(f"Agent with ID {agent_id} not found for node {node_id}")
            graph.add_node(node_id, make_agent_node(agents_map[agent_id]))
        elif node_type == "condition":
            graph.add_node(node_id, make_condition_node(node_id))
        elif node_type == "approval":
            question = node.get("question") or node.get("data", {}).get("question") or "Approve execution?"
            graph.add_node(node_id, make_approval_node(node_id, question))
        elif node_type == "trigger":
            # Trigger node is a pass-through
            graph.add_node(node_id, lambda s: {"messages": []})
        elif node_type == "end":
            # End node is a pass-through
            graph.add_node(node_id, lambda s: {"messages": []})

    # 2. Add all edges
    # We group edges by their 'from' node to detect conditional routing
    edges_by_from = {}
    for edge in edges_cfg:
        edges_by_from.setdefault(edge.get("from"), []).append(edge)

    for from_node, node_edges in edges_by_from.items():
        # Check if there is conditional routing from this node
        conditional_edges = [e for e in node_edges if e.get("when") is not None]
        
        if conditional_edges:
            # Compile conditional path routing
            router_fn = make_node_router(from_node, edges_cfg)
            path_map = {e.get("when"): e.get("to") for e in conditional_edges}
            
            # Register routes in the graph
            graph.add_conditional_edges(from_node, router_fn, path_map)
        else:
            # Standard single edge connection
            for edge in node_edges:
                graph.add_edge(edge.get("from"), edge.get("to"))

    # Define graph entry point
    # Find the node of type 'trigger' to set as entry point
    trigger_node = next((n.get("id") for n in nodes_cfg if n.get("type") == "trigger"), None)
    if not trigger_node:
         raise ValueError("Workflow JSON must contain a trigger node.")

    graph.set_entry_point(trigger_node)

    # Compile the graph
    return graph.compile()
