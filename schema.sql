
-- users
CREATE TABLE Users (
    userid SERIAL PRIMARY KEY NOT NULL,
    username VARCHAR(32) NOT NULL,
    bio TEXT,
    email VARCHAR(256) NOT NULL,
    passhash VARCHAR(256) NOT NULL,
    salt VARCHAR(256) NOT NULL,
    registered TIMESTAMP NOT NULL
);

-- msgs
CREATE TABLE Msgs (
    msgid SERIAL PRIMARY KEY NOT NULL,
    author INTEGER NOT NULL,
    contents VARCHAR(256) NOT NULL,
    link VARCHAR(256),
    postdate TIMESTAMP NOT NULL,
    reply INTEGER,
    FOREIGN KEY (author) REFERENCES Users(userid) ON DELETE CASCADE,
    FOREIGN KEY (reply) REFERENCES Msgs(msgid) ON DELETE SET NULL
);

-- tags
CREATE TABLE Tags (
    tagid SERIAL PRIMARY KEY NOT NULL,
    tagname VARCHAR(32) NOT NULL
);

-- msg_tag
CREATE TABLE MsgTag (
    msgtagid SERIAL PRIMARY KEY NOT NULL,
    msg INTEGER NOT NULL,
    tag INTEGER NOT NULL,
    FOREIGN KEY (msg) REFERENCES Msgs(msgid) ON DELETE CASCADE,
    FOREIGN KEY (tag) REFERENCES Tags(tagid) ON DELETE CASCADE
);

-- likes
CREATE TABLE Likes (
    likeid SERIAL PRIMARY KEY NOT NULL,
    msg INTEGER NOT NULL,
    likeuser INTEGER NOT NULL,
    FOREIGN KEY (msg) REFERENCES Msgs(msgid) ON DELETE CASCADE,
    FOREIGN KEY (likeuser) REFERENCES Users(userid) ON DELETE CASCADE
);

-- follows
CREATE TABLE Follows (
    followid SERIAL PRIMARY KEY NOT NULL,
    follower INTEGER NOT NULL,
    followed INTEGER NOT NULL,
    FOREIGN KEY (follower) REFERENCES Users(userid) ON DELETE CASCADE,
    FOREIGN KEY (followed) REFERENCES Users(userid) ON DELETE CASCADE
);

-- user_reports
CREATE TABLE UserReports (
    reportid SERIAL PRIMARY KEY NOT NULL,
    reported_by INTEGER NOT NULL,
    user_reported INTEGER NOT NULL,
    reason VARCHAR(128) NOT NULL,
    FOREIGN KEY (reported_by) REFERENCES Users(userid) ON DELETE NO ACTION,
    FOREIGN KEY (user_reported) REFERENCES Users(userid) ON DELETE CASCADE
);

-- msg_reports
CREATE TABLE MsgReports (
    reportid SERIAL PRIMARY KEY NOT NULL,
    reported_by INTEGER NOT NULL,
    msg_reported INTEGER NOT NULL,
    reason VARCHAR(128) NOT NULL,
    postdate TIMESTAMP NOT NULL,
    FOREIGN KEY (reported_by) REFERENCES Users(userid) ON DELETE NO ACTION,
    FOREIGN KEY (msg_reported) REFERENCES Msgs(msgid) ON DELETE CASCADE
);

-- indexes
CREATE INDEX msgs_from_user_idx ON Msgs (author);
CREATE INDEX followeds_from_user_idx ON Follows (follower);
CREATE INDEX likes_from_msg_idx ON Likes (msg);
CREATE UNIQUE INDEX tags_from_msg_idx ON MsgTag (msg);
CREATE UNIQUE INDEX msgs_from_tag_idx ON MsgTag (tag);

-- generate feed:
-- SELECT m.msgid, m.author, m.contents, m.link, m.postdate, m.reply, u.username, COUNT FROM follows f JOIN msgs m ON (m.author = f.followed) JOIN users u ON (u.userid = m.author) WHERE f.follower = %USER_ID% AND m.msgid <= %MSG_ID% ORDER BY m.postdate DESC LIMIT 25;
