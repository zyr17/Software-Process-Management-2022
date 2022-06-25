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
    stuNum: Optional[str]
    name: Optional[str]
    currentPassword: Optional[str]
    newPassword: Optional[str]


@router.put('/user/{id}')
def modify_user(id: int, data: modify_user_put, 
                auth_token: Optional[str] = Header()):
    """
    if auth role is user, current password is needed; if is admin, can change
    without current password.
    """
    try:
        check_auth_token(auth_token, need_admin = True)
    except HTTPException:
        # not admin token, need current password and id should match
        check_auth_token(auth_token, False, id)
        if data.currentPassword is None or \
                not db.check_password(id, data.currentPassword)[0]:
            raise HTTPException(
                status_code = 401,
                detail = { 'error_msg': 'current password check failed' }
            )

    resp, info = db.modify_user(id, data.name, data.newPassword, 
                                data.stuNum)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return {}


@router.get('/user/{id}')
def get_user(id: int, auth_token: Optional[str] = Header()):
    check_auth_token(auth_token, False, id)
    resp, info = db.get_user(id)
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info


@router.get('/user')
def get_all_user(auth_token: Optional[str] = Header()):
    check_auth_token(auth_token, True)
    resp, info = db.get_all_users()
    if not resp:
        raise HTTPException(
            status_code = 403,
            detail = info
        )
    return info
