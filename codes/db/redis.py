import time
import redis
from dotenv import load_dotenv, find_dotenv
import os
from typing import Literal
import random
from typing import Optional, List, Dict, Union


load_dotenv(find_dotenv())
redis_host = os.getenv('REDIS_HOST')


def singleton_warpper(clsObject):
    instance_key = '_singleton_instance'

    def inner(*args, **kwargs):
        if not hasattr(clsObject, instance_key):
            insObject = clsObject(*args, **kwargs)
            setattr(clsObject, instance_key, insObject)
        return getattr(clsObject, instance_key)
    return inner


@singleton_warpper
class RedisDB:

    def __init__(self):
        assert redis_host is not None, "REDIS_HOST is not found in env!"
        self.conn = redis.StrictRedis(redis_host, decode_responses = True)
        self.init()

    def reset(self):
        """
        clear all data and re-init data. used in unit tests.
        """
        self.conn.flushall()
        self.init()

    def init(self):
        """
        init functions. will call in init or all data has been removed.
        """
        self.init_account()
        self.init_studyroom()

    def init_account(self):
        """
        account related keys initialize.

        all account related keys start with `account:' meaning:
            "account:counter" int, registered account number
            "account:id:_" hash { id, name, password, stuNum, role }, account 
                information for id _.
            "account:name:_" id, to search id by account name
            "account:group:_" set, account id of specified group

        here if "account:counter" not in database, init counter.

        """
        counter = self.conn.get('account:counter')
        if counter is None:
            self.conn.set('account:counter', 0)

    def create_user(self, name: str, password: str, stuNum: str, 
                    role: Literal["admin", "user"]):
        """
        create a new user, will use account:counter as its id and increment
        counter. can create both admin and user, but use of API to register 
        admin account should be very careful.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if self.conn.get(f'account:name:{name}') is not None:
            return False, { 'error_msg': 'duplicate username' }

        if len(name) == 0 or len(password) == 0:
            return False, { 'error_msg': 'name or password empty' }

        id = int(self.conn.get('account:counter'))
        self.conn.incr('account:counter')
        self.conn.set(f'account:name:{name}', id)
        self.conn.hset(f'account:id:{id}', mapping = {
            'id': id,
            'name': name,
            'password': password,
            'stuNum': stuNum,
            'role': role
        })
        self.conn.sadd(f'account:group:{role}', id)
        return True, {}

    def generate_auth_token(self, name: str, password: str, 
                            valid_second: int = 3600):
        """
        input username and password, generate an auth_token which valid time
        is valid_second.

        key of authtoken X-Token is `authtoken:X-Token'. value is hash:
            time: expire unix time seconds
            id: corresponding user id for this token

        if success, return True, { id: int, name: str, auth: str, role: str, 
                                   expire: int }
        if fail, return False, { error_msg: str }
        """
        id = self.conn.get(f'account:name:{name}')
        if id is None:
            return False, { 'error_msg': 'username not exist' }
        id_pass = self.conn.hget(f'account:id:{id}', 'password')
        if id_pass != password:
            return False, { 'error_msg': 'password wrong' }
        allchar = 'zxcvbnmasdfghjklqwertyuiopZXCVBNMASDFGHJKLQWERTYUIOP'
        token = ''
        for i in range(64):
            token = token + allchar[random.randint(0, len(allchar) - 1)]
        expire_time = int(time.time()) + valid_second
        self.conn.hset(f'authtoken:{token}', mapping = {
            'time': expire_time,
            'id': id,
        })
        role = self.conn.hget(f'account:id:{id}', 'role')
        return True, { 'id': int(id), 'name': name, 'auth': token, 
                       'role': role, 'expire': expire_time }

    def check_auth_token(self, token: str):
        """
        validate auth token. if valid, return token user role and its id.

        if success, return True, { id: int, role: str }
        if fail, return False, { error_msg: str }
        """
        info = self.conn.hgetall(f'authtoken:{token}')
        if info is None or len(info) == 0:
            return False, { 'error_msg': 'unknown auth token' }
        if int(info['time']) < time.time():
            return False, { 'error_msg': 'auth token expired' }
        id = info['id']
        role = self.conn.hget(f'account:id:{id}', 'role')
        return True, { 'id': int(id), 'role': role }

    def check_password(self, id: int, password: str):
        """
        check password of specified id.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'account:id:{id}')) == 0:
            return False, { 'error_msg': 'account id not exist' }
        p = self.conn.hget(f'account:id:{id}', 'password')
        if password != p:
            return False, { 'error_msg': 'wrong current password' }
        return True, {}

    def modify_user(self, id: int, name: Optional[str], 
                    password: Optional[str], stuNum: Optional[str]):
        """
        modify user information.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'account:id:{id}')) == 0:
            return False, { 'error_msg': 'account id not exist' }
        info = self.conn.hgetall(f'account:id:{id}')
        if name is not None and name != info['name'] \
                and len(self.conn.keys(f'account:name:{name}')) != 0:
            return False, { 'error_msg': 'target name exists' }

        info = self.conn.hgetall(f'account:id:{id}')
        self.conn.delete(f'account:name:{info["name"]}')
        if name is not None:
            info['name'] = name
        if password is not None:
            info['password'] = password
        if stuNum is not None:
            info['stuNum'] = stuNum
        if len(info['name']) == 0 or len(info['password']) == 0:
            return False, { 'error_msg': 'name or password empty' }
        self.conn.hset(f'account:id:{id}', mapping = info)
        self.conn.set(f'account:name:{info["name"]}', id)

        return True, {}

    def get_user(self, id: int):
        """
        get information of one user

        if success, return True, { id: int, name: str, stuNum: str, role: str }
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'account:id:{id}')) == 0:
            return False, { 'error_msg': 'account id not exist' }

        info = self.conn.hgetall(f'account:id:{id}')
        return True, {
            'id': int(info['id']),
            'name': info['name'],
            'stuNum': info['stuNum'],
            'role': info['role'],
        }

    def get_all_users(self):
        """
        get all user information in a list, sorted with id

        if success, return True, [ users (refer to self.get_user) ... ]
        if fail, return False, { error_msg: str }
        """
        res = []
        keys = self.conn.keys('account:id:*')
        ids = [int(x.replace('account:id:', '')) for x in keys]
        for id in ids:
            resp, info = self.get_user(id)
            if not resp:
                return resp, info
            res.append(info)
        res.sort(key = lambda x: x['id'])
        return True, res

    def init_studyroom(self):
        """
        studyroom related keys initialize.

        all account related keys start with `room:' meaning:
            "room:counter" int, registered room number
            "room:id:_" hash { id: int, buildingNumber: str, 
                classRoomNumber: str, searNumber: int, startTime: int, 
                endTime: int }, room information for id _.
            "room:name:_:_" id, to search id by room buildingNum+roomNum

        here if "room:counter" not in database, init counter.
        """
        counter = self.conn.get('room:counter')
        if counter is None:
            self.conn.set('room:counter', 0) 

    def _studyroom_data_check(self, buildingNumber: str, classRoomNumber: str, 
                              seatNumber: int, startDate: int, endDate: int, 
                              startTime: int, endTime: int):
        """
        check if studyroom data is valid, used in create and modify.
        BASIC check, advanced rules such as seatNumber vs. current booking is
        not implemented here.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if len(buildingNumber) == 0 or len(classRoomNumber) == 0:
            return False, { 'error_msg': 'building or classroom number empty' }
        if ':' in buildingNumber or ':' in classRoomNumber:
            return False, { 'error_msg': 'building or classroom has colon' }
        if seatNumber <= 0:
            return False, { 'error_msg': 'sear number not positive' }
        if startTime < 0 or startTime > 23 or endTime < 0 or endTime > 23:
            return False, { 'error_msg': 'start or end time not in range' }
        if startTime > endTime:
            return False, { 'error_msg': 'start time later than end time' }
        if startDate < 0 or startDate > 99999 \
           or endDate < 0 or endDate > 99999:
            return False, { 'error_msg': 'start or end date not in range' }
        if startDate > endDate:
            return False, { 'error_msg': 'start date later than end date' }
        return True, {}

    def create_studyroom(self, buildingNumber: str, classRoomNumber: str, 
                         seatNumber: int, startDate: int, endDate: int, 
                         startTime: int, endTime: int):
        """
        create new studyroom. will use room:counter as its id and increment
        counter.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if self.conn.get(
                f'room:name:{buildingNumber}:{classRoomNumber}') is not None:
            return False, { 'error_msg': 'duplicate classroom' }
        checkres, info = self._studyroom_data_check(
            buildingNumber, classRoomNumber, seatNumber, startDate, endDate, 
            startTime, endTime
        )
        if not checkres:
            return False, info

        id = int(self.conn.get('room:counter'))
        self.conn.incr('room:counter')
        self.conn.set(f'room:name:{buildingNumber}:{classRoomNumber}', id)
        self.conn.hset(f'room:id:{id}', mapping = {
            'id': id,
            'buildingNumber': buildingNumber,
            'classRoomNumber': classRoomNumber,
            'seatNumber': seatNumber,
            'startDate': startDate,
            'endDate': endDate,
            'startTime': startTime,
            'endTime': endTime,
        })
        return True, {}

    def _studyroom_books_and_checkins(self, id: int):
        """
        get book and checkin number of studyroom, to count used seats

        if success, return True, [ { date: int, startTime: int, endTime: int, 
                                     type: Literal[booked, checkin] } ]
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'room:id:{id}')) == 0:
            return False, { 'error_msg': 'room id not exist' }

        booked_keys = self.conn.keys(f'book:*:{id}:*:*:*')
        checkin_keys = self.conn.keys(f'checkin:*:{id}:*:*:*')
        combine_keys = booked_keys + checkin_keys
        combine_keys = [x.split(':')[-3:] for x in combine_keys]
        booked_times = [[int(y) for y in x] for x in combine_keys]

        res: List[Dict[str, Union[int, str]]] = []
        for date, start, end in booked_times:
            res.append({
                'date': date,
                'startTime': start,
                'endTime': end,
                'type': 'booked'
            })
        res.sort(key = lambda x: x['date'] * 10000 
                                 + x['startTime'] * 100 + x['endTime'])
        return True, res

    def get_studyroom(self, id: int):
        """
        get studyroom information.

        if success, return True, {
            id: int,
            buildingNumber: str, 
            classRoomNumber: str, 
            searNumber: int, 
            startDate: int, 
            endDate: int,
            startTime: int, 
            endTime: int,
            book: [
                { date: int, startTime: int, endTime: int } ...
            ]
        } book contains current booking and checkin information of the room
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'room:id:{id}')) == 0:
            return False, { 'error_msg': 'room id not exist' }
        info = self.conn.hgetall(f'room:id:{id}')
        bookres, book = self._studyroom_books_and_checkins(id)
        if not bookres:
            return False, { 'error_msg': 'error in _studyroom_books' }
        res = {
            'id': int(info['id']),
            'buildingNumber': info['buildingNumber'],
            'classRoomNumber': info['classRoomNumber'],
            'seatNumber': int(info['seatNumber']),
            'startDate': int(info['startDate']),
            'endDate': int(info['endDate']),
            'startTime': int(info['startTime']),
            'endTime': int(info['endTime']),
            'book': book
        }
        return True, res

    def get_all_studyrooms(self):
        """
        get all room information in a list, sorted with id

        if success, return True, [ rooms (refer to self.get_studyroom) ... ]
        if fail, return False, { error_msg: str }
        """
        res = []
        keys = self.conn.keys('room:id:*')
        ids = [int(x.replace('room:id:', '')) for x in keys]
        for id in ids:
            resp, info = self.get_studyroom(id)
            if not resp:
                return resp, info
            res.append(info)
        res.sort(key = lambda x: x['id'])
        return True, res

    def modify_studyroom(
            self, id: int, buildingNumber: Optional[str], 
            classRoomNumber: Optional[str], seatNumber: Optional[int], 
            startDate: Optional[int], endDate: Optional[int],
            startTime: Optional[int], endTime: Optional[int]):
        """
        modify studyroom information. if seatNumber is modified, will check
        current available seat number not to be minus zero.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'room:id:{id}')) == 0:
            return False, { 'error_msg': 'room id not exist' }
        resp, info = self.get_studyroom(id)
        if not resp:
            return False, info
        if buildingNumber is not None and classRoomNumber is not None:
            if (info['buildingNumber'] != buildingNumber 
                    or info['classRoomNumber'] != classRoomNumber):
                key = f'room:name:{buildingNumber}:{classRoomNumber}'
                if len(self.conn.keys(key)) != 0:
                    return False, { 'error_message': 'duplicate room name' }
        if buildingNumber is None:
            buildingNumber = info['buildingNumber']
        if classRoomNumber is None:
            classRoomNumber = info['classRoomNumber']
        if seatNumber is None:
            seatNumber = int(info['seatNumber'])
        if startDate is None:
            startDate = int(info['startDate'])
        if endDate is None:
            endDate = int(info['endDate'])
        if startTime is None:
            startTime = int(info['startTime'])
        if endTime is None:
            endTime = int(info['endTime'])

        # check updated seat number can cover current booking
        booked_dict = { 0: 0 }  # put a zero as default min
        for b in info['book']:
            for t in range(b['startTime'], b['endTime'] + 1):
                idx = b['date'] * 100 + t
                if idx not in booked_dict:
                    booked_dict[idx] = 0
                booked_dict[idx] += 1
        current_max = max([v for k, v in booked_dict.items()])
        if seatNumber < current_max:
            return False, { 'error_msg': 'some seat has been booked, and '
                            'change of seat number will make empty seat be '
                            'minus' }
        # check updated startTime and endTime can cover current booking
        book_start = [x['startTime'] for x in info['book']]
        book_end = [x['endTime'] for x in info['book']]
        if len(info['book']) and (startTime > min(book_start) 
                                  or endTime < max(book_end)):
            return False, { 'error_msg': 'start time or end time not cover '
                            'all booking' }
        book_date = [x['date'] for x in info['book']]
        if len(info['book']) and (startDate > min(book_date)
                                  or endDate < max(book_date)):
            return False, { 'error_msg': 'start date or end date not cover '
                            'all booking' }

        checkres, checkinfo = self._studyroom_data_check(
            buildingNumber, classRoomNumber, seatNumber, startDate, endDate, 
            startTime, endTime
        )
        if not checkres:
            return False, checkinfo
        self.conn.delete(
            f'room:name:{info["buildingNumber"]}:{info["classRoomNumber"]}')
        self.conn.set(f'room:name:{buildingNumber}:{classRoomNumber}', id)
        self.conn.hset(f'room:id:{id}', mapping = {
            'id': id,
            'buildingNumber': buildingNumber,
            'classRoomNumber': classRoomNumber,
            'seatNumber': seatNumber,
            'startDate': startDate,
            'endDate': endDate,
            'startTime': startTime,
            'endTime': endTime,
        })
        return True, {}

    def book(self, userid: int, roomId: int, date: int, startTime: int, 
             endTime: int):
        """
        user request book for one seat. one book key will save as:
        book:{userid}:{roomId}:{date}:{startTime}:{endTime}
        value is book unix timestamp.

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'room:id:{roomId}')) == 0:
            return False, { 'error_msg': 'room id not found' }
        if len(self.conn.keys(f'account:id:{userid}')) == 0:
            return False, { 'error_msg': 'user id not found' }
        if len(self.conn.keys(f'book:{userid}:*')) > 0:
            return False, { 'error_msg': 'user has an active booking' }
        if startTime > endTime:
            return False, { 'error_msg': 'start time large than end time' }
        _, roominfo = self.get_studyroom(roomId)
        if date < roominfo['startDate'] or date > roominfo['endDate']:
            return False, { 'error_msg': 'date range not match' }
        booked_dict = {}  # count today's booked number for every time
        for one in roominfo['book']:
            if one['date'] == date:
                for t in range(one['startTime'], one['endTime'] + 1):
                    if t not in booked_dict:
                        booked_dict[t] = 0
                    booked_dict[t] += 1
        for t in range(startTime, endTime + 1):
            if t < roominfo['startTime'] or t > roominfo['endTime']:
                return False, { 'error_msg': 'time range not match' }
            if t in booked_dict and booked_dict[t] >= roominfo['seatNumber']:
                return False, { 'error_msg': 'not enough empty seat' }

        self.conn.set(f'book:{userid}:{roomId}:{date}:{startTime}:{endTime}',
                      int(time.time()))
        return True, {}

    def is_booked(self, userid: int):
        """
        check whether userid is booked now

        if success, return True, True|False
        if fail, return False, { error_msg: str }
        """
        if len(self.conn.keys(f'account:id:{userid}')) == 0:
            return False, { 'error_msg': 'account not exist' }
        return True, len(self.conn.keys(f'book:{userid}:*')) > 0

    def get_book(self, userid: int):
        """
        get book information of user.

        if success, return True, {
            roomId: int,
            buildingNumber: str,
            classRoomNumber: str,
            date: int,
            startTime: int,
            endTime: int,
            bookTimeStamp: int
        }
        if fail, return False, { error_msg: str }
        """
        resp, info = self.is_booked(userid)
        if not resp:
            return False, info
        if not info:
            return False, { 'error_msg': 'book not found' }
        key = self.conn.keys(f'book:{userid}:*')[0]
        booktime = self.conn.get(key)
        key = key.split(':')
        roomId, date, startTime, endTime = [int(x) for x in key[2:]]
        resp, info = self.get_studyroom(roomId)
        if not resp:
            return False, info
        res = {
            'roomId': roomId,
            'buildingNumber': info['buildingNumber'],
            'classRoomNumber': info['classRoomNumber'],
            'date': date,
            'startTime': startTime,
            'endTime': endTime,
            'bookTimeStamp': booktime
        }
        return True, res

    def pos_checkin(self, id: int, pos: str):
        """
        position checkin. pos is a string, if match `buildingNum:classRoomNum`,
        can checkin; otherwise return error.
        if checkin, key prefix book: will change to checkin:, and value will
        become a hash with { book: int, checkin: int }

        if success, return True, {}
        if fail, return False, { error_msg: str }
        """
        resp, info = self.get_book(id)
        if not resp:
            return False, info
        if pos != info['buildingNumber'] + ':' + info['classRoomNumber']:
            return False, { 'error_msg': 'position not match' }

        # checkin
        old_key = (f'book:{id}:{info["roomId"]}:{info["date"]}:'
                   f'{info["startTime"]}:{info["endTime"]}')
        new_key = (f'checkin:{id}:{info["roomId"]}:{info["date"]}:'
                   f'{info["startTime"]}:{info["endTime"]}')
        self.conn.delete(old_key)
        self.conn.hset(new_key, mapping = {
            'book': info['bookTimeStamp'],
            'checkin': int(time.time())
        })

        return True, {}

    def card_checkin(self, userid: int, roomid: int):
        """
        card checkin, admin should set roomid first, and get userid with
        slide.

        if success, return True, {
            userName: str,
            buildingNum: str,
            classRoomNum: str,
            startTime: int,
            endTime: int
        }
        if fail, return False, { error_msg: str }
        """
        resp, info = self.get_book(userid)
        if not resp:
            return False, info
        if roomid != info['roomId']:
            return False, {
                'error_msg': 'room wrong! you booked '
                f"{info['buildingNumber']} {info['classRoomNumber']}!"
            }

        # checkin
        old_key = (f'book:{userid}:{info["roomId"]}:{info["date"]}:'
                   f'{info["startTime"]}:{info["endTime"]}')
        new_key = (f'checkin:{userid}:{info["roomId"]}:{info["date"]}:'
                   f'{info["startTime"]}:{info["endTime"]}')
        self.conn.delete(old_key)
        self.conn.hset(new_key, mapping = {
            'book': info['bookTimeStamp'],
            'checkin': int(time.time())
        })
        resp, uinfo = self.get_user(userid)
        if not resp:
            return False, uinfo
        userName = uinfo['name']

        return True, {
            'userName': userName,
            'buildingNum': info['buildingNumber'],
            'classRoomNum': info['classRoomNumber'],
            'startTime': info['startTime'],
            'endTime': info['endTime']
        }
