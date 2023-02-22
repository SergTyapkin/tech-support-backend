# -----------------------
# -- Default user part --
# -----------------------
_userColumns = "users.id, users.firstName, users.secondName, users.thirdName, users.email, users.telegram, users.title, users.isAdmin, users.joinedDate, users.isConfirmedEmail, users.isConfirmedByAdmin, users.avatarImageId"
# ----- INSERTS -----
insertUser = \
    "INSERT INTO users (password, avatarImageId, email, firstName, secondName, thirdName, telegram) " \
    "VALUES (%s, NULL, %s, %s, %s, %s, %s) " \
    f"RETURNING {_userColumns}"

insertSession = \
    "INSERT INTO sessions (userId, token, expires) " \
    "VALUES (%s, %s, NOW() + interval '1 hour' * %s) " \
    "RETURNING *"

insertSecretCode = \
    "INSERT INTO secretCodes (userId, code, type, expires) " \
    "VALUES (%s, %s, %s, NOW() + interval '1 hour' * %s)" \
    "RETURNING *"

# ----- SELECTS -----
selectUserByEmailPassword = \
    f"SELECT {_userColumns} FROM users " \
    "WHERE email = %s AND password = %s"

selectUserById = \
    f"SELECT {_userColumns} FROM users " \
    "WHERE id = %s"

selectAnotherUserById = \
    f"SELECT id, firstName, secondName, thirdName, isAdmin, joinedDate, avatarImageId, telegram, title FROM users " \
    "WHERE id = %s"

selectUserByEmail = \
    f"SELECT {_userColumns} FROM users " \
    "WHERE email = %s"

selectUserIdBySessionToken = \
    "SELECT userId FROM sessions " \
    "WHERE token = %s"

selectSessionByUserId = \
    "SELECT token, expires FROM sessions " \
    "WHERE userId = %s"

selectUserDataBySessionToken = \
    f"SELECT {_userColumns} FROM sessions " \
    "JOIN users ON sessions.userId = users.id " \
    "WHERE token = %s"

selectSecretCodeByUserIdType = \
    "SELECT * FROM secretCodes " \
    "WHERE userId = %s AND " \
    "type = %s AND " \
    "expires > NOW()"

selectUserByEmailCodeType = \
    "SELECT users.id, firstName, secondName, thirdName, joineddate, avatarImageId FROM users " \
    "JOIN secretCodes ON secretCodes.userId = users.id " \
    "WHERE email = %s AND " \
    "code = %s AND " \
    "type = %s AND " \
    "expires > NOW()"

def selectUsersByFilters(filters):
    return \
        f"SELECT {_userColumns} FROM users " \
        "WHERE " + \
        (f"isconfirmedByAdmin = {filters['confirmedByAdmin']} AND " if 'confirmedByAdmin' in filters else "") + \
        (f"isconfirmedEmail = {filters['confirmedEmail']} AND " if 'confirmedEmail' in filters else "") + \
        (f"LOWER(firstName  || ' ' || secondName) LIKE '%%{filters['search'].lower()}%%' AND " if 'search' in filters else "") + \
        "1 = 1 " \
        "ORDER BY firstName, secondName"

# ----- UPDATES -----
updateUserById = \
    "UPDATE users SET " \
    "firstName = %s, " \
    "secondName = %s, " \
    "thirdName = %s, " \
    "email = %s, " \
    "telegram = %s, " \
    "title = %s, " \
    "avatarImageId = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserPasswordByIdPassword = \
    "UPDATE users SET " \
    "password = %s " \
    "WHERE id = %s AND password = %s " \
    "RETURNING id"

updateUserPasswordBySecretcodeType = \
    "UPDATE users " \
    "SET password = %s " \
    "FROM secretCodes " \
    "WHERE secretCodes.userId = users.id AND " \
    "secretCodes.code = %s AND " \
    "secretCodes.type = %s " \
    "RETURNING users.*"

updateUserConfirmationBySecretcodeType = \
    "UPDATE users " \
    "SET isConfirmedEmail = True " \
    "FROM secretCodes " \
    "WHERE secretCodes.userId = users.id AND " \
    "secretCodes.code = %s AND " \
    "secretCodes.type = %s " \
    "RETURNING users.*"

# ----- DELETES -----
deleteExpiredSessions = \
    "DELETE FROM sessions " \
    "WHERE expires <= NOW()"

deleteUserById = \
    "DELETE FROM users " \
    "WHERE id = %s"

deleteSessionByToken = \
    "DELETE FROM sessions " \
    "WHERE token = %s"

deleteExpiredSecretCodes = \
    "DELETE FROM secretCodes " \
    "WHERE expires <= NOW()"

deleteSecretCodeByUseridCode = \
    "DELETE FROM secretCodes " \
    "WHERE userId = %s AND " \
    "code = %s"

# -----------------
# -- Events part --
# -----------------

