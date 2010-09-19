
 
CREATE TABLE currentsessions (
    sessionid integer NOT NULL,
    username text,
    starttime text not null default current_timestamp,
    stoptime not null default current_timestamp
);

CREATE TABLE classes (
    classtype text NOT NULL
);

CREATE TABLE dataobjects (
    objectserialnumber integer NOT NULL,
    pickleddata blob NOT NULL,
    owner text NOT NULL,
    timestampcreated text not null default current_timestamp,
    classtype text,
    comments text
);

CREATE TABLE images (
    objectid text NOT NULL,
    imagename text NOT NULL,
    imagefiletype text NOT NULL,
    imagedata bytea NOT NULL
);