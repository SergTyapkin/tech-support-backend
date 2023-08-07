import random
import uuid

from flask import Blueprint

from src.utils.access import *
from src.constants import *
from src.utils.detectGeoPositionUtils import detectGeoLocation
from src.utils.utils import *

from src import email_templates as emails

app = Blueprint('user', __name__)


def new_session(resp, browser, osName, geolocation, ip):
    # tokenResp = DB.execute(sql.selectSessionByUserId, [resp['id']])
    # if tokenResp:
    #     token = tokenResp['token']
    #     expires = tokenResp['expires']
    # else:

    token = str(uuid.uuid4())
    hoursAlive = 24 * 7  # 7 days
    session = DB.execute(sql.insertSession, [resp['id'], token, hoursAlive, ip, browser, osName, geolocation])
    expires = session['expires']

    DB.execute(sql.deleteExpiredSessions)

    res = jsonResponse(resp)
    res.set_cookie("session_token", token, expires=expires, httponly=True, samesite="lax")
    return res


def new_secret_code(userId, type, hours=1):
    DB.execute(sql.deleteExpiredSecretCodes)

    secretCode = DB.execute(sql.selectSecretCodeByUserIdType, [userId, type])
    if secretCode:
        code = secretCode['code']
        return code

    # create new
    if type == "login":
        random.seed()
        code = str(random.randint(1, 999999)).zfill(6)
    else:
        code = str(uuid.uuid4())

    DB.execute(sql.insertSecretCode, [userId, code, type, hours])

    return code


@app.route("/auth", methods=["POST"])
def userAuth():
    try:
        req = request.json
        email = req['email']
        password = req['password']
        clientBrowser = req.get('clientBrowser') or 'Unknown browser'
        clientOS = req.get('clientOS') or 'Unknown OS'
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)
    email = email.strip().lower()
    password = hash_sha256(password)

    resp = DB.execute(sql.selectUserByEmailPassword, [email, password])
    if not resp:
        return jsonResponse("Неверные email или пароль", HTTP_INVALID_AUTH_DATA)

    return new_session(resp, clientBrowser, clientOS, detectGeoLocation(), request.environ['IP_ADDRESS'])


@app.route("/session", methods=["DELETE"])
@login_required
def userSessionDelete(userData):
    try:
        DB.execute(sql.deleteSessionByToken, [userData['session_token']])
    except:
        return jsonResponse("Сессия не удалена", HTTP_INTERNAL_ERROR)

    res = jsonResponse("Вы вышли из аккаунта")
    res.set_cookie("session_token", "", max_age=-1, httponly=True, samesite="none", secure=True)
    return res


@app.route("/sessions/another", methods=["DELETE"])
@login_required
def userAnotherSessionsDelete(userData):
    try:
        DB.execute(sql.deleteAllUserSessionsWithout, [userData['id'], userData['session_token']])
    except:
        return jsonResponse("Сессия не удалена", HTTP_INTERNAL_ERROR)

    res = jsonResponse("Вы вышли из аккаунта")
    return res


@app.route("/sessions/all")
@login_required
def getAllUserSessions(userData):
    try:
        sessions = DB.execute(sql.selectAllUserSessions, [userData['id']], manyResults=True)
    except:
        return jsonResponse("Не удалось получить список сессий", HTTP_INTERNAL_ERROR)

    for session in sessions:
        times_to_str(session)
        if session['token'] == userData['session_token']:
            session['isCurrent'] = True
        else:
            session['isCurrent'] = False
        del session['token']
    return jsonResponse({'sessions': sessions})


