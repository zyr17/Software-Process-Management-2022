from fastapi.testclient import TestClient
import pytest_utils
from main import app


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

    # sucessfully get token
    resp = client.post('/login', json = { 
        'name': 'admin', 
        'password': 'password'
    })
    assert resp.status_code == 200, resp.json()
    token = resp.json()['auth']

    # should pass admin token check
    resp = client.get('/check_auth_token', json = { 'is_admin': True }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 200

    # id not match, but is admin token, should pass
    resp = client.get('/check_auth_token', json = { 'is_admin': False, 
                                                    'id': 999 }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 200


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
