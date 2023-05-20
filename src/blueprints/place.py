from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *


app = Blueprint('places', __name__)


@app.route("/all")
@login_required_return_id
def placesGet(userId):
    places = DB.execute(sql.selectAllPlaces, [], manyResults=True)
    return jsonResponse({"places": places})


@app.route("")
@login_required_return_id
def placeGet(userId):
    try:
        req = request.args
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    return jsonResponse(DB.execute(sql.selectPLaceById, [id]))


@app.route("", methods=["POST"])
@login_and_can_edit_places_required
def placeCreate(userData):
    try:
        req = request.json
        name = req['name']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.insertPlace, [name])
    return jsonResponse(resp)


@app.route("", methods=["PUT"])
@login_and_can_edit_places_required
def placeUpdate(userData):
    try:
        req = request.json
        id = req['id']
        name = req['name']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.updatePlaceById, [name, id])
    if resp is None:
        return jsonResponse("Место не найдено", HTTP_NOT_FOUND)
    return jsonResponse(resp)


@app.route("", methods=["DELETE"])
@login_and_can_edit_places_required
def placeDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(sql.deletePlaceById, [id])
    return jsonResponse("Место удалено")
