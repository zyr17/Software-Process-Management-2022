from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from pydantic import BaseModel
from typing import Optional


db = RedisDB()
router = APIRouter()


class add_studyroom_post(BaseModel):
    buildingNumber: str
    classRoomNumber: str
    seatNumber: int
    startDate: int
    endDate: int
    startTime: int
    endTime: int


@router.post('/studyroom')
def add_studyroom(data: add_studyroom_post, auth_token: str = Header()):
    """
    here start time x means x:00 and end time y means y:59. 
    e.g. start time 8 end time 18 means available for 8:00-18:59.

    start date and end date is the day passed from 1970.1.1, and
    1970.1.1 is day 0.
    """
    check_auth_token(auth_token, True)
    resp, info = db.create_studyroom(
        data.buildingNumber, data.classRoomNumber, data.seatNumber, 
        data.startDate, data.endDate, data.startTime, data.endTime
    )
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info


@router.get('/studyroom/{id}')
def get_studyroom(id: int, auth_token: str = Header()):
    check_auth_token(auth_token, False)
    resp, info = db.get_studyroom(id)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info


@router.get('/studyroom')
def get_all_studyrooms(auth_token: str = Header()):
    check_auth_token(auth_token, False)
    resp, info = db.get_all_studyrooms()
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info


class modify_studyroom_post(BaseModel):
    buildingNumber: Optional[str]
    classRoomNumber: Optional[str]
    seatNumber: Optional[int]
    startDate: Optional[int]
    endDate: Optional[int]
    startTime: Optional[int]
    endTime: Optional[int]


@router.put('/studyroom/{id}')
def modify_studyroom(id: int, data: modify_studyroom_post, 
                     auth_token: str = Header()):
    check_auth_token(auth_token, True)
    resp, info = db.modify_studyroom(
        id, data.buildingNumber, data.classRoomNumber, data.seatNumber,
        data.startDate, data.endDate, data.startTime, data.endTime)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info
