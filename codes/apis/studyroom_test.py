from fastapi.testclient import TestClient
from pytest_utils import (reset_db, add_admin_account, add_student_account, 
                          get_token, token2header)
from main import app


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
        'startDate': 20000,
        'endDate': 20010,
        'seatNumber': 1,
        'startTime': 8,
        'endTime': 18
    })
    assert resp.status_code == 422, resp.json()

    # miss data, 422
    resp = client.post('/studyroom', json = {
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
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
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': -10,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 'hahaha',
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # startTime invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': -10,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 24,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 'xxx',
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # endTime invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': -10
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 30
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 'yyy'
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # startDate invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': -1,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 999999,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 'aaa',
        'endDate': 20010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # startDate invalid 403, type wrong 422
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': -1000000000,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 1010101010,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 'bbb',
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # start date later than end date, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 19000,
        'startTime': 8,
        'endTime': 18
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # start time later than end time, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 4
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # user token cannot add, 401
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(user_token))
    assert resp.status_code == 401, resp.json()

    # building or classroom contain colon, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building:1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room:1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # empty building or classroom, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': '',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': '',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # success
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # success 2
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building2',
        'classRoomNumber': 'room2',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # success with building or classroom exist but not both
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room2',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()

    # duplicate room, 403
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()


def test_get_studyroom_information():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    admin_token = get_token(client)
    user_token = get_token(client, 'stu', 'pass')

    room0 = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }
    room1 = {
        'buildingNumber': 'building2',
        'classRoomNumber': 'room2',
        'seatNumber': 2,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 18,
        'endTime': 22
    }

    resp = client.post('/studyroom', json = room0, 
                       headers = token2header(admin_token))
    resp = client.post('/studyroom', json = room1, 
                       headers = token2header(admin_token))

    room0_out = room0.copy()
    room1_out = room1.copy()
    room0_out['book'] = []
    room0_out['id'] = 0
    room1_out['book'] = []
    room1_out['id'] = 1

    # no auth token, 422
    resp = client.get('/studyroom/0')
    assert resp.status_code == 422, resp.json()

    # use admin token, get data should same
    resp = client.get('/studyroom/0', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == room0_out
    resp = client.get('/studyroom/1', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == room1_out

    # id not exist, 403
    resp = client.get('/studyroom/2', headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # id not int, 422
    resp = client.get('/studyroom/hahaha', headers = token2header(admin_token))
    assert resp.status_code == 422, resp.json()

    # use user token, should same
    resp = client.get('/studyroom/0', headers = token2header(user_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == room0_out
    resp = client.get('/studyroom/1', headers = token2header(user_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == room1_out


def test_get_all_studyroom_information():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    admin_token = get_token(client)
    user_token = get_token(client, 'stu', 'pass')

    rooms = [
        {
            'buildingNumber': 'building1',
            'classRoomNumber': 'room1',
            'seatNumber': 1,
            'startDate': 20000,
            'endDate': 20010,
            'startTime': 8,
            'endTime': 20
        },
        {
            'buildingNumber': 'building2',
            'classRoomNumber': 'room2',
            'seatNumber': 2,
            'startDate': 20000,
            'endDate': 20010,
            'startTime': 18,
            'endTime': 22
        },
        {
            'buildingNumber': 'building1',
            'classRoomNumber': 'room2',
            'seatNumber': 10,
            'startDate': 20000,
            'endDate': 20010,
            'startTime': 6,
            'endTime': 23
        },
    ]
    rooms_out = [x.copy() for x in rooms]
    for num, room in enumerate(rooms_out):
        room['book'] = []
        room['id'] = num
    rooms_current = []

    # without auth, 422
    resp = client.get('/studyroom')
    assert resp.status_code == 422, resp.json()

    # all auth can get result
    resp = client.get('/studyroom', headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == rooms_current
    resp = client.get('/studyroom', headers = token2header(user_token))
    assert resp.status_code == 200, resp.json()
    assert resp.json() == rooms_current

    # add room and check
    for room, room_out in zip(rooms, rooms_out):
        resp = client.post('/studyroom', json = room,
                           headers = token2header(admin_token))
        assert resp.status_code == 200, resp.json()
        rooms_current.append(room_out)
        resp = client.get('/studyroom', headers = token2header(admin_token))
        assert resp.status_code == 200, resp.json()
        assert resp.json() == rooms_current
        resp = client.get('/studyroom', headers = token2header(user_token))
        assert resp.status_code == 200, resp.json()
        assert resp.json() == rooms_current


def test_modify_studyroom():
    reset_db()
    add_admin_account()
    add_student_account('stu', 'pass', '')
    admin_token = get_token(client)
    user_token = get_token(client, 'stu', 'pass')

    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building1',
        'classRoomNumber': 'room1',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))
    resp = client.post('/studyroom', json = {
        'buildingNumber': 'building2',
        'classRoomNumber': 'room2',
        'seatNumber': 1,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 8,
        'endTime': 20
    }, headers = token2header(admin_token))

    # change without auth token, 422
    resp = client.put('/studyroom/0', json = {
        'startTime': 6,
    })
    assert resp.status_code == 422, resp.json()

    # change with user token, 401
    resp = client.put('/studyroom/0', json = {
        'startTime': 6,
    }, headers = token2header(user_token))
    assert resp.status_code == 401, resp.json()

    # change with empty building or classroom, 403
    resp = client.put('/studyroom/0', json = {
        'buildingNumber': '',
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'classRoomNumber': '',
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # change not exist room, 403
    resp = client.put('/studyroom/200', json = {
        'classRoomNumber': '',
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # change to exist room name, 403
    resp = client.put('/studyroom/0', json = {
        'buildingNumber': 'building2',
        'classRoomNumber': 'room2',
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # only change endtime and time error
    resp = client.put('/studyroom/0', json = {
        'endTime': -1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'endTime': 30
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'endTime': 1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    # only change enddate and date error
    resp = client.put('/studyroom/0', json = {
        'endDate': -1
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'endDate': 300000
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()
    resp = client.put('/studyroom/0', json = {
        'endDate': 19000
    }, headers = token2header(admin_token))
    assert resp.status_code == 403, resp.json()

    # successfully change all field
    resp = client.put('/studyroom/0', json = {
        'buildingNumber': 'mod0',
        'classRoomNumber': 'mod0',
        'seatNumber': 2,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 10,
        'endTime': 22
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.get('/studyroom/0', 
                      headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = resp.json()
    del resp['book']
    assert resp == {
        'id': 0,
        'buildingNumber': 'mod0',
        'classRoomNumber': 'mod0',
        'seatNumber': 2,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 10,
        'endTime': 22
    }

    # successfully send change, although nothing really changed
    resp = client.put('/studyroom/0', json = {
        'buildingNumber': 'mod0',
        'classRoomNumber': 'mod0',
        'seatNumber': 2,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 10,
        'endTime': 22
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.get('/studyroom/0', 
                      headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = resp.json()
    del resp['book']
    assert resp == {
        'id': 0,
        'buildingNumber': 'mod0',
        'classRoomNumber': 'mod0',
        'seatNumber': 2,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 10,
        'endTime': 22
    }

    # change part of field
    resp = client.put('/studyroom/0', json = {
        'buildingNumber': 'building2',
        'seatNumber': 20,
        'endTime': 10
    }, headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = client.get('/studyroom/0', 
                      headers = token2header(admin_token))
    assert resp.status_code == 200, resp.json()
    resp = resp.json()
    del resp['book']
    assert resp == {
        'id': 0,
        'buildingNumber': 'building2',
        'classRoomNumber': 'mod0',
        'seatNumber': 20,
        'startDate': 20000,
        'endDate': 20010,
        'startTime': 10,
        'endTime': 10
    }
