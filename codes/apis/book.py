from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from pydantic import BaseModel


db = RedisDB()
router = APIRouter()


class book_post(BaseModel):
    roomId: int
    date: int
    startTime: int
    endTime: int


@router.post('/book/{userid}')
def user_book(userid: int, data: book_post, auth_token: str = Header()):
    check_auth_token(auth_token, False, userid)
    resp, info = db.book(userid, data.roomId, data.date, data.startTime, 
                         data.endTime)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )


@router.get('/book/{userid}')
def get_book_info(userid: int, auth_token: str = Header()):
    check_auth_token(auth_token, False, userid)
    resp, info = db.is_booked(userid)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    if not info:
        raise HTTPException(
            status_code = 404,
            detail = 'not found'
        )
    resp, info = db.get_book(userid)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info
