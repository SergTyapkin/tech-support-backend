from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *


app = Blueprint('participations', __name__)

#
# @app.route("/event", methods=["POST"])
# @login_required
# def participateInEvent(userData):
#     try:
#         req = request.json
#         eventId = req['eventId']
#         userId = req['userId']
#         positionId = req['positionId']
#     except:
#         return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)
#
#     if (userId != userData['id']) and (not userData['isadmin']):
#         return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)
#
#     return jsonResponse(DB.execute(sql.insertParticipation, [eventId, userId, positionId]))
#

@app.route("/event", methods=["POST"])
@login_required
def participateInEvent(userData):
    try:
        req = request.json
        eventId = req['eventId']
        userId = req['userId']
        positionId = req['positionId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if (userId != userData['id']) and (not userData['isadmin']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    eventData = DB.execute(sql.selectEventById, [eventId])
    if eventData is None:
        jsonResponse("Такого события не сущетвует", HTTP_NOT_FOUND)

    if (not eventData['isnext']) and (not userData['isadmin']):
        jsonResponse("Событие уже закончилось, а вы - не админ", HTTP_DATA_CONFLICT)

    response = jsonResponse(DB.execute(sql.insertParticipation, [eventId, userId, positionId]))
    return jsonResponse(response)


@app.route("/event", methods=["DELETE"])
@login_required
def notParticipateInEvent(userData):
    try:
        req = request.json
        eventId = req['eventId']
        userId = req['userId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if (userId != userData['id']) and (not userData['isadmin']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    eventData = DB.execute(sql.selectEventById, [eventId])
    if eventData is None:
        jsonResponse("Такого события не сущетвует", HTTP_NOT_FOUND)

    if (not eventData['isnext']) and (not userData['isadmin']):
        jsonResponse("Событие уже закончилось, а вы - не админ", HTTP_DATA_CONFLICT)

    DB.execute(sql.deleteParticipationByEventidUserid, [eventId, userId])
    return jsonResponse("Запись на событие удалена")
