from fastapi import HTTPException
from db.redis import RedisDB
from typing import Optional


db = RedisDB()


def check_auth_token(token: Optional[str], need_admin: bool, 
                     need_id: Optional[int] = None):
    """
    check if auth token is valid and fit role.

    if need_id is set, then token should exactly belongs to the user OR an
    admin token.

    if token not exist/expire/role wrong, raise 401
    if all pass, return None
    """
    if token is None:
        raise HTTPException(
            status_code = 401,
            detail = { 'error_msg': 'no auth token in header' }
        )
    resp, info = db.check_auth_token(token)
    if not resp:
        raise HTTPException(
            status_code = 401,
            detail = info
        )
    if need_admin and info['role'] != 'admin':
        raise HTTPException(
            status_code = 401,
            detail = { 'error_msg': 'not admin' }
        )
    if need_id is not None and int(info['id']) != need_id \
            and info['role'] != 'admin':
        raise HTTPException(
            status_code = 401,
            detail = { 
                'error_msg': 'auth token id and operation id not match'
            }
        )
