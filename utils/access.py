import hashlib
from functools import wraps

from flask import request

import database.SQL_requests as sql
from connections import DB
from constants import *
from utils.utils import *


def hash_sha256(auth_string: str) -> str:
    hash = hashlib.sha256(auth_string.encode()).hexdigest()
    return hash

def get_logined_userid():
    token = request.cookies.get('session_token')
    if not token:
        return ''
    session = DB.execute(sql.selectUserIdBySessionToken, [token])
    if len(session) == 0:
        return ''
    return session['userid']


def get_logined_user():
    token = request.cookies.get('session_token')
    if not token:
        return None
    result = DB.execute(sql.selectUserDataBySessionToken, [token])
    if len(result) == 0:
        return None
    return result


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        userData = get_logined_user()
        if not userData:
            return jsonResponse("Не авторизован", HTTP_INVALID_AUTH_DATA)
        return f(*args, userData, **kwargs)

    return wrapper


def login_and_email_confirmation_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        userData = get_logined_user()
        if not userData:
            return jsonResponse("Не авторизован", HTTP_INVALID_AUTH_DATA)
        if not userData['isconfirmed']:
            return jsonResponse("EMail не подтвержден", HTTP_NO_PERMISSIONS)
        return f(*args, userData, **kwargs)

    return wrapper


def login_required_return_id(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        userid = get_logined_userid()
        if not userid:
            return jsonResponse("Не авторизован", HTTP_INVALID_AUTH_DATA)
        return f(*args, userid, **kwargs)

    return wrapper


def login_required_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        userData = get_logined_user()
        if not userData:
            return jsonResponse("Не авторизован", HTTP_INVALID_AUTH_DATA)
        if not userData['isadmin']:
            return jsonResponse("Нет прав админа", HTTP_NO_PERMISSIONS)
        return f(*args, userData, **kwargs)

    return wrapper


def login_or_none(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        userData = get_logined_user()
        if not userData:
            userData = None
        return f(*args, userData, **kwargs)

    return wrapper


def login_or_none_return_id(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        userId = get_logined_userid()
        if not userId:
            userId = None
        return f(*args, userId, **kwargs)

    return wrapper
