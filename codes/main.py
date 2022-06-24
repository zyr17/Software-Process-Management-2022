from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get('/')
def mainpage():
    return { 'message': 'hello, world!' }
