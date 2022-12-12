# -----------------------
# -- Default user part --
# -----------------------
_userColumns = "users.id, name, email, isAdmin, joinedDate, isConfirmedEmail, isConfirmedByAdmin, avatarImageId"
# ----- INSERTS -----
insertUser = \
    "INSERT INTO users (password, avatarImageId, email, name) " \
    "VALUES (%s, NULL, %s, %s) " \
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
    f"SELECT id, name, isAdmin, joinedDate, avatarImageId FROM users " \
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
    "SELECT users.id, name, joineddate, avatarImageId FROM users " \
    "JOIN secretCodes ON secretCodes.userId = users.id " \
    "WHERE email = %s AND " \
    "code = %s AND " \
    "type = %s AND " \
    "expires > NOW()"

# ----- UPDATES -----
updateUserById = \
    "UPDATE users SET " \
    "name = %s, " \
    "email = %s, " \
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
    "INSERT INTO events (name, description, placeId, date, timeStart, timeEnd, eventTimeStart, eventTimeEnd, authorId) " \
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertPeopleNeeds = \
    "INSERT INTO people_needs (eventId, positionId, count) " \
    "VALUES (%s, %s, %s) " \
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


# ----- SELECTS -----
def selectEvents(filters):
    type = 'next'
    if 'type' in filters:
        type = filters.type

    typeStr = "NULL = NULL "
    if type == 'next':
        typeStr = "date > NOW()"
    elif type == 'past':
        typeStr = "date <= NOW()"

    participationJoin = ""
    participationWhere = ""
    if 'participantId' in filters:
        participationJoin = "JOIN participations p ON p.eventId = event.id "
        participationWhere = "WHERE p.userId = %s "

    return \
        "SELECT * FROM events " \
        "JOIN places ON events.placeId = place.id " \
        "JOIN users ON events.authorId = users.id " + \
        participationJoin + \
        "WHERE " + \
        ("date = %s AND " if 'date' in filters else "") + \
        ("placeId = %s AND " if 'placeId' in filters else "") + \
        participationWhere + typeStr


selectEventById = \
    "SELECT * FROM events " \
    "JOIN users ON events.authorId = users.id " \
    "JOIN places ON events.placeId = places.id " \
    "WHERE events.id = %s"

selectAllPositions = \
    "SELECT * FROM positions"
selectPositionById = \
    "SELECT * FROM positions " \
    "WHERE id = %s"

selectAllPlaces = \
    "SELECT * FROM places"
selectPLaceById = \
    "SELECT * FROM places " \
    "WHERE id = %s"

selectRatings = \
    "SELECT count(participations.id) as rating, users.id, users.name " \
    "FROM users " \
    "LEFT JOIN participations ON participations.userId = users.id " \
    "WHERE isConfirmedEmail = True AND isConfirmedByAdmin = True " \
    "GROUP BY users.id " \
    "ORDER BY rating DESC"

selectPeopleNeedsByEventId = \
    "SELECT people_needs.*, name FROM people_needs " \
    "JOIN positions ON people_needs.positionid = positions.id " \
    "WHERE eventId = %s"

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
    "eventTimeEnd = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserConfirmationByAdminById = \
    "UPDATE users SET " \
    "isConfirmedByAdmin = %s " \
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

updatePeopleneedsCountByEventidPositionid = \
    "UPDATE people_needs SET " \
    "count = %s " \
    "WHERE eventId = %s AND positionId = %s " \
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

deletePeopleNeedsByEventId = \
    "DELETE FROM people_needs " \
    "WHERE eventId = %s"

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
