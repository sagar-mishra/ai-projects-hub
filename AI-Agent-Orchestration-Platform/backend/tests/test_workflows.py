import pytest
from fastapi.testclient import TestClient

def test_create_workflow(client: TestClient):
    graph_json = {
        "nodes": [
            { "id": "trigger", "type": "trigger" },
            { "id": "end", "type": "end" }
        ],
        "edges": [
            { "from": "trigger", "to": "end" }
        ]
    }
    response = client.post("/api/workflows", json={
        "name": "Test Workflow",
        "description": "Simple visual flow",
        "graph_json": json_string(graph_json)
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert "id" in data

def test_run_workflow(client: TestClient):
    # 1. Create a workflow
    graph_json = {
        "nodes": [
            { "id": "trigger", "type": "trigger" },
            { "id": "end", "type": "end" }
        ],
        "edges": [
            { "from": "trigger", "to": "end" }
        ]
    }
    create_response = client.post("/api/workflows", json={
        "name": "Run Test Workflow",
        "graph_json": json_string(graph_json)
    })
    wf_id = create_response.json()["id"]

    # 2. Trigger run
    response = client.post(f"/api/workflows/{wf_id}/run", json={
        "message": "Start task"
    })
    assert response.status_code == 202
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "pending"

def test_load_template(client: TestClient):
    # Load research pipeline template
    response = client.post("/api/templates/research_pipeline/load")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Research Pipeline"
    assert data["template_name"] == "Research Pipeline"
    assert data["is_template"] is False # instantiated workflow from template

def json_string(d):
    import json
    return json.dumps(d)
