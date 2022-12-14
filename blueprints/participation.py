from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *


app = Blueprint('participations', __name__)


@app.route("/unvoted", methods=["GET"])
@login_required_admin
def getUnvotedParticipations(userData):
    resp = DB.execute(sql.selectParticipationsUnvoted, manyResults=True)
    list_times_to_str(resp)
    return jsonResponse({'participations': resp})


@app.route("/event", methods=["GET"])
@login_required
def getParticipationsByEvent(userData):
    try:
        req = request.json
        eventId = req['eventId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.selectParticipationsByEventid, [eventId], manyResults=True)
    if resp is None:
        return jsonResponse("Событие не найдено", HTTP_NOT_FOUND)

    return jsonResponse(resp)



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

    response = DB.execute(sql.insertParticipation, [eventId, userId, positionId])
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


@app.route("/event", methods=["PUT"])
@login_required_admin
def updateParticipationData(userData):
    try:
        req = request.json
        id = req['id']
        positionId = req.get('positionId')
        score = req.get('score')
        comment = req.get('comment')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    participationData = DB.execute(sql.selectParticipationById, [id])
    if participationData is None:
        jsonResponse("Такого события не сущетвует", HTTP_NOT_FOUND)

    if positionId is None: positionId = participationData['positionid']
    if score is None: score = participationData['score']
    if comment is None: comment = participationData['admincomment']

    response = DB.execute(sql.updateParticipationById, [positionId, score, comment, id])
    return jsonResponse(response)
