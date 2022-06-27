from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app
import time


client = TestClient(app)


def test_get_history():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    add_student_account('stu2', 'pass2', '')
    add_student_account('stu3', 'pass3', '')
    admin_token = get_token(client)
    user1_token = get_token(client, 'stu', 'pass')
    user2_token = get_token(client, 'stu2', 'pass2')
    user3_token = get_token(client, 'stu3', 'pass3')

    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'startDate': 20000,
        'endDate': 20010,
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building2',
        'classRoomNumber': 'room2',
        'startDate': 20000,
        'endDate': 20010,
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # make book, checkin and cancel
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    time.sleep(1)  # to make sure timestamp different
    assert resp.status_code == 200, resp.json()
    resp = client.delete('/book/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 13,
        'endTime': 15
    }, headers = token2header(user1_token))
    time.sleep(1)  # to make sure timestamp different
    assert resp.status_code == 200, resp.json()
    resp = client.post('/card_checkin', json = {
        'userId': 1,
        'roomId': 0
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 1,
        'date': 20006,
        'startTime': 12,
        'endTime': 13
    }, headers = token2header(user1_token))
    time.sleep(1)  # to make sure timestamp different
    assert resp.status_code == 200, resp.json()

    # no auth, 422
    resp = client.get('/history/1')
    assert resp.status_code == 422, resp.json()

    # wrong user token, 401
    resp = client.get('/history/1', headers = token2header(user2_token))
    assert resp.status_code == 401, resp.json()

    # not exist user, 403
    resp = client.get('/history/9', headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # find empty user success
    resp = client.get('/history/2', headers = token2header(user2_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == []

    # history success
    resp = client.get('/history/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    for x in data:
        dkey = ['bookTimeStamp', 'checkinTimeStamp', 'cancelTimeStamp']
        for k in dkey:
            if k in x:
                del x[k]
    assert data == [
        {
            'type': 'booked',
            'roomId': 1,
            'buildingNumber': 'building2',
            'classRoomNumber': 'room2',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
        {
            'type': 'checkin',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20005,
            'startTime': 13,
            'endTime': 15,
        },
        {
            'type': 'cancel',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20005,
            'startTime': 12,
            'endTime': 15,
        },
    ]

    # cancel and rebook cancelled
    resp = client.delete('/book/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20006,
        'startTime': 12,
        'endTime': 13
    }, headers = token2header(user1_token))
    time.sleep(1)  # to make sure timestamp different
    assert resp.status_code == 200, resp.json()
    resp = client.delete('/book/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 1,
        'date': 20006,
        'startTime': 12,
        'endTime': 13
    }, headers = token2header(user1_token))
    time.sleep(1)  # to make sure timestamp different
    assert resp.status_code == 200, resp.json()

    # history success, rebook overlap cancel
    resp = client.get('/history/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    for x in data:
        dkey = ['bookTimeStamp', 'checkinTimeStamp', 'cancelTimeStamp']
        for k in dkey:
            if k in x:
                del x[k]
    assert data == [
        {
            'type': 'booked',
            'roomId': 1,
            'buildingNumber': 'building2',
            'classRoomNumber': 'room2',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
        {
            'type': 'cancel',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
        {
            'type': 'checkin',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20005,
            'startTime': 13,
            'endTime': 15,
        },
        {
            'type': 'cancel',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20005,
            'startTime': 12,
            'endTime': 15,
        },
    ]


def test_delete_history():
    test_get_history()  # reset to last history
    admin_token = get_token(client)
    user1_token = get_token(client, 'stu', 'pass')
    user2_token = get_token(client, 'stu2', 'pass2')
    user3_token = get_token(client, 'stu3', 'pass3')

    # no auth, 422
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    })
    assert resp.status_code == 422, resp.json()

    # field miss, 422
    resp = client.delete('/history/1', json = {
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20005,
        'endTime': 15
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # delete other user, 401
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user2_token))
    assert resp.status_code == 401, resp.json()

    # not exist, 403
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20008,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # delete book, 403
    resp = client.delete('/history/1', json = {
        'roomId': 1,
        'date': 20006,
        'startTime': 12,
        'endTime': 13
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # admin delete checkin success
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 13,
        'endTime': 15
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.get('/history/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    for x in data:
        dkey = ['bookTimeStamp', 'checkinTimeStamp', 'cancelTimeStamp']
        for k in dkey:
            if k in x:
                del x[k]
    assert data == [
        {
            'type': 'booked',
            'roomId': 1,
            'buildingNumber': 'building2',
            'classRoomNumber': 'room2',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
        {
            'type': 'cancel',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
        {
            'type': 'cancel',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20005,
            'startTime': 12,
            'endTime': 15,
        },
    ]

    # delete cancel success
    resp = client.delete('/history/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    resp = client.get('/history/1', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    for x in data:
        dkey = ['bookTimeStamp', 'checkinTimeStamp', 'cancelTimeStamp']
        for k in dkey:
            if k in x:
                del x[k]
    assert data == [
        {
            'type': 'booked',
            'roomId': 1,
            'buildingNumber': 'building2',
            'classRoomNumber': 'room2',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
        {
            'type': 'cancel',
            'roomId': 0,
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'date': 20006,
            'startTime': 12,
            'endTime': 13,
        },
    ]