@app.route("")
@login_or_none
def userGet(userData):
    try:
        req = request.args
        userId = req.get('id')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    def addRatingsData(userData):
        res = DB.execute(sql.selectRatings, [], manyResults=True)
        positionDecrease = 0
        for idx, rating in enumerate(res):
            if rating['rating'] is None:
                positionDecrease += 1

            if int(rating['id']) == int(userData['id']):
                userData['rating'] = rating['rating'] or 0
                userData['position'] = idx + 1 - positionDecrease
                return
        userData['rating'] = 0
        userData['position'] = len(res)

    def addEvents(userData):
        allEvents = DB.execute(sql.selectEvents({"participantId": userData['id']}), manyResults=True)
        list_times_to_str(allEvents)
        resEvents = []
        for event in allEvents:
            if event["score"] is not None:
                resEvents.append({
                    "id": event["id"],
                    "name": event["name"],
                    "position": event["positionname"],
                    "score": event["score"],
                })
        userData['completedevents'] = resEvents

    if userId is None:  # return self user data
        if userData is None:
            return jsonResponse("Не авторизован", HTTP_INVALID_AUTH_DATA)
        addEvents(userData)
        addRatingsData(userData)
        return jsonResponse(userData)

    # get another user data
    userData = DB.execute(sql.selectAnotherUserById, [userId])
    if not userData:
        return jsonResponse("Пользователь не найден", HTTP_NOT_FOUND)
    addEvents(userData)
    addRatingsData(userData)
    return jsonResponse(userData)


@app.route("", methods=["POST"])
def userCreate():
    try:
        req = request.json
        firstName = req['firstName']
        secondName = req['secondName']
        thirdName = req['thirdName']
        password = req['password']
        email = req['email']
        telegram = req.get('telegram')
        clientBrowser = req.get('clientBrowser') or 'Unknown browser'
        clientOS = req.get('clientOS') or 'Unknown OS'
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)
    email = email.strip().lower()
    firstName = firstName.strip()
    secondName = secondName.strip()
    thirdName = thirdName.strip()
    telegram = telegram.strip(' @').lower()

    password = hash_sha256(password)

    try:
        resp = DB.execute(sql.insertUser, [password, email, firstName, secondName, thirdName, telegram])
    except:
        return jsonResponse("Имя пользователя или email заняты", HTTP_DATA_CONFLICT)

    return new_session(resp, clientBrowser, clientOS, detectGeoLocation(), request.environ['IP_ADDRESS'])


@app.route("", methods=["PUT"])
@login_required
def userUpdate(userData):
    try:
        req = request.json
        userId = req['userId']
        firstName = req.get('firstName')
        secondName = req.get('secondName')
        thirdName = req.get('thirdName')
        email = req.get('email')
        telegram = req.get('telegram')
        title = req.get('title')
        avatarImageId = req.get('avatarImageId')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if userData['id'] != userId:
        if not (userData['canedituserstitles'] or userData['caneditusersdata']):
            return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)
        userData = DB.execute(sql.selectUserById, [userId])
    elif (not userData['canedituserstitles']) and (title is not None):
        return jsonResponse("Изменять титул могут только админы", HTTP_NO_PERMISSIONS)

    if email: email = email.strip().lower()
    if telegram: telegram = telegram.strip(' @').lower()
    if firstName: firstName = firstName.strip()
    if secondName: secondName = secondName.strip()
    if thirdName: thirdName = thirdName.strip()

    if firstName is None: firstName = userData['firstname']
    if secondName is None: secondName = userData['secondname']
    if thirdName is None: thirdName = userData['thirdname']
    if email is None: email = userData['email']
    if telegram is None: telegram = userData['telegram']
    if title is None: title = userData['title']
    if avatarImageId is None and 'avatarImageId' not in req: avatarImageId = userData['avatarimageid']

    try:
        resp = DB.execute(sql.updateUserById, [firstName, secondName, thirdName, email, telegram, title, avatarImageId, userId])
    except:
        return jsonResponse("Имя пользователя или email заняты", HTTP_DATA_CONFLICT)

    return jsonResponse(resp)


