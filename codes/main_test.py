from fastapi.testclient import TestClient
import pytest_utils
from main import app


client = TestClient(app)


def test_mainpage():
    resp = client.get('/').json()
    assert resp == { 'message': 'hello, world!' }
