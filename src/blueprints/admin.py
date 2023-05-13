from flask import Blueprint

from src.utils.access import *
from src.constants import *
from src.utils.utils import *

app = Blueprint('admin', __name__)


@app.route("/sql", methods=["POST"])
@login_required_admin
def executeSQL(userData):
    try:
        req = request.json
        sqlText = req['sql']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    try:
        resp = DB.execute(sqlText, manyResults=True)
        list_times_to_str(resp)
        return jsonResponse({"response": resp})
    except Exception as err:
        return jsonResponse(str(err), HTTP_INTERNAL_ERROR)


@app.route("/user/confirmation", methods=["PUT"])
@login_required_admin
def setToUserAdminConfirmation(userData):
    try:
        req = request.json
        userId = req['userId']
        isConfirmed = req['isConfirmed']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(sql.updateUserConfirmationByAdminById, [isConfirmed, userId], manyResults=True)
    return jsonResponse(resp)
