import pytest
from fastapi.testclient import TestClient

def test_telegram_webhook_accepts_payload(client: TestClient):
    payload = {
        "update_id": 1234567,
        "message": {
            "message_id": 1,
            "from": {
                "id": 9999,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 8888,
                "first_name": "Test",
                "type": "private"
            },
            "date": 1600000000,
            "text": "What is the capital of France?"
        }
    }
    response = client.post("/webhook/telegram", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
