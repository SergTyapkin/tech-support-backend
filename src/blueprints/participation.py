from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *


app = Blueprint('participations', __name__)


@app.route("/unvoted", methods=["GET"])
@login_and_can_edit_participations_required
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
        comment = req.get('comment')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if (userId != userData['id']) and (not userData['caneditparticipations']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    eventData = DB.execute(sql.selectEventById, [eventId])
    if eventData is None:
        jsonResponse("Такого события не существует", HTTP_NOT_FOUND)

    if (not eventData['isnext']) and (not userData['caneditparticipations']):
        jsonResponse("Событие уже закончилось, а вы - не админ", HTTP_DATA_CONFLICT)

    try:
        response = DB.execute(sql.insertParticipation, [eventId, userId, positionId, comment])
    except:
        return jsonResponse("Пользователь уже записан на это мероприятие", HTTP_DATA_CONFLICT)
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

    if (userId != userData['id']) and (not userData['caneditparticipations']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    eventData = DB.execute(sql.selectEventById, [eventId])
    if not eventData:
        return jsonResponse("Такого события не сущетвует", HTTP_NOT_FOUND)

    if (not eventData['isnext']) and (not userData['caneditparticipations']):
        return jsonResponse("Событие уже закончилось, а вы - не админ", HTTP_DATA_CONFLICT)

    DB.execute(sql.deleteParticipationByEventidUserid, [eventId, userId])
    return jsonResponse("Запись на событие удалена")


@app.route("/event", methods=["PUT"])
@login_and_can_edit_participations_required
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
    if score is None and "score" not in req: score = participationData['score']
    if comment is None: comment = participationData['admincomment']

    response = DB.execute(sql.updateParticipationById, [positionId, score, comment, id])
    return jsonResponse(response)


@app.route("/event/comment", methods=["PUT"])
@login_required
def updateSelfParticipationComment(userData):
    try:
        req = request.json
        id = req['id']
        comment = req.get('comment')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    participationData = DB.execute(sql.selectParticipationById, [id])
    if participationData is None:
        jsonResponse("Такого события не сущетвует", HTTP_NOT_FOUND)
    if participationData['userid'] != userData['id']:
        jsonResponse("Нет прав на редактирование чужого комментария", HTTP_NO_PERMISSIONS)

    if comment is None: comment = participationData['admincomment']

    response = DB.execute(sql.updateParticipationCommentById, [comment, id])
    return jsonResponse(response)


@app.route("/extract")
@login_required_return_id
def getExtractByAllParticipations(userId):
    period = DB.execute(sql.selectCurrentPeriod)
    if not period:
        return jsonResponse("Текущий период не найден", HTTP_NOT_FOUND)
    print(period)
    participationData = DB.execute(sql.selectParticipationsExtractByUserIdPeriod, [userId, period['datestart'], period['dateend']], manyResults=True)
    print(participationData)
    list_times_to_str(participationData)
    times_to_str(period)
    return jsonResponse({
        "participations": participationData,
        "dateStart": period['datestart'],
        "dateEnd": period['dateend'],
        "periodName": period['name'],
        "periodId": period['id'],
    })
