------- Users data -------
CREATE TABLE IF NOT EXISTS users (
    id                 SERIAL PRIMARY KEY,
    password           TEXT NOT NULL,
    telegram           TEXT DEFAULT NULL,
    email              TEXT NOT NULL UNIQUE,
    name               TEXT DEFAULT NULL,
    title              TEXT DEFAULT NULL,
    isAdmin            BOOLEAN DEFAULT FALSE,
    joinedDate         TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    isConfirmedEmail   BOOLEAN DEFAULT FALSE,
    isConfirmedByAdmin BOOLEAN DEFAULT FALSE
    -- avatarImageId    SERIAL -- will adds by ALTER in end
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
    imageId        INT REFERENCES images(id) ON DELETE SET NULL,
    authorId       INT REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS usersAchievements (
    id             SERIAL PRIMARY KEY,
    userId         INT REFERENCES users(id) ON DELETE CASCADE,
    achievementId  INT REFERENCES achievements(id) ON DELETE SET NULL,
    level          INT NOT NULL DEFAULT 1,
    dateGotten     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    authorId       INT REFERENCES users(id) ON DELETE SET NULL
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
----------
DO $$
BEGIN
    IF NOT EXISTS(
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'users'
          AND column_name = 'avatarimageid'
    ) THEN
        ALTER TABLE users ADD COLUMN
            avatarImageId INT REFERENCES images(id) ON DELETE SET NULL;
        ALTER TABLE users ALTER COLUMN avatarImageId
            DROP NOT NULL;
        ALTER TABLE users ALTER COLUMN avatarImageId
            SET DEFAULT NULL;
    END IF;
END;
$$;


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
