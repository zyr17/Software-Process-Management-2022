from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app


client = TestClient(app)


def test_pos_checkin():
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

    # make book
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()

    # no auth, 422
    resp = client.post('/position_checkin/1', json = {
        'position': 'building1:room1'
    })
    assert resp.status_code == 422, resp.json()
    # checkin without position, 422
    resp = client.post('/position_checkin/1', json = {
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()
    # user checkin other user, 401
    resp = client.post('/position_checkin/1', json = {
        'position': 'building1:room1'
    }, headers = token2header(user2_token))
    assert resp.status_code == 401, resp.json()
    # checkin not booked user, 403
    resp = client.post('/position_checkin/2', json = {
        'position': 'building1:room1'
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()
    # checkin with wrong position, 403
    resp = client.post('/position_checkin/1', json = {
        'position': 'building1:room2'
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # checkin success
    resp = client.post('/position_checkin/1', json = {
        'position': 'building1:room1'
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    # checkin twice will fail
    resp = client.post('/position_checkin/1', json = {
        'position': 'building1:room1'
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # after checkin, user can book again
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 10,
        'endTime': 11
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()

    # although after checkin, seat still occupied, 403
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 13,
        'endTime': 14   
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()


def test_card_checkin():
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

    # make book
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()

    # no auth, 422
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
        'userId': 1
    })
    assert resp.status_code == 422, resp.json()
    # checkin missing id, 422
    resp = client.post('/card_checkin', json = {
        'userId': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    # user card checkin, 401
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
        'userId': 1
    }, headers = token2header(user1_token))
    assert resp.status_code == 401, resp.json()
    # checkin not booked user, 403
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
        'userId': 2
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # checkin not exist room, 403
    resp = client.post('/card_checkin', json = {
        'roomId': 9,
        'userId': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # checkin with wrong room, 403
    resp = client.post('/card_checkin', json = {
        'roomId': 1,
        'userId': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # checkin success
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
        'userId': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    # checkin twice will fail
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
        'userId': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # after checkin, user can book again
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 10,
        'endTime': 11
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # although after checkin, seat still occupied, 403
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 13,
        'endTime': 14   
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # position checkin success
    resp = client.post('/position_checkin/1', json = {
        'position': 'building1:room1'
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    # checkin twice will fail
    resp = client.post('/card_checkin', json = {
        'roomId': 0,
        'userId': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
