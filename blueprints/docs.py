from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *


app = Blueprint('docs', __name__)


@app.route("")
@login_required_return_id
def docsGet(userId):
    try:
        req = request.args
        id = req.get('id')

        placeId = req.get('placeId')
        positionId = req.get('positionId')
        search = req.get('search')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if id is not None:  # get single doc
        docData = DB.execute(sql.selectDocById, [id])
        if docData is None:
            return jsonResponse("Документ не найден", HTTP_NOT_FOUND)
        return jsonResponse(docData)

    # get docs list by filters
    docs = DB.execute(sql.selectDocs(req), [], manyResults=True)
    return jsonResponse({"docs": docs})


@app.route("", methods=["POST"])
@login_required_admin
def eventCreate(userData):
    try:
        req = request.json
        title = req['title']
        text = req['text']
        placeId = req['placeId']
        positionId = req['positionId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    doc = DB.execute(sql.insertDoc, [title, text, placeId, positionId, userData['id'], userData['id']])

    return jsonResponse(doc)


@app.route("", methods=["PUT"])
@login_required_admin
def eventUpdate(userData):
    try:
        req = request.json
        id = req['id']
        title = req.get('title')
        text = req.get('text')
        placeId = req.get('placeId')
        positionId = req.get('positionId')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    docData = DB.execute(sql.selectDocById, [id])
    if docData is None:
        return jsonResponse("Документ не найден", HTTP_NOT_FOUND)

    if title is None: title = docData['title']
    if text is None: text = docData['text']
    if placeId is None: placeId = docData['placeid']
    if positionId is None: positionId = docData['positionid']

    doc = DB.execute(sql.updateDocById, [title, text, placeId, positionId, userData['id'], id])

    return jsonResponse(doc)


@app.route("", methods=["DELETE"])
@login_required_admin
def eventDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(sql.deleteDocById, [id])
    return jsonResponse("Документ удален")
