from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from typing import Optional
from pydantic import BaseModel


db = RedisDB()
router = APIRouter()


class login_post(BaseModel):
    """
    login params. name and password is essential. if token_valid_time is not
    specified, then default maximum(3600s) is used. otherwise, use specified
    time, but cannot exceed maximum time.
    """
    name: str
    password: str
    token_valid_time: Optional[int]


@router.post('/login')
def login(data: login_post):
    name = data.name
    password = data.password
    time = 3600
    if data.token_valid_time is not None:
        time = data.token_valid_time
    if time > 3600:
        raise HTTPException(
            status_code = 403,
            detail = { 'error_msg': 'token valid time too long' }
        )
    resp, info = db.generate_auth_token(name, password, time)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info


class check_auth_get(BaseModel):
    id: Optional[int]
    is_admin: bool = False


@router.get('/check_auth_token')
def check_auth_token_page(data: check_auth_get, auth_token: str = Header()):
    """
    check if auth token is valid with specified permission
    """
    check_auth_token(auth_token, data.is_admin, data.id)
    return {}


class register_user_post(BaseModel):
    name: str
    password: str
    stuNum: str


@router.post('/user')
def register_user(data: register_user_post):
    resp, info = db.create_user(data.name, data.password, data.stuNum, 
                                role = 'user')
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return {}


class modify_user_put(BaseModel):
    id: int
    stuNum: Optional[str]
    name: Optional[str]
    currentPassword: Optional[str]
    newPassword: Optional[str]


@router.put('/user')
def modify_user(data: modify_user_put, auth_token: Optional[str] = Header()):
    raise HTTPException(
        status_code = 403,
        detail = { 'error_msg': 'Not Implemented' }
    )
