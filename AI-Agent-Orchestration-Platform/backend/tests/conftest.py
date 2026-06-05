import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app
from backend.database import get_session
# Import models to register them with SQLModel metadata
from backend.models import Agent, Workflow, WorkflowRun, Log, Message, Memory, Conversation, Approval


# Test database engine
TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_platform.db")
connect_args = {"check_same_thread": False}
test_engine = create_engine(f"sqlite:///{TEST_DB_FILE}", connect_args=connect_args)

@pytest.fixture(name="session")
def session_fixture():
    # Override database engine globally
    import backend.database as db
    
    orig_engine = db.engine
    db.engine = test_engine
    
    # Setup database schemas
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
        
    db.engine = orig_engine
    SQLModel.metadata.drop_all(test_engine)
    
    # Dispose engine to close all connections before removing the file
    test_engine.dispose()
    
    # Cleanup test db file
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
