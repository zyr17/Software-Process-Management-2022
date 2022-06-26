from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from pydantic import BaseModel


db = RedisDB()
router = APIRouter()


class pos_checkin_post(BaseModel):
    position: str


@router.post('/position_checkin/{userid}')
def pos_checkin(userid: int, data: pos_checkin_post, 
                auth_token: str = Header()):
    check_auth_token(auth_token, False, userid)
    resp, info = db.pos_checkin(userid, data.position)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return {}