# ----- INSERTS -----
insertEvent = \
    "INSERT INTO events (name, description, placeId, date, timeStart, timeEnd, eventTimeStart, eventTimeEnd, peopleNeeds, authorId) " \
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertParticipation = \
    "INSERT INTO participations (eventId, userId, positionId) " \
    "VALUES (%s, %s, %s) " \
    "RETURNING *"

insertPosition = \
    "INSERT INTO positions (name) " \
    "VALUES (%s) " \
    "RETURNING *"

insertPlace = \
    "INSERT INTO places (name) " \
    "VALUES (%s) " \
    "RETURNING *"

insertDoc = \
    "INSERT INTO docs (title, text, placeId, positionid, authorId, lastRedactorId) " \
    "VALUES (%s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

# ----- SELECTS -----
def selectEvents(filters):
    type = ''
    if 'type' in filters:
        type = filters['type']

    typeStr = "1 = 1 "
    if type == 'next':
        typeStr = "(date + timeend) > NOW() "
    elif type == 'past':
        typeStr = "(date + timeend) <= NOW() "

    participationSelect = ""
    participationJoin = ""
    participationWhere = ""
    if 'participantId' in filters:
        participationSelect = ", positions.name positionname, score "
        participationJoin = "JOIN participations p ON p.eventId = events.id LEFT JOIN positions ON p.positionId = positions.id "
        participationWhere = f"p.userId = {filters['participantId']} AND "

    return \
        f"SELECT events.*, (users.firstName  || ' ' || users.thirdName) as authorname, places.name placename {participationSelect}, (events.date + events.timeEnd >= NOW()) isnext FROM events " \
        "LEFT JOIN places ON events.placeId = places.id " \
        "LEFT JOIN users ON events.authorId = users.id " + \
        participationJoin + \
        "WHERE " + \
        (f"date = {filters['date']} AND " if 'date' in filters else "") + \
        (f"placeId = {filters['placeId']} AND " if 'placeId' in filters else "") + \
        (f"LOWER(events.name) LIKE '%%{filters['search'].lower()}%%' AND " if 'search' in filters else "") + \
        participationWhere + typeStr + \
        "ORDER BY events.date, events.timestart"


selectEventById = \
    "SELECT events.*, (users.firstName  || ' ' || users.thirdName) as authorname, users.telegram authortelegram, places.name placename, (events.date + events.timeEnd >= NOW()) isnext FROM events " \
    "LEFT JOIN users ON events.authorId = users.id " \
    "LEFT JOIN places ON events.placeId = places.id " \
    "WHERE events.id = %s"


def selectDocs(filters):
    return \
        f"SELECT docs.*, (users.firstName  || ' ' || users.thirdName) as authorname, ured.firstName lastredactorname, ured.telegram lastredactortelegram, places.name placename, positions.name positionname FROM docs " \
        "LEFT JOIN places ON docs.placeId = places.id " \
        "LEFT JOIN positions ON docs.positionId = positions.id " \
        "LEFT JOIN users ON docs.authorId = users.id " + \
        "LEFT JOIN users ured ON docs.lastRedactorId = ured.id " + \
        "WHERE " + \
        (f"placeId = {filters['placeId']} AND " if 'placeId' in filters else "") + \
        (f"positionId = {filters['positionId']} AND " if 'positionId' in filters else "") + \
        (f"LOWER(title) LIKE '%%{filters['search'].lower()}%%' AND " if 'search' in filters else "") + \
        "1 = 1 " \
        "ORDER BY title"


selectDocById = \
    "SELECT docs.*, (users.firstName  || ' ' || users.thirdName) as authorname, users.telegram authortelegram, places.name placename, positions.name positionname FROM docs " \
    "LEFT JOIN users ON docs.authorId = users.id " \
    "LEFT JOIN places ON docs.placeId = places.id " \
    "LEFT JOIN positions ON docs.positionId = positions.id " \
    "WHERE docs.id = %s"

selectAllPositions = \
    "SELECT * FROM positions " \
    "ORDER BY name"
selectPositionById = \
    "SELECT * FROM positions " \
    "WHERE id = %s"

selectAllPlaces = \
    "SELECT * FROM places " \
    "ORDER BY name"
selectPLaceById = \
    "SELECT * FROM places " \
    "WHERE id = %s"

selectParticipationById = \
    "SELECT * FROM participations " \
    "WHERE id = %s"

selectParticipationByUseridEventid = \
    "SELECT * FROM participations " \
    "WHERE userid = %s AND " \
    "eventid = %s"

selectParticipationsByEventid = \
    "SELECT participations.*, (users.firstName  || ' ' || users.thirdName) as username, users.avatarImageId userimageid, users.title usertitle, positions.name positionname FROM participations " \
    "JOIN users ON participations.userid = users.id " \
    "JOIN positions on participations.positionid = positions.id " \
    "JOIN events on participations.eventid = events.id " \
    "WHERE eventid = %s " \
    "ORDER BY events.date, events.timestart"

