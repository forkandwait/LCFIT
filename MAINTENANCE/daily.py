#!/usr/bin/python

"""
Basically: we do a bunch of queries, put the results in variables,
feed the variables through a template, and mail the result to webb.
"""

import os
import re
import smtplib
import sys
import time
import types
import syslog  							# Add some syslog stuff
syslog.openlog('daily.py', syslog.LOG_PID | syslog.LOG_NOWAIT | syslog.LOG_NDELAY)

import Cheetah.Template as Template
import psycopg2
import psycopg2.extensions

# Config stuff
DB_NAME = 'larrydb'
EMAIL = 'webbs@demog.berkeley.edu'
IS_DEVEL_MACHINE = True					# Is this script being run on 
LARRY_WWW_FILE_ROOT = '/var/www/localhost/htdocs' # put the tar of larry here for linking and downloading
LARRY_TMP_FILE_ROOT = '/tmp' # put the tar  of the database here
LARRY_TRUNK ='/home/webbs/larry'
LARRY_DATA_DIR=LARRY_WWW_FILE_ROOT + '/larry-data'
PASSPHRASE = 'hdy352!!%jf'
SVN_ROOT = '/var/lib/svn/DEMOG_SVN'
TEMPLATE_FILE = '/home/webbs/larry/MAINTENANCE/daily_email.tmpl'
USER_NAME = 'webbs'
TESTER_NAME = 'webbs_tester'			# name under which testing stuff is stored
TESTER_SWEEP_DAYS = 3					# days old for testing objects to delete

#function to strip stupid stuff from 2-d arrays
def strip_q(arr):
	ret = [[str(x) for x  in y ] for y in arr]
	ret = [[x.replace("'", '') for x in y ] for y in ret]
	return ret

# Tell log hello
syslog.syslog('Beginning run of LCFIT daily.py')

#  Set up
conn = psycopg2.connect(dsn='host=%s dbname=%s user=%s' % ('localhost', DB_NAME, USER_NAME))
curs = conn.cursor()
search_dict = {}						# The things that will go into the template
search_dict['RUN_START_TIME'] = time.strftime('%Y-%m-%d %H:%M:%S')
search_dict['BLAH'] = 'a string to be interpolated'

# Delete all the empty temp directories in larry-data over 48 hours old
for f in os.listdir(LARRY_DATA_DIR):
	try:
		fdir = LARRY_DATA_DIR + '/' + f
		os.rmdir(fdir)
		syslog.syslog('Deleted: %s.' % fdir)
	except OSError, e:
		syslog.syslog('Non-empty directory %s.  Exception: "%s".'  % (fdir, e))

# Delete all files over TESTER_SWEEP_DAYS days old created by TESTER_NAME
sql = " delete from  dataobjects where owner='%s' and age(timestampcreated) < interval '%s days' " \
	  % (TESTER_NAME, TESTER_SWEEP_DAYS)
curs.execute(sql)
conn.commit()
search_dict['TEST_OBJECTS_DELETE_COUNT'] = curs.rowcount

# Vacuum the DB
try:
	conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	#curs.execute("VACUUM FULL; ANALYZE;")
	conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)
except:
	raise

#  Check disk size
p = os.popen('df -h')
search_dict['DF_OUTPUT'] = p.read()
p.close()

#  Check uptime and logins
p = os.popen('w')
search_dict['W_OUTPUT'] = p.read()
p.close()

#  Check number of LC sessions in the last day
sql = "select username, count(*) as c from currentsessions " + \
	  " where starttime > cast ('%s' as timestamp) - interval '1 day' " % search_dict['RUN_START_TIME'] + \
	  " group by username order by c desc;" 
try:
	curs.execute(sql)
except:
	raise
search_dict['LC_SESSION_COUNTS'] = strip_q(curs.fetchall())


#  Check total number of open LC sessions
sql = "select username, count(*) as c from currentsessions where stoptime is not null " + \
	  " group by username ;" 
try:
	curs.execute(sql)
