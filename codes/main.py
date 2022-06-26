from fastapi import FastAPI
import apis.account
import apis.studyroom
import apis.book
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(apis.account.router)
app.include_router(apis.studyroom.router)
app.include_router(apis.book.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def mainpage():
    return { 'message': 'hello, world!' }
