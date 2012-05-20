--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: -
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

--
-- Name: auth_lc_user(text, text, cidr); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION auth_lc_user(text, text, cidr) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
DECLARE
	session_seq_val int;
	valid boolean;
BEGIN
    select True into valid from authorizedUsers where username=$1 and password = $2; 
    if not FOUND then
	   RAISE NOTICE 'Invalid authorization against db.  Timestamp: %s.  Username "%", password "%", source ip %.', 
										CURRENT_TIMESTAMP, $1, $2, $3;
	   return -1;
	else
		update currentSessions set stoptime=now() where username=$1 and stoptime is null; -- NOTE this row locks all the rows for username! competing logins hang until one of them commits.  Interesting
		insert into currentSessions (sessionid, username, ipaddress) values (DEFAULT, $1, $3) returning sessionid into session_seq_val;
		RAISE NOTICE 'Successful authorization against db.  Timestamp: %s.  Username "%", password "%", source ip %.', 
										 CURRENT_TIMESTAMP, $1, $2, $3;
		return session_seq_val;
	end if;
	raise exception 'Should never arrive here.';
	return -99;
END;
$_$;


--
-- Name: FUNCTION auth_lc_user(text, text, cidr); Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON FUNCTION auth_lc_user(text, text, cidr) IS 'Used to authorize a user for logging in, and to clear all old sessions.';