@app.route("", methods=["DELETE"])
@login_required
def userDelete(userData):
    try:
        req = request.json
        userId = req['userId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if (userData['id'] != userId) and (not userData['caneditusersdata']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    DB.execute(sql.deleteUserById, [userId])
    return jsonResponse("Пользователь удален")


@app.route("/password", methods=["PUT"])
@login_required_return_id
def userUpdatePassword(userId):
    try:
        req = request.json
        oldPassword = req['oldPassword']
        newPassword = req['newPassword']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    oldPassword = hash_sha256(oldPassword)
    newPassword = hash_sha256(newPassword)

    resp = DB.execute(sql.updateUserPasswordByIdPassword, [newPassword, userId, oldPassword])
    if len(resp) == 0:
        return jsonResponse("Старый пароль не такой", HTTP_INVALID_AUTH_DATA)

    return jsonResponse("Успешно обновлено")


@app.route("/password/restore", methods=["POST"])
def userRestorePasswordSendEmail():
    try:
        req = request.json
        email = req['email']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)
    email = email.strip().lower()

    userData = DB.execute(sql.selectUserByEmail, [email])
    if not userData:
        return jsonResponse("На этот email не зарегистрирован ни один аккаунт", HTTP_NOT_FOUND)

    secretCode = new_secret_code(userData['id'], "password")

    send_email(email,
               "Восстановление пароля на TechSupport",
               emails.restorePassword(f"/image/{userData['avatarimageid']}", userData['firstname'] + ' ' + userData['secondname'], secretCode))

    return jsonResponse("Ссылка для восстановления выслана на почту " + email)


@app.route("/password/restore", methods=["PUT"])
def userRestorePasswordChangePassword():
    try:
        req = request.json
        newPassword = req['newPassword']
        code = req['code']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    newPassword = hash_sha256(newPassword)

    userData = DB.execute(sql.updateUserPasswordBySecretcodeType, [newPassword, code, "password"])
    if not userData:
        return jsonResponse("Код восстановления не найден", HTTP_NOT_FOUND)

    DB.execute(sql.deleteSecretCodeByUseridCode, [userData['id'], code])
    return jsonResponse("Пароль изменен")


@app.route("/auth/code", methods=["POST"])
def userAuthByEmailCode():
    try:
        req = request.json
        email = req['email']
        code = req.get('code')
        clientBrowser = req.get('clientBrowser') or 'Unknown browser'
        clientOS = req.get('clientOS') or 'Unknown OS'
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)
    email = email.strip().lower()

    if code is None:
        userData = DB.execute(sql.selectUserByEmail, [email])
        if not userData:
            return jsonResponse("На этот email не зарегистрирован ни один аккаунт", HTTP_NOT_FOUND)
        if not userData['isconfirmedemail']:
            return jsonResponse("Этот email не подтвержден в соответствующем аккаунте", HTTP_NO_PERMISSIONS)

        secretCode = new_secret_code(userData['id'], "login")

        avatarImageId = userData['avatarimageid']
        send_email(email,
                   "Вход на TechSupport",
                   emails.loginByCode(f"/image/{avatarImageId}" if avatarImageId is not None else None,
                                      userData['firstname'] + ' ' + userData['secondname'], secretCode))

        return jsonResponse("Код выслан на почту " + email)

    resp = DB.execute(sql.selectUserByEmailCodeType, [email, code, "login"])
    if not resp:
        return jsonResponse("Неверные email или одноразовый код", HTTP_INVALID_AUTH_DATA)

    return new_session(resp, clientBrowser, clientOS, detectGeoLocation(), request.environ['IP_ADDRESS'])


@app.route("/email/confirm", methods=["POST"])
@login_required
def userConfirmEmailSendMessage(userData):
    email = userData['email']

    userData = DB.execute(sql.selectUserByEmail, [email])
    if not userData:
        return jsonResponse("На этот email не зарегистрирован ни один аккаунт", HTTP_NOT_FOUND)

    secretCode = new_secret_code(userData['id'], "email", hours=24)

    send_email(email,
               "Подтверждение регистрации на TechSupport",
               emails.confirmEmail(f"/image/{userData['avatarimageid']}", userData['firstname'] + ' ' + userData['secondname'], secretCode))

    return jsonResponse("Ссылка для подтверждения email выслана на почту " + email)


@app.route("/email/confirm", methods=["PUT"])
def userConfirmEmail():
    try:
        req = request.json
        code = req['code']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.updateUserConfirmationBySecretcodeType, [code, "email"])
    if not resp:
        return jsonResponse("Неверный одноразовый код", HTTP_INVALID_AUTH_DATA)

    return jsonResponse("Адрес email подтвержден")


@app.route("/all")
def usersGetAll():
    try:
        req = request.args
        search = req.get('search')
        confirmedByAdminState = req.get('confirmedByAdmin')
        confirmedEmailState = req.get('confirmedEmail')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.selectUsersByFilters(req), manyResults=True)
    return jsonResponse({'users': resp})
