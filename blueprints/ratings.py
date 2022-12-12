from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *

app = Blueprint('ratings', __name__)


@app.route("")
def getRatings():
    resp = DB.execute(sql.selectRatings, manyResults=True)
    notNoneRatings = []
    noneRatings = []
    for rating in resp:
        if rating['rating'] is None:
            rating['rating'] = 0
            noneRatings.append(rating)
        else:
            notNoneRatings.append(rating)

    return jsonResponse({'ratings': notNoneRatings + noneRatings})
