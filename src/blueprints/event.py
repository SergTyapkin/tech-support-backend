from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *


app = Blueprint('events', __name__)


@app.route("")
@login_required_return_id
def eventsGet(userId):
    try:
        req = request.args
        id = req.get('id')

        date = req.get('date')
        placeId = req.get('placeId')
        participantId = req.get('participantId')
        type = req.get('type')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if id is not None:  # get single event
        eventData = DB.execute(sql.selectEventById, [id])
        times_to_str(eventData)
        participations = DB.execute(sql.selectParticipationsByEventid, [eventData['id']], manyResults=True)
        eventData['participations'] = participations
        res = DB.execute(sql.selectParticipationByUseridEventid, [userId, id])
        eventData['isyouparticipate'] = bool(res)
        return jsonResponse(eventData)

    # get events list by filters
    events = DB.execute(sql.selectEvents(req), [], manyResults=True)
    list_times_to_str(events)
    for event in events:
        countRes = DB.execute(sql.selectParticipationsCountByEventid, [event['id']])
        event['participationscount'] = countRes.get('count') or 0
        event['peopleneeds'] = event['peopleneeds'] or 0
    return jsonResponse({"events": events})


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
        peopleNeeds = req.get('peopleNeeds')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if eventTimeEnd == '':
        eventTimeEnd = None
    if eventTimeStart == '':
        eventTimeStart = None

    event = DB.execute(sql.insertEvent, [name, description, placeId, date, timeStart, timeEnd, eventTimeStart, eventTimeEnd, peopleNeeds, userData['id']])
    times_to_str(event)
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
        peopleNeeds = req.get('peopleNeeds')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    eventData = DB.execute(sql.selectEventById, [id])
    if eventData is None:
        return jsonResponse("Событие не найдено", HTTP_NOT_FOUND)
    times_to_str(eventData)

    if name is None: name = eventData['name']
    if description is None: description = eventData['description']
    if placeId is None: placeId = eventData['placeid']
    if date is None: date = eventData['date']
    if timeStart is None: timeStart = eventData['timestart']
    if timeEnd is None: timeEnd = eventData['timeend']
    if eventTimeStart is None: eventTimeStart = eventData['eventtimestart']
    if eventTimeEnd is None: eventTimeEnd = eventData['eventtimeend']
    if peopleNeeds is None: peopleNeeds = eventData['peopleneeds']

    if eventTimeEnd == '':
        eventTimeEnd = None
    if eventTimeStart == '':
        eventTimeStart = None

    event = DB.execute(sql.updateEventById, [name, description, placeId, date, timeStart, timeEnd, eventTimeStart, eventTimeEnd, peopleNeeds, id])
    times_to_str(event)
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
