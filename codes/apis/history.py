from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from pydantic import BaseModel


db = RedisDB()
router = APIRouter()


@router.get('/history/{userid}')
def history_get(userid: int, auth_token: str = Header()):
    check_auth_token(auth_token, False, userid)
    resp, info = db.get_history(userid)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info


class history_delete(BaseModel):
    roomId: int
    date: int
    startTime: int
    endTime: int


@router.delete('/history/{userid}')
def history_delete_func(userid: int, data: history_delete, 
                        auth_token: str = Header()):
    check_auth_token(auth_token, False, userid)
    resp, info = db.delete_history(userid, data.roomId, data.date, 
                                   data.startTime, data.endTime)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info
