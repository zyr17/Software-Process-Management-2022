from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app


client = TestClient(app)


def test_book_and_get_all_studyroom():
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

    # no header, 422
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 14,
        'endTime': 15
    })
    assert resp.status_code == 422, resp.json()

    # field not complete, 422
    resp = client.post('/book/1', json = {
        'date': 20005,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'startTime': 14,
    }, headers = token2header(user1_token))
    assert resp.status_code == 422, resp.json()

    # user book for other user, 401
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 401, resp.json()

    # book not exist room, 403
    resp = client.post('/book/1', json = {
        'roomId': 1,
        'date': 20005,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    # book not exist user, 403
    resp = client.post('/book/9', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 14,
        'endTime': 15
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # start time large than end time, 403
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 16,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    # time not in room range, 403
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 7,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 9,
        'endTime': 22
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # date not in range, 403
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 200,
        'startTime': 10,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20012,
        'startTime': 9,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # book success
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    # user3 success to occupy whole day of another day
    resp = client.post('/book/3', json = {
        'roomId': 0,
        'date': 20006,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(user3_token))
    assert resp.status_code == 200, resp.json()

    # duplicate book, 403
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 8,
        'endTime': 9
    }, headers = token2header(user1_token))
    assert resp.status_code == 403, resp.json()

    # book time has no empty seat, 403
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 10,
        'endTime': 12
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 14,
        'endTime': 17
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 9,
        'endTime': 17
    }, headers = token2header(user2_token))
    assert resp.status_code == 403, resp.json()

    # admin to book success
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 8,
        'endTime': 10
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # get all studyroom, empty number should match
    resp = client.get('/studyroom', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == [ {
        'id': 0,
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18,
        'book': [
            { 'date': 20005, 'startTime': 8, 'endTime': 10, 'type': 'booked'},
            { 'date': 20005, 'startTime': 12, 'endTime': 15, 'type': 'booked'},
            { 'date': 20006, 'startTime': 8, 'endTime': 18, 'type': 'booked'},
        ]
    } ]


def test_book_and_modify_studyroom():
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
        'seatNumber': 2,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
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
    resp = client.post('/book/3', json = {
        'roomId': 0,
        'date': 20010,
        'startTime': 10,
        'endTime': 17
    }, headers = token2header(user3_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
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
        'startTime': 11,
        'endTime': 16,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # startDate and endDate cover current booking, 403
    resp = client.put('/studyroom/0', json = {
        'startDate': 20006,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'endDate': 20009,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'startDate': 20006,
        'endDate': 20019,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 1,
        'startDate': 11,
        'endDate': 16,
        'startDate': 20006,
        'endDate': 20009,
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # change success
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 3,
        'startTime': 10,
        'endTime': 17,
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.put('/studyroom/0', json = {
        'seatNumber': 2,
        'startTime': 8,
        'endTime': 20,
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()


def test_get_book():
    pass

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
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # get not booked user, 404
    resp = client.get('/book/1', headers = token2header(user1_token))
    assert resp.status_code == 404, resp.json()

    # get not exist user, 403
    resp = client.get('/book/9', headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # make book
    resp = client.post('/book/1', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }, headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    resp = client.post('/book/2', json = {
        'roomId': 0,
        'date': 20005,
        'startTime': 11,
        'endTime': 16
    }, headers = token2header(user2_token))
    assert resp.status_code == 200, resp.json()

    book1_out = {
        'roomId': 0,
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'date': 20005,
        'startTime': 12,
        'endTime': 15
    }
    book2_out = {
        'roomId': 0,
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'date': 20005,
        'startTime': 11,
        'endTime': 16
    }

    # user get other user book, 401
    resp = client.get('/book/1', headers = token2header(user2_token))
    assert resp.status_code == 401, resp.json()

    # user get book
    resp = client.get('/book/1', headers = token2header(user1_token))
    assert resp.status_code == 200, resp.json()
    respjson = resp.json()
    del respjson['bookTimeStamp']
    assert respjson == book1_out

    # admin get book
    resp = client.get('/book/2', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    respjson = resp.json()
    del respjson['bookTimeStamp']
    assert respjson == book2_out
