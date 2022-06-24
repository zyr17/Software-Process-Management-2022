from fastapi import FastAPI
import apis.account


app = FastAPI()
app.include_router(apis.account.router)


@app.get('/')
def mainpage():
    return { 'message': 'hello, world!' }
