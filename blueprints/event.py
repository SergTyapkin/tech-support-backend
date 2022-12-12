from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *


app = Blueprint('events', __name__)


@app.route("/all")
@login_required_return_id
def eventsGet(userId):
    try:
        req = request.args
        date = req.get('date')
        placeId = req.get('placeId')
        participantId = req.get('participantId')
        type = req.get('type')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    return jsonResponse(DB.execute(sql.selectEvents(req), [], manyResults=True))


@app.route("")
@login_required_return_id
def eventGet(userId):
    try:
        req = request.args
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    eventData = DB.execute(sql.selectEventById, [id])
    peopleNeeds = DB.execute(sql.selectPeopleNeedsByEventId, [id], manyResults=True)
    for needing in peopleNeeds:
        needing = {
            'positionId': needing['positionId'],
            'name': needing['name'],
            'count': needing['count']
        }
    eventData['needPeople'] = peopleNeeds
    return jsonResponse(eventData)


@app.route("", methods=["POST"])
@login_required_admin
def eventCreate(userData):
    try:
        req = request.json
        name = req['name']
        description = req.get('description')
        placeId = req['placeId']
        date = req['date']
        timeStart = req['timeStart']
        timeEnd = req['timeEnd']
        eventTimeStart = req.get('eventTimeStart')
        eventTimeEnd = req.get('eventTimeEnd')
        needPeople = req['needPeople']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    event = DB.execute(sql.insertEvent, [name, description, placeId, date, timeStart, timeEnd, eventTimeStart, eventTimeEnd, userData.id])

    for needing in needPeople:
        resp = DB.execute(sql.insertPeopleNeeds, [event['id'], needing.positionId, needing.count])
    return jsonResponse(event)


@app.route("", methods=["PUT"])
@login_required_admin
def eventUpdate(userData):
    try:
        req = request.json
        id = req['id']
        name = req.get('name')
        description = req.get('description')
        placeId = req.get('placeId')
        date = req.get('date')
        timeStart = req.get('timeStart')
        timeEnd = req.get('timeEnd')
        eventTimeStart = req.get('eventTimeStart')
        eventTimeEnd = req.get('eventTimeEnd')
        needPeople = req.get('needPeople')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    event = DB.execute(sql.updateEventById, [name, id])
    if event is None:
        return jsonResponse("Событие не найдено", HTTP_NOT_FOUND)

    DB.execute(sql.deletePeopleNeedsByEventId, [event['id']])
    for needing in needPeople:
        resp = DB.execute(sql.insertPeopleNeeds, [event['id'], needing.positionId, needing.count])
    return jsonResponse(event)


@app.route("", methods=["DELETE"])
@login_required_admin
def eventDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(sql.deleteEventById, [id])
    return jsonResponse("Событие удалено")
