from src.connections import DB
from src.utils.utils import read_config
import src.database.SQL_requests as sql


achievementsConfig = read_config('./configs/autoAchievementsConfig.json')


def getUserEventsCount(userId):
    userEvents = DB.execute(sql.selectEvents({"participantId": userId}), manyResults=True)
    completedEventsCount = 0
    for event in userEvents:
        if event['score'] is not None:
            completedEventsCount += 1
    return completedEventsCount


def getGottenAchievementLevel(userId, achievementId):
    userAchievements = DB.execute(sql.selectUserAchievementsByUserid, [userId], manyResults=True)
    gottenAchievementLevel = 0
    for userAchievement in userAchievements:
        if userAchievement['achievementid'] == achievementId:
            gottenAchievementLevel = userAchievement['level']
    return gottenAchievementLevel


def addAchievement(userId, achievementId, level):
    gottenAchievementLevel = getGottenAchievementLevel(userId, achievementId)
    if gottenAchievementLevel == 0:
        DB.execute(sql.insertUserAchievement, [userId, achievementId, level, None])
    elif gottenAchievementLevel != level:
        deleteAchievement(userId, achievementId)
        DB.execute(sql.insertUserAchievement, [userId, achievementId, level, None])


def deleteAchievement(userId, achievementId):
    try:
        DB.execute(sql.deleteUserAchievementByUserIdAchievementId, [userId, achievementId])
    except:
        pass


# -----------------
def checkAchievementEventsCount(user):
    achievementId = achievementsConfig['countEventsAchievementId']
    userId = user['id']

    eventsCount = getUserEventsCount(userId)
    if eventsCount >= 50:
        addAchievement(userId, achievementId, 5)
    elif eventsCount >= 40:
        addAchievement(userId, achievementId, 4)
    elif eventsCount >= 30:
        addAchievement(userId, achievementId, 3)
    elif eventsCount >= 20:
        addAchievement(userId, achievementId, 2)
    elif eventsCount >= 10:
        addAchievement(userId, achievementId, 1)
    else:
        deleteAchievement(userId, achievementId)


def checkAchievementAllPlaces(user):
    achievementId = achievementsConfig['allPlacesAchievementId']
    userId = user['id']

    hasPlaces = DB.execute(sql.selectUserParticipationPlaces, [userId], manyResults=True)
    hasPlaces = set(map(lambda place: place['placeid'], hasPlaces))
    allPlaces = DB.execute(sql.selectAllPlaces, manyResults=True)
    allPlaces = set(map(lambda place: place['id'], allPlaces))

    hasNotPlaces = allPlaces - hasPlaces
    firstSetElement = None
    for firstSetElement in hasNotPlaces:  # get first element in set
        break

    if len(hasNotPlaces) == 0:
        addAchievement(userId, achievementId, 2)
    elif len(hasNotPlaces) == 1 and firstSetElement == achievementsConfig['extraPlaceId']:
        addAchievement(userId, achievementId, 1)
    else:
        deleteAchievement(userId, achievementId)


if __name__ == '__main__':
    users = DB.execute(sql.selectUsersByFilters({}), manyResults=True)
    for user in users:
        checkAchievementEventsCount(user)
        checkAchievementAllPlaces(user)