--
-- Name: new_lc_user(text, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION new_lc_user(text, text, text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
DECLARE
    pending_row pending_registrations%ROWTYPE;
    reg_rowct int;
    authct int;
    email_notice text;
BEGIN
    select * into pending_row from pending_registrations where username=$1 and password=$2 order by inserted_timestamp desc limit 1;
    if not FOUND then
        raise exception 'No such pending registration: %, %.', $1, $2;
    end if;

    select count(*) into authct from authorizedusers where email=$3 or username=$1;
    if authct <> 0 then
        raise exception 'Trying to register previously registered username: %.', $1;
    end if;

    select count(*) into reg_rowct from pending_registrations where username=$1 and password=$2 and email=$3 and finished = False;
    if reg_rowct <= 0 then
       RAISE NOTICE 'reg_rowct == 0';
        --RAISE EXCEPTION 'Nonexistent or finished ID/password: %, %, %.', $1, $2, $3;                                                             
    elsif reg_rowct >= 2 then
        RAISE NOTICE 'Duplicate registration rows with same username and password.  Using most recent, %.',
                               pending_row.inserted_timestamp;
    else
        RAISE NOTICE 'Registering % % %.', $1, $2, $3;
    end if;

    insert into  authorizedusers (username, password, email) values ($1, $2, $3);
    update pending_registrations set finished = True where email = $3;
    email_notice := 'Successfully registered ' || $1 || ' at ' || $3 || '.';
    return email_notice;
END;

$_$;


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: authorizedusers; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE authorizedusers (
    username text NOT NULL,
    password text,
    timestamp_registered timestamp without time zone DEFAULT now(),
    email text,
    id integer NOT NULL,
    CONSTRAINT authorized_users_noblank CHECK ((char_length(username) >= 2))
);


--
-- Name: TABLE authorizedusers; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE authorizedusers IS 'This table has the usernames and passwords for people who can login to the LCFIT application.';


--
-- Name: authorizedusers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE authorizedusers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: authorizedusers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE authorizedusers_id_seq OWNED BY authorizedusers.id;


--
-- Name: classes; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE classes (
    classtype text NOT NULL
);


--
-- Name: TABLE classes; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE classes IS 'This table contains a list of valid classes that can be stored in the "dataobjects" table, and displayed in the LcList workspace.';


--
-- Name: currentsessions; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE currentsessions (
    sessionid integer NOT NULL,
    username text,
    starttime timestamp without time zone DEFAULT now() NOT NULL,
    stoptime timestamp without time zone,
    ipaddress inet
);


--
-- Name: TABLE currentsessions; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE currentsessions IS 'This table has an entry for all the sessions, with a key corresponding to a session id kept track of in modpython.  If a user has a session ID in their cookie that corresponds to a session id which has a non-null stoptime, that session is considered invalid and the user must log in again.  When a user logs in, all the previous stoptimes for that user are marked now() if they are null; when a user logs out the appropriate session stoptime is marked now().';


--
-- Name: currentsessions_sessionid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE currentsessions_sessionid_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: currentsessions_sessionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE currentsessions_sessionid_seq OWNED BY currentsessions.sessionid;


--
-- Name: dataobjects; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE dataobjects (
    objectserialnumber integer NOT NULL,
    pickleddata bytea NOT NULL,
    owner text NOT NULL,
    timestampcreated timestamp without time zone DEFAULT now() NOT NULL,
    classtype text,
    comments text
);


--
-- Name: TABLE dataobjects; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE dataobjects IS 'This table has the forecast objects stored, one per row.  "objectserialnumber" contains to the serial number given the object at creation.  "pickleddata" contains the pickled data from the python class instantiation.  "owner" refers to the username (in authorizedusers) who created the object.  "timestampcreated" is the timestamp when the object was inserted.  "classtype" contains the name of the class of the python object -- this is necessary in order to unpickle the data into the correct class.  "comments" is an arbitrary field for text from the user -- hopefully for them to reference the forecast later.';


--
-- Name: dataobjects_objectserialnumber_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE dataobjects_objectserialnumber_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: dataobjects_objectserialnumber_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE dataobjects_objectserialnumber_seq OWNED BY dataobjects.objectserialnumber;


--
-- Name: email_test; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE email_test (
    email text,
    username text
);


--
-- Name: images; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE images (
    objectid text NOT NULL,
    imagename text NOT NULL,
    imagefiletype text NOT NULL,
    imagedata bytea NOT NULL
);


--
-- Name: TABLE images; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE images IS 'This table contains all the images, with "object id" as a foreign key to the dataobject that associated with the image.  "imagename" is ... the name of the image, usually defined in LcConfig.py.  "imagefiletype" is always "png".  "imagedata" is a binary file in the format of the filetype.';


--
-- Name: object_activity; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW object_activity AS
    SELECT dataobjects.owner, dataobjects.classtype, count(*) AS count, (min(dataobjects.timestampcreated))::date AS first, (min(dataobjects.timestampcreated))::date AS latest FROM dataobjects GROUP BY dataobjects.owner, dataobjects.classtype ORDER BY dataobjects.owner, (min(dataobjects.timestampcreated))::date DESC;


--
-- Name: pageviews; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pageviews (
    sessionid integer,
    pageviewtimestamp timestamp without time zone DEFAULT now() NOT NULL,
    url text,
    datastring text
);


--
-- Name: pending_registrations; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE pending_registrations (
    fullname text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    affiliation text NOT NULL,
    reasons text NOT NULL,
    howfind text NOT NULL,
    inserted_timestamp timestamp without time zone DEFAULT now() NOT NULL,
    id integer NOT NULL,
    finished boolean DEFAULT false,
    email text NOT NULL,
    CONSTRAINT check_spaces_password CHECK ((NOT (password ~ '[[:space:]]'::text))),
    CONSTRAINT check_spaces_username CHECK ((NOT (username ~ '[[:space:]]'::text))),
    CONSTRAINT email_form_check_const CHECK ((email ~ '^[^[:space:]]+@[^[:space:]]+$'::text))
);


--
-- Name: TABLE pending_registrations; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE pending_registrations IS 'the fields should be self-explanatory, except "finished" is set to true when the registration has been taken care of, and the "id" is a serial number for each record that has no meaning except to make it easy to refer to the record later.';


--
-- Name: pending_registrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE pending_registrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: pending_registrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE pending_registrations_id_seq OWNED BY pending_registrations.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE reports (
    id integer NOT NULL,
    timestamp_run timestamp without time zone DEFAULT now(),
    report text NOT NULL
);


--
-- Name: TABLE reports; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE reports IS 'Whenever the daily maintenance script is run, it inserts the text of its report in here for later reference.';


--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE reports_id_seq OWNED BY reports.id;


--
-- Name: user_pageviews; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW user_pageviews AS
    SELECT a.username, a.sessionid, b.pageviewtimestamp, b.url, "substring"(b.datastring, 1, 25) AS "substring" FROM currentsessions a, pageviews b WHERE (a.sessionid = b.sessionid) ORDER BY a.username, a.sessionid, b.pageviewtimestamp;


--
-- Name: VIEW user_pageviews; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON VIEW user_pageviews IS 'Joins sessions with usernames.';


--
-- Name: user_pageviews_activity; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW user_pageviews_activity AS
    SELECT b.username, count(*) AS "total views", to_char(min(b.pageviewtimestamp), 'YYYY-MM-DD'::text) AS "earliest view", to_char(max(b.pageviewtimestamp), 'YYYY-MM-DD'::text) AS "latest view" FROM user_pageviews b GROUP BY b.username ORDER BY to_char(max(b.pageviewtimestamp), 'YYYY-MM-DD'::text) DESC;


--
-- Name: user_pageviews_by_url; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW user_pageviews_by_url AS
    SELECT user_pageviews.username, "substring"(user_pageviews.url, 1, 25) AS url_substr, min((user_pageviews.pageviewtimestamp)::date) AS "first date", max((user_pageviews.pageviewtimestamp)::date) AS "last date", count(*) AS count FROM user_pageviews GROUP BY user_pageviews.username, "substring"(user_pageviews.url, 1, 25) ORDER BY user_pageviews.username, count(*);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE authorizedusers ALTER COLUMN id SET DEFAULT nextval('authorizedusers_id_seq'::regclass);


--
-- Name: sessionid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE currentsessions ALTER COLUMN sessionid SET DEFAULT nextval('currentsessions_sessionid_seq'::regclass);


--
-- Name: objectserialnumber; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE dataobjects ALTER COLUMN objectserialnumber SET DEFAULT nextval('dataobjects_objectserialnumber_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE pending_registrations ALTER COLUMN id SET DEFAULT nextval('pending_registrations_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE reports ALTER COLUMN id SET DEFAULT nextval('reports_id_seq'::regclass);


--
-- Name: authorizedusers_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY authorizedusers
    ADD CONSTRAINT authorizedusers_pkey PRIMARY KEY (username);


--
-- Name: classes_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (classtype);


--
-- Name: currentsessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY currentsessions
    ADD CONSTRAINT currentsessions_pkey PRIMARY KEY (sessionid);


--
-- Name: dataobjects_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY dataobjects
    ADD CONSTRAINT dataobjects_pkey PRIMARY KEY (objectserialnumber);


--
-- Name: images_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY images
    ADD CONSTRAINT images_pkey PRIMARY KEY (objectid, imagename);


--
-- Name: currentsessions_username_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY currentsessions
    ADD CONSTRAINT currentsessions_username_fkey FOREIGN KEY (username) REFERENCES authorizedusers(username) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: dataobjects_classtype_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dataobjects
    ADD CONSTRAINT dataobjects_classtype_fkey FOREIGN KEY (classtype) REFERENCES classes(classtype);


--
-- Name: dataobjects_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY dataobjects
    ADD CONSTRAINT dataobjects_owner_fkey FOREIGN KEY (owner) REFERENCES authorizedusers(username);


--
-- Name: pageviews_sessionid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY pageviews
    ADD CONSTRAINT pageviews_sessionid_fkey FOREIGN KEY (sessionid) REFERENCES currentsessions(sessionid);


--
-- PostgreSQL database dump complete
--

