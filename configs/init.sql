------- Users data -------
CREATE TABLE IF NOT EXISTS users (
    id                 SERIAL PRIMARY KEY,
    password           TEXT NOT NULL,
    telegram           TEXT DEFAULT NULL,
    email              TEXT NOT NULL UNIQUE,
    firstName          TEXT NOT NULL,
    secondName         TEXT DEFAULT NULL,
    thirdName          TEXT DEFAULT NULL,
    title              TEXT DEFAULT NULL,
    joinedDate         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    isConfirmedEmail   BOOLEAN DEFAULT FALSE,
    isConfirmedByAdmin BOOLEAN DEFAULT FALSE,
    avatarImageId      TEXT,

    canEditAchievements    BOOLEAN DEFAULT FALSE,
    canAssignAchievements  BOOLEAN DEFAULT FALSE,
    canConfirmNewUsers     BOOLEAN DEFAULT FALSE,
    canEditEvents          BOOLEAN DEFAULT FALSE,
    canEditUsersTitles     BOOLEAN DEFAULT FALSE,
    canEditUsersData       BOOLEAN DEFAULT FALSE,
    canEditParticipations  BOOLEAN DEFAULT FALSE,
    canEditDocs            BOOLEAN DEFAULT FALSE,
    canEditPlaces          BOOLEAN DEFAULT FALSE,
    canEditPositions       BOOLEAN DEFAULT FALSE,
    canExecuteSQL          BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS sessions (
    userId   SERIAL NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token    TEXT NOT NULL UNIQUE,
    expires  TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS secretCodes (
    id             SERIAL PRIMARY KEY,
    userId         INT REFERENCES users(id) ON DELETE CASCADE,
    code           TEXT NOT NULL UNIQUE,
    type           TEXT NOT NULL,
    expires        TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (userId, type)
);
------ Business data -------
CREATE TABLE IF NOT EXISTS positions (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS places (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL,
    description    TEXT DEFAULT NULL,
    placeId        INT REFERENCES places(id) ON DELETE SET NULL,
    date           DATE NOT NULL,
    timeStart      TIME NOT NULL,
    timeEnd        TIME NOT NULL,
    eventTimeStart TIME DEFAULT NULL,
    eventTimeEnd   TIME DEFAULT NULL,
    peopleNeeds    INT DEFAULT NULL,
    authorId       INT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS participations (
    id             SERIAL PRIMARY KEY,
    eventId        INT REFERENCES events(id) ON DELETE SET NULL,
    userId         SERIAL NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    positionId     INT REFERENCES positions(id) ON DELETE SET NULL,
    adminComment   TEXT DEFAULT NULL,
    score          FLOAT DEFAULT NULL,
    UNIQUE (userId, eventId)
);


CREATE TABLE IF NOT EXISTS images (
    id             SERIAL PRIMARY KEY,
    author         INT REFERENCES users(id) ON DELETE SET NULL,
    type           TEXT NOT NULL,
    bytes          BYTEA
);

CREATE TABLE IF NOT EXISTS achievements (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL,
    description    TEXT DEFAULT NULL,
    levels         INT NOT NULL,
    imageId        TEXT,
    special        BOOLEAN NOT NULL DEFAULT FALSE,
    authorId       INT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS usersAchievements (
    id             SERIAL PRIMARY KEY,
    userId         INT REFERENCES users(id) ON DELETE CASCADE,
    achievementId  INT REFERENCES achievements(id) ON DELETE CASCADE,
    level          INT NOT NULL DEFAULT 1,
    dateGotten     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    authorId       INT REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE (userId, achievementId, level)
);

CREATE TABLE IF NOT EXISTS docs (
    id             SERIAL PRIMARY KEY,
    title          TEXT NOT NULL,
    text           TEXT NOT NULL,
    placeId        INT REFERENCES places(id) ON DELETE SET NULL,
    positionId     INT REFERENCES positions(id) ON DELETE SET NULL,
    authorId       INT REFERENCES users(id) ON DELETE SET NULL,
    lastRedactorId INT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS periods (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    dateStart     DATE NOT NULL,
    dateEnd       DATE NOT NULL
);
----------
-- DO $$
-- BEGIN
--     IF NOT EXISTS(
--         SELECT column_name
--         FROM information_schema.columns
--         WHERE table_name = 'users'
--           AND column_name = 'avatarimageid'
--     ) THEN
--         ALTER TABLE users ADD COLUMN
--             avatarImageId INT REFERENCES images(id) ON DELETE SET NULL;
--         ALTER TABLE users ALTER COLUMN avatarImageId
--             DROP NOT NULL;
--         ALTER TABLE users ALTER COLUMN avatarImageId
--             SET DEFAULT NULL;
--     END IF;
-- END;
-- $$;


--------
CREATE OR REPLACE FUNCTION set_email_not_confirmed() RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.email != OLD.email THEN
        NEW.isConfirmedEmail = false;
    END IF;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS before_update ON users;
CREATE TRIGGER before_update
    BEFORE UPDATE ON users
    FOR EACH ROW
        EXECUTE PROCEDURE set_email_not_confirmed();

--------
CREATE OR REPLACE FUNCTION decrease_achievements_levels() RETURNS TRIGGER AS
$$
BEGIN
    UPDATE usersAchievements
    SET level = NEW.levels
    WHERE achievementId = NEW.id
    AND level > NEW.levels;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS after_update ON achievements;
CREATE TRIGGER after_update
    BEFORE UPDATE ON achievements
    FOR EACH ROW
        EXECUTE PROCEDURE decrease_achievements_levels();

--------
-- CREATE OR REPLACE FUNCTION delete_another_levels_of_achievement() RETURNS TRIGGER AS
-- $$
-- BEGIN
--     DELETE FROM usersAchievements
--     WHERE achievementId = NEW.achievementId
--       AND userId = NEW.userId;
--
--     RETURN NEW;
-- END
-- $$ LANGUAGE plpgsql;
--
-- DROP TRIGGER IF EXISTS before_insert ON usersAchievements;
-- CREATE TRIGGER before_insert
--     AFTER INSERT ON usersAchievements
--     FOR EACH ROW
--         EXECUTE PROCEDURE delete_another_levels_of_achievement();

--------
CREATE OR REPLACE FUNCTION max_achievement_level_limit() RETURNS TRIGGER AS
$$
DECLARE
    maxLevels INT;
BEGIN
    SELECT levels INTO maxLevels FROM achievements
    WHERE id = NEW.achievementId;

    IF NEW.level < 1 THEN
        NEW.level = 1;
    END IF;
    IF NEW.level > maxLevels THEN
        NEW.level = maxLevels;
    END IF;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS before_insert ON usersAchievements;
CREATE TRIGGER before_insert
    BEFORE UPDATE ON usersAchievements
    FOR EACH ROW
        EXECUTE PROCEDURE max_achievement_level_limit();
