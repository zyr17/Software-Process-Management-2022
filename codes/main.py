from fastapi import FastAPI
import apis.account
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(apis.account.router)


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/')
def mainpage():
    return { 'message': 'hello, world!' }
