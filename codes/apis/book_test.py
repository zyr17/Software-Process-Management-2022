from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app
import time


client = TestClient(app)


def test_book():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    add_student_account('stu2', 'pass2', '')
    admin_token = get_token(client)
    user1_token = get_token(client, 'stu', 'pass')
    user2_token = get_token(client, 'stu2', 'pass2')

    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # no header, 422
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 14,
        'endTime': 15
    })
    assert resp.status_code == 422, resp.json()

    # field not complete, 422
    resp = client.post('/book/1', json = {
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 14,
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()

    # user book for other user, 401
    resp = client.post('/book/2', json = {
        'roomid': 0,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 401, resp.json()

    # book not exist room, 403
    resp = client.post('/book/1', json = {
        'roomid': 1,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    # book not exist user, 403
    resp = client.post('/book/9', json = {
        'roomid': 0,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # start time large than end time, 403
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 16,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    # time not in room range, 403
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 7,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 9,
        'endTime': 22
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # book success
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()

    # duplicate book, 403
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 8,
        'endTime': 9
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # book time has no empty seat, 403
    resp = client.post('/book/2', json = {
        'roomid': 0,
        'startTime': 10,
        'endTime': 12
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/2', json = {
        'roomid': 0,
        'startTime': 14,
        'endTime': 17
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/2', json = {
        'roomid': 0,
        'startTime': 9,
        'endTime': 17
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()

    # admin to book success
    resp = client.post('/book/2', json = {
        'roomid': 0,
        'startTime': 8,
        'endTime': 10
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()


def test_book_and_modify_studyroom():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    add_student_account('stu2', 'pass2', '')
    admin_token = get_token(client)
    user1_token = get_token(client, 'stu', 'pass')
    user2_token = get_token(client, 'stu2', 'pass2')

    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 2,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # make book
    resp = client.post('/book/1', json = {
        'roomid': 0,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/2', json = {
        'roomid': 0,
        'startTime': 11,
        'endTime': 16
    }, headers = token2header(user2_token))
    assert resp.status_code == 200, resp.json()

    # modify to lower seat, 403
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 1,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # startTime and endTime cover current booking, 403
    resp = client.put('/studyroom/0', json = {
        'startTime': 12,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'endTime': 15,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'startTime': 20,
        'endTime': 22,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 1,
        'startTime': 12,
        'endTime': 15,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # change success
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 3,
        'startTime': 11,
        'endTime': 16,
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 2,
        'startTime': 8,
        'endTime': 20,
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
