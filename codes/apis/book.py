from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from pydantic import BaseModel
from typing import Optional


db = RedisDB()
router = APIRouter()


class book_post(BaseModel):
    roomid: int
    startTime: int
    endTime: int


@router.post('/book/{userid}')
def user_book(userid: int, data: book_post, auth_token: str = Header()):
    check_auth_token(auth_token, False, userid)
    resp, info = db.book(userid, data.roomid, data.startTime, data.endTime)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
