import pytest
from fastapi.testclient import TestClient
from backend.models import Agent

def test_create_agent(client: TestClient):
    response = client.post("/api/agents", json={
        "name": "Test Researcher",
        "role": "Search Assistant",
        "description": "Searches online sources",
        "system_prompt": "You are a search assistant.",
        "model": "llama-3.1-8b-instant",
        "tools_json": "[\"web_search\"]",
        "memory_enabled": True
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Researcher"
    assert data["role"] == "Search Assistant"
    assert data["tools_json"] == "[\"web_search\"]"
    assert "id" in data

def test_create_agent_invalid_tools(client: TestClient):
    response = client.post("/api/agents", json={
        "name": "Invalid Agent",
        "system_prompt": "Test prompt",
        "tools_json": "invalid-json"
    })
    assert response.status_code == 422

def test_get_agent(client: TestClient):
    # Create an agent first
    create_response = client.post("/api/agents", json={
        "name": "Get Agent",
        "system_prompt": "Test"
    })
    agent_id = create_response.json()["id"]

    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Agent"

def test_get_agent_not_found(client: TestClient):
    response = client.get("/api/agents/non-existent-id")
    assert response.status_code == 404

def test_update_agent(client: TestClient):
    create_response = client.post("/api/agents", json={
        "name": "Update Me",
        "system_prompt": "Original prompt"
    })
    agent_id = create_response.json()["id"]

    response = client.put(f"/api/agents/{agent_id}", json={
        "name": "Updated Name",
        "system_prompt": "New prompt"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["system_prompt"] == "New prompt"

def test_delete_agent(client: TestClient):
    create_response = client.post("/api/agents", json={
        "name": "Delete Me",
        "system_prompt": "To be deleted"
    })
    agent_id = create_response.json()["id"]

    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/api/agents/{agent_id}")
    assert get_response.status_code == 404
