

--
-- Name: new_lc_user(text, text); Type: FUNCTION; Schema: public; Owner: webbs
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
        RAISE EXCEPTION 'Nonexistent or finished ID/password: %, %.', $1, $2;
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


ALTER FUNCTION public.new_lc_user(text, text) OWNER TO webbs;

--
-- Name: FUNCTION new_lc_user(text, text); Type: COMMENT; Schema: public; Owner: webbs
--

COMMENT ON FUNCTION new_lc_user(text, text) IS 'Adds a new user with password.';

