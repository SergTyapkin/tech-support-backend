------- Users data -------
CREATE TABLE IF NOT EXISTS users (
    id                 SERIAL PRIMARY KEY,
    password           TEXT NOT NULL,
    email              TEXT DEFAULT NULL UNIQUE,
    name               TEXT DEFAULT NULL,
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

------ Positions data -------
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
    placeId        SERIAL NOT NULL REFERENCES places(id) ON DELETE SET NULL,
    date           DATE NOT NULL,
    timeStart      TIME NOT NULL,
    timeEnd        TIME NOT NULL,
    eventTimeStart TIME DEFAULT NULL,
    eventTimeEnd   TIME DEFAULT NULL,
    authorId       SERIAL NOT NULL REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS people_needs (
    id             SERIAL PRIMARY KEY,
    eventId        SERIAL NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    positionId     SERIAL NOT NULL REFERENCES positions(id) ON DELETE SET NULL,
    count          INT NOT NULL
);

CREATE TABLE IF NOT EXISTS participations (
    id             SERIAL PRIMARY KEY,
    eventId        SERIAL NOT NULL REFERENCES events(id) ON DELETE SET NULL,
    userId         SERIAL NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    positionId     SERIAL NOT NULL REFERENCES positions(id) ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS images (
    id             SERIAL PRIMARY KEY,
    author         SERIAL REFERENCES users(id) ON DELETE SET NULL,
    type           TEXT NOT NULL,
    bytes          BYTEA
);


CREATE TABLE IF NOT EXISTS secretCodes (
    id             SERIAL PRIMARY KEY,
    userId         SERIAL REFERENCES users(id) ON DELETE CASCADE,
    code           TEXT NOT NULL UNIQUE,
    type           TEXT NOT NULL,
    expires        TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (userId, type)
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
            avatarImageId SERIAL REFERENCES images(id) ON DELETE SET NULL;
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
