from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *


app = Blueprint('periods', __name__)


@app.route("/all")
@login_required_return_id
def periodsGet(userId):
    periods = DB.execute(sql.selectAllPeriods, [], manyResults=True)
    list_times_to_str(periods)
    return jsonResponse({"periods": periods})


@app.route("")
@login_required_return_id
def periodGet(userId):
    try:
        req = request.args
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    period = DB.execute(sql.selectPeriodById, [id])
    times_to_str(period)
    return jsonResponse(period)


@app.route("/current")
@login_required_return_id
def currentPeriodGet(userId):
    period = DB.execute(sql.selectCurrentPeriod)
    times_to_str(period)
    return jsonResponse(period)
