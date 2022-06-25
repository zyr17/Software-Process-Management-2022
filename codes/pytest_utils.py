from typing import Optional
from db.redis import RedisDB


db = RedisDB()


def reset_db():
    db.reset()


def add_admin_account(name = 'admin', password = 'password'):
    """add one admin account"""
    resp, info = db.create_user(name, password, '0', 'admin')
    assert resp, info


def add_student_account(name, password, stuNum):
    """add one admin account"""
    resp, info = db.create_user(name, password, stuNum, 'user')
    assert resp, info


def get_header(auth: Optional[str] = None):
    header = { 'Content-Type': 'application/json' }
    if auth is not None:
        header['Auth-Token'] = auth
    return header


def get_token(client, name, password):
    # get admin token
    resp = client.post('/login', json = { 
        'name': name, 
        'password': password,
    })
    assert resp.status_code == 200, resp.json()
    token = resp.json()['auth']
    return token


def token2header(token: str):
    return { 'Auth-Token': token }