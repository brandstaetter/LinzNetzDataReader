import pytest
from fastapi.testclient import TestClient

from data_analyzer.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
