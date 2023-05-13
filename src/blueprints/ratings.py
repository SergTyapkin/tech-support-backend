from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *

app = Blueprint('ratings', __name__)


@app.route("")
def getRatings():
    resp = DB.execute(sql.selectRatings, manyResults=True)
    moreZeroRatings = []
    lowZeroRatings = []
    noneRatings = []
    for rating in resp:
        if rating['rating'] is None:
            rating['rating'] = 0
            noneRatings.append(rating)
        elif float(rating['rating']) > 0:
            moreZeroRatings.append(rating)
        else:
            lowZeroRatings.append(rating)

    return jsonResponse({'ratings': moreZeroRatings + noneRatings + lowZeroRatings})
