from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *


app = Blueprint('periods', __name__)


@app.route("/all")
@login_required_return_id
def periodsGet(userId):
    periods = DB.execute(sql.selectAllPeriods, [], manyResults=True)
    return jsonResponse({"periods": periods})


@app.route("")
@login_required_return_id
def periodGet(userId):
    try:
        req = request.args
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    return jsonResponse(DB.execute(sql.selectPeriodById, [id]))
