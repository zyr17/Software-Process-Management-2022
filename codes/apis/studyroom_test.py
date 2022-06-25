from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app
import time


client = TestClient(app)


def test_create_studyroom():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    admin_token = get_token(client)
    user_token = get_token(client, 'stu', 'pass')

    # no header, 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    })
    assert resp.status_code == 422, resp.json()

    # miss data, 422
    resp = client.post('/studyroom', json = {
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # seatNumber invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 0,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': -10,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 'hahaha',
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # startTime invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': -10,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 24,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 'xxx',
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # endTime invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': -10
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 30
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 'yyy'
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # start time later than end time, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 4
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # user token cannot add, 401
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(user_token))
    assert resp.status_code == 401, resp.json()

    # building or classroom contain colon, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building:1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room:1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # empty building or classroom, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': '',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': '',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # success
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # success 2
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building2',
        'classRoomNumber': 'room2',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # success with building or classroom exist but not both
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room2',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # duplicate room, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
