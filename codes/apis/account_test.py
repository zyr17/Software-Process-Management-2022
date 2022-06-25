from fastapi.testclient import TestClient
import pytest_utils
from main import app
import time


client = TestClient(app)


def test_admin_login_and_auth_token():
    pytest_utils.reset_db()
    pytest_utils.add_admin_account()

    # password not right, 403
    resp = client.post('/login', json = { 
        'name': 'admin', 
        'password': 'p'
    })
    assert resp.status_code == 403, resp.json()

    # name not exist, 403
    resp = client.post('/login', json = { 
        'name': 'a', 
        'password': 'password'
    })
    assert resp.status_code == 403, resp.json()

    # token time length wrong, 403
    resp = client.post('/login', json = { 
        'name': 'a', 
        'password': 'password',
        'token_valid_time': 86400
    })
    assert resp.status_code == 403, resp.json()

    # sucessfully get token
    post_time = int(time.time()) + 3600
    resp = client.post('/login', json = { 
        'name': 'admin', 
        'password': 'password'
    })
    assert resp.status_code == 200, resp.json()
    assert resp.json()['role'] == 'admin'
    assert resp.json()['name'] == 'admin'
    # token expire time should later than post time + 3600s
    assert resp.json()['expire'] >= post_time
    token = resp.json()['auth']

    # should pass admin token check
    resp = client.get('/check_auth_token', json = { 'is_admin': True }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 200, resp.json()

    # id not match, but is admin token, should pass
    resp = client.get('/check_auth_token', json = { 'is_admin': False, 
                                                    'id': 999 }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 200, resp.json()

    # test token expire
    resp = client.post('/login', json = { 
        'name': 'admin', 
        'password': 'password',
        'token_valid_time': 1
    })
    assert resp.status_code == 200, resp.json()
    assert resp.json()['role'] == 'admin'
    token = resp.json()['auth']

    # sleep 2s, so token must expire and 401
    time.sleep(2)
    resp = client.get('/check_auth_token', json = { 'is_admin': True }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 401, resp.json()


def test_student_login_and_auth_token():
    pytest_utils.reset_db()
    pytest_utils.add_admin_account()
    pytest_utils.add_student_account('user1', 'pass1', '1024')

    # password not right, 403
    resp = client.post('/login', json = { 
        'name': 'user1', 
        'password': 'p'
    })
    assert resp.status_code == 403, resp.json()

    # name not exist, 403
    resp = client.post('/login', json = { 
        'name': 'u', 
        'password': 'pass1'
    })
    assert resp.status_code == 403, resp.json()

    # sucessfully get token
    resp = client.post('/login', json = { 
        'name': 'user1', 
        'password': 'pass1'
    })
    assert resp.status_code == 200, resp.json()
    assert resp.json()['name'] == 'user1'
    token = resp.json()['auth']

    # should 401 admin token check
    resp = client.get('/check_auth_token', json = { 'is_admin': True }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 401, resp.json()

    # should pass normal token check
    resp = client.get('/check_auth_token', json = { 'is_admin': False }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 200, resp.json()

    # id not match, should 401
    resp = client.get('/check_auth_token', json = { 'is_admin': False, 
                                                    'id': 999 }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 401, resp.json()

    # id should be 1 and match, should pass
    resp = client.get('/check_auth_token', json = { 'is_admin': False, 
                                                    'id': 1 }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 200, resp.json()


def test_student_register_and_login():
    pytest_utils.reset_db()
    pytest_utils.add_admin_account()

    # register a student with insufficient information, 422
    resp = client.post('/user', json = {
        'name': 'stu1',
        'password': 'password'
    })
    assert resp.status_code == 422, resp.json()
    resp = client.post('/user', json = {
        'password': 'password',
        'stuNum': '1'
    })
    assert resp.status_code == 422, resp.json()
    resp = client.post('/user', json = {
        'name': 'stu1',
        'stuNum': '1'
    })
    assert resp.status_code == 422, resp.json()

    # username or password empty, 403
    resp = client.post('/user', json = {
        'name': '',
        'password': 'password',
        'stuNum': '1'
    })
    assert resp.status_code == 403, resp.json()
    resp = client.post('/user', json = {
        'name': 'stu1',
        'password': '',
        'stuNum': '1'
    })
    assert resp.status_code == 403, resp.json()

    # success register
    resp = client.post('/user', json = {
        'name': 'stu1',
        'password': 'password',
        'stuNum': '1'
    })
    assert resp.status_code == 200, resp.json()

    # success register with empty stuNum
    resp = client.post('/user', json = {
        'name': 'stu2',
        'password': 'password2',
        'stuNum': ''
    })
    assert resp.status_code == 200, resp.json()

    # exist username, 403
    resp = client.post('/user', json = {
        'name': 'stu1',
        'password': 'password3',
        'stuNum': '1'
    })
    assert resp.status_code == 403, resp.json()

    # exist password and stuNum, 200
    resp = client.post('/user', json = {
        'name': 'stu3',
        'password': 'password',
        'stuNum': '1'
    })
    assert resp.status_code == 200, resp.json()

    # login and get token
    resp = client.post('/login', json = { 
        'name': 'stu1', 
        'password': 'password'
    })
    assert resp.status_code == 200, resp.json()
    assert resp.json()['name'] == 'stu1'
