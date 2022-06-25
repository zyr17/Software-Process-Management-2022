import time
import redis
from dotenv import load_dotenv, find_dotenv
import os
from typing import Literal
import random
from typing import Optional


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
        self.account_prefix = 'account:'
        counter = self.conn.get('account:counter')
        if counter is None:
            self.conn.set('account:counter', 0)

    def _prefix(self, s: str, kind: str):
        if kind == 'account':
            return self.account_prefix + s
        else:
            raise ValueError(f"Unknown prefix kind {kind}")

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
        if info is None:
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