except:
	raise
search_dict['LC_SESSION_TOTALS'] = strip_q(curs.fetchall())


# Check number, type, size, owner of LC objects last day
sql = "select owner, classtype, count(*) as c from dataobjects " + \
	  " where timestampcreated > cast ('%s' as timestamp) - interval '1 day' " % search_dict['RUN_START_TIME'] + \
	  " group by owner, classtype order by owner, classtype"
try:
	curs.execute(sql)	
except:
	raise
search_dict['LC_DAILY_OBJECT_INFO'] = strip_q(curs.fetchall())

# Check number, type, size, owner of LC objects total
sql = "select owner, classtype, count(*) as c from dataobjects " + \
	  " group by owner, classtype order by owner, classtype"
try:
	curs.execute(sql)
except:
	raise
search_dict['LC_TOTAL_OBJECT_INFO'] = strip_q(curs.fetchall())

#  Check pending registrations, creating scripts in the template
#      Email         Username  Password  Timestamp           Fullname  Affil        Reasons   Howfind
sql = "select email, username, password, inserted_timestamp, fullname, affiliation, reasons, howfind " +\
	  " from pending_registrations where not finished order by inserted_timestamp asc"
try:
	curs.execute(sql)
except:
	raise
search_dict['LC_PENDING_REG'] = strip_q(curs.fetchall())

#  Do something with the log as analyzed by analog
search_dict['ANALOG_OUTPUT'] = file('/var/log/analog/index.txt').read()

#  Create text report using template, including registration scripts for pending users
search_dict['RUN_END_TIME'] = time.strftime('%Y-%m-%d %H:%M:%S')
search_list = [search_dict]
report_template = Template.Template(file=TEMPLATE_FILE, searchList = search_list)
report = str(report_template)
sql = "insert into reports (report) values (quote_literal(%s))" 
try:
	curs.execute(sql, (report,))
	conn.commit()
except:
	raise
	
#  Clean up database connection
curs.close()
conn.close()

#  If running a development machine, back up source code, export
#  source code, and db data
if IS_DEVEL_MACHINE:
	out = []
	out.append(os.system("svnadmin dump --quiet %s > %s/lcfit.svn.dump" % (SVN_ROOT, LARRY_WWW_FILE_ROOT)))
	out.append(os.system("bzip2 --force %s/lcfit.svn.dump" % LARRY_WWW_FILE_ROOT))
	out.append(os.system("svn export --force --quiet %s /tmp/larry_export" % LARRY_TRUNK))
	out.append(os.system("tar -cjf %s/lcfit.tar.bz2 /tmp/larry_export 2>/dev/null" % LARRY_WWW_FILE_ROOT))
	out.append(os.system("pg_dump -a %s | gpg --batch -a --symmetric --passphrase='%s' > %s/lcfit-db.gpg" \
					% (DB_NAME, PASSPHRASE, LARRY_TMP_FILE_ROOT)))
	if out.count(0) < 5: 
		sys.stderr.write("Problem backing up source and db: %s" % out)
		sys.stderr.flush()
else:
	# if not a development machine, dump the database
	out = []
	out.append(os.system("pg_dump -a %s | gpg  -a --symmetric --passphrase='%s' > %s/lcfit-db.gpg" \
					% (DB_NAME, PASSPHRASE, LARRY_WWW_FILE_ROOT)))
	if out.count(0) < 1: 
		sys.stderr.write("Problem backing up source and db: %s" % out)
		sys.stderr.flush()

#  Email results
mserver = smtplib.SMTP('smtp.demog.berkeley.edu')
mserver.set_debuglevel(0)
headers = "Subject: %s\r\n\r\n" % \
		  ('LCFIT Daily Maintenance: %s' % time.asctime())
mserver.sendmail(from_addr='webbs@demog.berkeley.edu', to_addrs=[EMAIL], msg=headers+report)
mserver.quit()

# Tell log goodbye
syslog.syslog('Ending run of LCFIT daily.py')
