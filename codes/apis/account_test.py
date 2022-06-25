from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app
import time


client = TestClient(app)


def test_admin_login_and_auth_token():
    reset_db()
    add_admin_account()

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

    # test big minus token, can generate but cannot use
    resp = client.post('/login', json = { 
        'name': 'admin', 
        'password': 'password',
        'token_valid_time': -1000000000000000
    })
    assert resp.status_code == 200, resp.json()
    assert resp.json()['role'] == 'admin'
    token = resp.json()['auth']
    resp = client.get('/check_auth_token', json = { 'is_admin': True }, 
                      headers = { 'Auth-Token': token })
    assert resp.status_code == 401, resp.json()

    # not exist token, 401
    resp = client.get('/check_auth_token', json = { 'is_admin': True }, 
                      headers = { 'Auth-Token': 'not-exist' })
    assert resp.status_code == 401, resp.json()


def test_student_login_and_auth_token():
    reset_db()
    add_admin_account()
    add_student_account('user1', 'pass1', '1024')

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
    reset_db()
    add_admin_account()

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


def test_get_user_information():
    reset_db()
    add_admin_account()
    add_student_account('stu1', 'pass1', 'num1')
    add_student_account('stu2', 'pass2', '')

    admin_token = get_token(client, 'admin', 'password')
    stu1_token = get_token(client, 'stu1', 'pass1')
    stu2_token = get_token(client, 'stu2', 'pass2')

    # no auth token, 422
    resp = client.get('/user/0')
    assert resp.status_code == 422, resp.json()

    # use admin token, get data should same
    resp = client.get('/user/0', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == {
        'id': 0,
        'stuNum': '0',
        'name': 'admin',
        'role': 'admin'
    }
    resp = client.get('/user/1', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == {
        'id': 1,
        'stuNum': 'num1',
        'name': 'stu1',
        'role': 'user'
    }
    resp = client.get('/user/2', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == {
        'id': 2,
        'stuNum': '',
        'name': 'stu2',
        'role': 'user'
    }

    # id not exist, 403
    resp = client.get('/user/3', headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # id not int, 422
    resp = client.get('/user/hahaha', headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # use stu1 token get self, should same
    resp = client.get('/user/1', headers = token2header(stu1_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == {
        'id': 1,
        'stuNum': 'num1',
        'name': 'stu1',
        'role': 'user'
    }
    # use stu2 token get self, should same
    resp = client.get('/user/2', headers = token2header(stu2_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == {
        'id': 2,
        'stuNum': '',
        'name': 'stu2',
        'role': 'user'
    }
    # use stu1 token get stu2, 401
    resp = client.get('/user/2', headers = token2header(stu1_token))
    assert resp.status_code == 401, resp.json()


def test_get_all_user_information():
    reset_db()
    add_admin_account()

    admin_token = get_token(client, 'admin', 'password')

    admin_info = { 'id': 0, 'stuNum': '0', 'name': 'admin', 'role': 'admin' }
    stu_infos = [
        { 'id': 1, 'password': 'pass1', 'stuNum': 'num1', 
          'name': 'stu1', 'role': 'user' },
        { 'id': 2, 'password': 'pass2', 'stuNum': '', 
          'name': 'stu2', 'role': 'user' },
        { 'id': 3, 'password': 'pass3', 'stuNum': '333', 
          'name': 'ssssttu3', 'role': 'user' },
    ]
    current_infos = [admin_info]

    # without auth, 422
    resp = client.get('/user')
    assert resp.status_code == 422, resp.json()

    # admin auth
    resp = client.get('/user', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == current_infos

    # add account and check
    for stu in stu_infos:
        add_student_account(stu['name'], stu['password'], stu['stuNum'])
        stu = stu.copy()
        del stu['password']
        current_infos.append(stu)
        resp = client.get('/user', headers = token2header(admin_token))
        assert resp.status_code == 200, resp.json()
        assert resp.json() == current_infos

    # with user token, 401
    user_token = get_token(client, stu_infos[0]['name'], 
                           stu_infos[0]['password'])
    resp = client.get('/user', headers = token2header(user_token))
    assert resp.status_code == 401, resp.json()


def test_modify_user():
    # TODO currently modify information will not expire available tokens.
    reset_db()
    add_admin_account()
    add_student_account('stu1', 'pass1', 'num1')
    add_student_account('stu2', 'pass2', '')

    admin_token = get_token(client, 'admin', 'password')
    stu1_token = get_token(client, 'stu1', 'pass1')
    stu2_token = get_token(client, 'stu2', 'pass2')

    admin_info = { 'id': 0, 'stuNum': '0', 'name': 'admin', 'role': 'admin' }
    stu1_info = { 'id': 1, 'stuNum': 'num1', 'name': 'stu1', 'role': 'user' }
    stu2_info = { 'id': 2, 'stuNum': '', 'name': 'stu2', 'role': 'user' }

    # user change others, 401 and data not change
    resp = client.put('/user/2', json = {
        'name': 'mod2',
        'currentPassword': 'pass2',
        'newPassword': 'mod2'
    }, headers = token2header(stu1_token))
    assert resp.status_code == 401, resp.json()
    assert client.get('/user/2', headers = token2header(admin_token)).json() \
           == stu2_info

    # user change self without pass or wrong pass, 401
    resp = client.put('/user/2', json = {
        'name': 'mod2',
        'stuNum': 'mod2',
        'currentPassword': 'wrong',
        'newPassword': 'mod2'
    }, headers = token2header(stu2_token))
    assert resp.status_code == 401, resp.json()
    assert client.get('/user/2', headers = token2header(admin_token)).json() \
           == stu2_info
    # empty currentPassword, 401
    resp = client.put('/user/2', json = {
        'name': 'mod2',
        'stuNum': 'mod2',
        'currentPassword': '',
        'newPassword': 'mod2'
    }, headers = token2header(stu2_token))
    assert resp.status_code == 401, resp.json()
    assert client.get('/user/2', headers = token2header(admin_token)).json() \
           == stu2_info
    # not send currentPassword, 401
    resp = client.put('/user/2', json = {
        'name': 'mod2',
        'stuNum': 'mod2',
        'newPassword': 'mod2'
    }, headers = token2header(stu2_token))
    assert resp.status_code == 401, resp.json()
    assert client.get('/user/2', headers = token2header(admin_token)).json() \
           == stu2_info
    # change to exist username, 403
    resp = client.put('/user/2', json = {
        'name': 'admin',
        'stuNum': 'mod2',
        'currentPassword': 'pass2',
        'newPassword': 'mod2'
    }, headers = token2header(stu2_token))
    assert resp.status_code == 403, resp.json()
    # user change successful, and can login with new username
    resp = client.put('/user/2', json = {
        'name': 'mod2',
        'stuNum': 'mod2',
        'currentPassword': 'pass2',
        'newPassword': 'mod2'
    }, headers = token2header(stu2_token))
    assert resp.status_code == 200, resp.json()
    assert client.get('/user/2', headers = token2header(admin_token)).json() \
           == { 'id': 2, 'name': 'mod2', 'stuNum': 'mod2', 'role': 'user' }
    resp = client.post('/login', json = { 'name': 'mod2', 'password': 'mod2' })
    assert resp.status_code == 200, resp.json()
    # user change successful with partial information change
    resp = client.put('/user/1', json = {
        'stuNum': 'mod1',
        'currentPassword': 'pass1',
        'newPassword': 'mod1'
    }, headers = token2header(stu1_token))
    assert resp.status_code == 200, resp.json()
    assert client.get('/user/1', headers = token2header(admin_token)).json() \
           == { 'id': 1, 'name': 'stu1', 'stuNum': 'mod1', 'role': 'user' }
    resp = client.post('/login', json = { 'name': 'stu1', 'password': 'mod1' })
    assert resp.status_code == 200, resp.json()

    # change with empty username or password, 403
    resp = client.put('/user/2', json = {
        'name': '',
        'stuNum': 'mod2',
        'newPassword': 'mod2'
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/user/2', json = {
        'name': 'mod2',
        'stuNum': 'mod2',
        'newPassword': ''
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # admin change not exist user, 403
    resp = client.put('/user/200', json = {
        'name': 'mod200',
        'stuNum': 'mod200',
        'newPassword': 'mod200'
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # admin change its information without password
    resp = client.put('/user/0', json = {
        'stuNum': 'mod0',
        'newPassword': 'mod0'
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert client.get('/user/0', headers = token2header(admin_token)).json() \
           == { 'id': 0, 'name': 'admin', 'stuNum': 'mod0', 'role': 'admin' }
    resp = client.post('/login', json = { 'name': 'admin', 
                                          'password': 'mod0' })
    assert resp.status_code == 200, resp.json()

    # admin change others without password
    resp = client.put('/user/1', json = {
        'stuNum': '',
        'newPassword': 'modx'
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert client.get('/user/1', headers = token2header(admin_token)).json() \
           == { 'id': 1, 'name': 'stu1', 'stuNum': '', 'role': 'user' }
    resp = client.post('/login', json = { 'name': 'stu1', 
                                          'password': 'modx' })
    assert resp.status_code == 200, resp.json()

    # admin only change others username
    resp = client.put('/user/1', json = {
        'name': 'modx',
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert client.get('/user/1', headers = token2header(admin_token)).json() \
           == { 'id': 1, 'name': 'modx', 'stuNum': '', 'role': 'user' }
    resp = client.post('/login', json = { 'name': 'modx', 
                                          'password': 'modx' })
    assert resp.status_code == 200, resp.json()
