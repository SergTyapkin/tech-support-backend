from flask import Blueprint

from connections import DB
from utils.access import *
from utils.utils import *


app = Blueprint('achievements', __name__)


@app.route("")
@login_required_return_id
def achievementsGet(userId_logined):
    try:
        req = request.args
        id = req.get('id')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if id is not None:  # get single achievement
        achievementData = DB.execute(sql.selectAchievementById, [id])
        return jsonResponse(achievementData)

    # get all achievements list
    achievements = DB.execute(sql.selectAllAchievements, [], manyResults=True)
    return jsonResponse({"achievements": achievements})


@app.route("", methods=["POST"])
@login_required_admin
def achievementCreate(userData):
    try:
        req = request.json
        name = req['name']
        description = req.get('description')
        levels = req['levels']
        imageId = req.get('imageId')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievement = DB.execute(sql.insertAchievement, [name, description, levels, imageId, userData['id']])
    return jsonResponse(achievement)


@app.route("", methods=["PUT"])
@login_required_admin
def achievementUpdate(userData):
    try:
        req = request.json
        id = req['id']
        name = req.get('name')
        description = req.get('description')
        levels = req.get('levels')
        imageId = req.get('imageId')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievementData = DB.execute(sql.selectAchievementById, [id])
    if achievementData is None:
        return jsonResponse("Достижение не найдено", HTTP_NOT_FOUND)

    if name is None: name = achievementData['name']
    if description is None: description = achievementData['description']
    if levels is None: levels = achievementData['levels']
    if imageId is None: imageId = achievementData['imageId']

    achievement = DB.execute(sql.updateAchievementById, [name, description, levels, imageId, id])
    return jsonResponse(achievement)


@app.route("", methods=["DELETE"])
@login_required_admin
def achievementDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(sql.deleteAchievementById, [id])
    return jsonResponse("Достижение удалено")


# ---- USERS ACHIEVEMENTS
@app.route("/user")
@login_required_return_id
def userAchievementsGet(userId_logined):
    try:
        req = request.args
        userId = req['userId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    userAchievements = DB.execute(sql.selectUserAchievementsByUserid, [userId], manyResults=True)
    list_times_to_str(userAchievements)
    return jsonResponse({"achievements": userAchievements})


@app.route("/user", methods=["POST"])
@login_required_admin
def userAchievementCreate(userData):
    try:
        req = request.json
        userId = req['userId']
        achievementId = req['achievementId']
        level = req['level']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievement = DB.execute(sql.insertUserAchievement, [userId, achievementId, level, userData['id']])
    return jsonResponse(achievement)


@app.route("/user", methods=["PUT"])
@login_required_admin
def userAchievementUpdate(userData):
    try:
        req = request.json
        id = req['id']
        level = req['level']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievement = DB.execute(sql.updateUserAchievementLevelById, [level, id])
    return jsonResponse(achievement)


@app.route("/user", methods=["DELETE"])
@login_required_admin
def userAchievementDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(sql.deleteUserAchievementById, [id])
    return jsonResponse("Достижение пользователя удалено")
