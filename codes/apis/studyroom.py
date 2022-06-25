from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from pydantic import BaseModel


db = RedisDB()
router = APIRouter()


class add_studyroom_post(BaseModel):
    buildingNumber: str
    classRoomNumber: str
    seatNumber: int
    startTime: int
    endTime: int 


@router.post('/studyroom')
def add_studyroom(data: add_studyroom_post, auth_token: str = Header()):
    check_auth_token(auth_token, True)
    resp, info = db.create_studyroom(
        data.buildingNumber, data.classRoomNumber, data.seatNumber, 
        data.startTime, data.endTime
    )
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info
