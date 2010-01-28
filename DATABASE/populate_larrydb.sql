-- This file gets the database moving so that a few users can login,
--   and a few classes can be displayed.


begin;
insert into authorizedusers (username, password) values ('webbs', 'foobar');
insert into authorizedusers (username, password) values ('carl', 'foobar');
insert into authorizedusers (username, password) values ('rlee', 'foobar');
insert into authorizedusers (username, password) values ('tim', 'foobar');
INSERT into classes values ('HMD');
INSERT into classes values ('LcMFPop');
INSERT into classes values ('LcCoherentPop');
INSERT into classes values ('LcSinglePop');
commit;