selectParticipationsCountByEventid = \
    "SELECT COUNT(*) count FROM participations " \
    "WHERE eventid = %s"

selectParticipationsUnvoted = \
    "SELECT participations.*, (users.firstName  || ' ' || users.thirdName) as username, users.avatarImageId userimageid, users.title usertitle, positions.name positionname, events.name eventname, events.date eventdate FROM participations " \
    "JOIN users ON participations.userid = users.id " \
    "JOIN positions on participations.positionid = positions.id " \
    "JOIN events on participations.eventid = events.id " \
    "WHERE score is NULL AND " \
    "(events.date + events.timestart) < NOW() " \
    "ORDER BY events.date, events.timestart"

selectRatings = \
    "SELECT sum(participations.score) as rating, users.id, (users.firstName  || ' ' || users.thirdName) as name, users.title, users.avatarimageid " \
    "FROM users " \
    "LEFT JOIN participations ON participations.userId = users.id " \
    "WHERE isConfirmedEmail = True AND isConfirmedByAdmin = True " \
    "GROUP BY users.id " \
    "ORDER BY rating DESC"

# ----- UPDATES -----
updateEventById = \
    "UPDATE events SET " \
    "name = %s, " \
    "description = %s, " \
    "placeId = %s, " \
    "date = %s, " \
    "timeStart = %s, " \
    "timeEnd = %s, " \
    "eventTimeStart = %s, " \
    "eventTimeEnd = %s, " \
    "peopleNeeds = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserConfirmationByAdminById = \
    "UPDATE users SET " \
    "isConfirmedByAdmin = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateParticipationById = \
    "UPDATE participations SET " \
    "positionId = %s, " \
    "score = %s, " \
    "adminComment = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updatePositionById = \
    "UPDATE positions SET " \
    "name = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updatePlaceById = \
    "UPDATE places SET " \
    "name = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateDocById = \
    "UPDATE docs SET " \
    "title = %s, " \
    "text = %s, " \
    "placeId = %s, " \
    "positionId = %s," \
    "lastredactorid = %s " \
    "WHERE id = %s " \
    "RETURNING *"

# ----- DELETES -----
deleteEventById = \
    "DELETE FROM events " \
    "WHERE id = %s"

deletePositionById = \
    "DELETE FROM positions " \
    "WHERE id = %s"

deletePlaceById = \
    "DELETE FROM places " \
    "WHERE id = %s"

deleteParticipationByEventidUserid = \
    "DELETE FROM participations " \
    "WHERE eventId = %s AND userId = %s"

deleteDocById = \
    "DELETE FROM docs " \
    "WHERE id = %s "

# --- IMAGES ---
insertImage = \
    "INSERT INTO images (author, type, bytes) " \
    "VALUES (%s, %s, %s) " \
    "RETURNING id, author, type"

selectImageById = \
    "SELECT * FROM images " \
    "WHERE id = %s"

deleteImageByIdAuthor = \
    "DELETE FROM images " \
    "WHERE id = %s AND author = %s"


# --- ACHIEVEMENTS ---
insertAchievement = \
    "INSERT INTO achievements (name, description, levels, imageId, authorId) " \
    "VALUES (%s, %s, %s, NULL, %s) " \
    "RETURNING *"

selectAchievementById = \
    "SELECT achievements.*, (users.firstName  || ' ' || users.thirdName) as authorname, users.telegram authortelegram FROM achievements " \
    "JOIN users ON achievements.authorid = users.id " \
    "WHERE achievements.id = %s"

# %s for name search must be provided as: '%{}%'.format(<YOUR_VAR>)
selectAchievementBySearchName = \
    f"SELECT * FROM achievements " \
    f"WHERE LOWER(name) LIKE %s " \
    f"ORDER BY name"

updateAchievementById = \
    "UPDATE achievements " \
    "SET name = %s, " \
    "description = %s, " \
    "levels = %s, " \
    "imageid = %s " \
    "WHERE id = %s " \
    "RETURNING *"

deleteAchievementById = \
    "DELETE FROM achievements " \
    "WHERE id = %s"


insertUserAchievement = \
    "INSERT INTO usersachievements (userId, achievementId, level, authorId) " \
    "VALUES (%s, %s, %s, %s) " \
    "RETURNING *"

selectUserAchievementsByUserid = \
    "SELECT usersachievements.*, achievements.levels, achievements.imageid FROM usersachievements " \
    "JOIN achievements on usersachievements.achievementid = achievements.id " \
    "WHERE userid = %s " \
    "ORDER BY dategotten"

updateUserAchievementLevelById = \
    "UPDATE usersachievements " \
    "SET level = %s," \
    "dateGotten = NOW() " \
    "WHERE id = %s " \
    "RETURNING *"

deleteUserAchievementById = \
    "DELETE FROM usersachievements " \
    "WHERE id = %s"

