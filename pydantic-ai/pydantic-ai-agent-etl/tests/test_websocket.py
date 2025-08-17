import pytest
from fastapi.testclient import TestClient
from app.api.v1.websocket import manager
from core.server import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def test_client(app):
    return TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup connections after each test"""
    yield
    manager.active_connections.clear()

def test_websocket_functionality(test_client):
    # Test with correlation ID in headers
    headers = {"x-correlation-id": "test-correlation-id-1"}
    with test_client.websocket_connect("/api/v1/ws", headers=headers) as websocket1:
        headers2 = {"x-correlation-id": "test-correlation-id-2"}
        with test_client.websocket_connect("/api/v1/ws", headers=headers2) as websocket2:
            # Test message sending
            websocket1.send_text("Hello from client 1")
            response1 = websocket1.receive_text()
            assert response1 == "Message received: Hello from client 1"
            
            # Test message from second client
            websocket2.send_text("Hello from client 2")
            response2 = websocket2.receive_text()
            assert response2 == "Message received: Hello from client 2"

def test_connection_management(test_client):
    correlation_id = "test-correlation-id"
    headers = {"x-correlation-id": correlation_id}
    
    assert correlation_id not in manager.active_connections
    
    with test_client.websocket_connect("/api/v1/ws", headers=headers) as websocket:
        # Verify connection is stored with correlation ID
        assert correlation_id in manager.active_connections
        
        # Test message with correlation ID context
        websocket.send_text("Test message")
        response = websocket.receive_text()
        assert response == "Message received: Test message"

    # Verify connection is removed after closing
    assert correlation_id not in manager.active_connections

def test_correlation_id_generation(test_client):
    """Test automatic correlation ID generation when not provided"""
    with test_client.websocket_connect("/api/v1/ws") as websocket:
        # Send message to trigger logging
        websocket.send_text("Test message")
        response = websocket.receive_text()
        
        # Verify response and that a correlation ID was generated
        assert response == "Message received: Test message"
        assert len(manager.active_connections) == 1
        generated_id = list(manager.active_connections.keys())[0]
        assert generated_id is not None
        assert len(generated_id) > 0

def test_stress_test_websocket(test_client):
    """Test multiple concurrent connections and messages"""
    def client_session(client_id):
        headers = {"x-correlation-id": f"stress-test-{client_id}"}
        with test_client.websocket_connect("/api/v1/ws", headers=headers) as websocket:
            for i in range(5):
                message = f"Message {i} from client {client_id}"
                websocket.send_text(message)
                response = websocket.receive_text()
                assert response == f"Message received: {message}"

    # Run multiple clients
    num_clients = 5
    for i in range(num_clients):
        client_session(i)

    # Verify all connections are properly closed
    assert len(manager.active_connections) == 0
