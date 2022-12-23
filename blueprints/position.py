from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *


app = Blueprint('positions', __name__)


@app.route("/all")
@login_required_return_id
def positionsGet(userId):
    positions = DB.execute(sql.selectAllPositions, [], manyResults=True)
    return jsonResponse({"positions": positions})


@app.route("")
@login_required_return_id
def positionGet(userId):
    try:
        req = request.args
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    return jsonResponse(DB.execute(sql.selectPositionById, [id]))


@app.route("", methods=["POST"])
@login_required_admin
def positionCreate(userData):
    try:
        req = request.json
        name = req['name']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.insertPosition, [name])
    return jsonResponse(resp)


@app.route("", methods=["PUT"])
@login_required_admin
def positionUpdate(userData):
    try:
        req = request.json
        id = req['id']
        name = req['name']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.updatePositionById, [name, id])
    if resp is None:
        return jsonResponse("Должность не найдена", HTTP_NOT_FOUND)
    return jsonResponse(resp)


@app.route("", methods=["DELETE"])
@login_required_admin
def positionDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(sql.deletePositionById, [id])
    return jsonResponse("Должность удалена")
