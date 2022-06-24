from fastapi import APIRouter, Header, HTTPException
from db.redis import RedisDB
from .auth import check_auth_token
from typing import Optional
from pydantic import BaseModel


db = RedisDB()
router = APIRouter()


class login_post(BaseModel):
    name: str
    password: str


@router.post('/login')
def login(data: login_post):
    name = data.name
    password = data.password
    resp, info = db.generate_auth_token(name, password)
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
    check_auth_token(auth_token, data.is_admin, data.id)
    return {}
