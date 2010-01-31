
import os
import re
import smtplib
import sys
import time
import types
import syslog  							# Add some syslog stuff

import Cheetah.Template as Template
import psycopg2
import psycopg2.extensions


# config ish stuff
DB_NAME = 'larrydb'
USER_NAME = 'webbs'
PASSPHRASE = 'hdy352!!%jf'
LCFITEMAIL = 'lcfit@demog.berkeley.edu'
EMAILTB = 'authorizedusers'

# from db, grab a list of email addresses to send
conn = psycopg2.connect(dsn='host=%s dbname=%s user=%s' % ('localhost', DB_NAME, USER_NAME))
curs = conn.cursor()
SQL='select email from %s where email is not null order by email' % EMAILTB
curs.execute(SQL)
emails = []
for row in curs.fetchall():
	emails.append(row[0])
	pass

print emails


# from command line get subject header and message file (cheetah
# template); add searchList func later. Template should maybe be in db?
subj = sys.argv[1]
messt = open(sys.argv[2]).read()

# loop: convert template, send to particular email
for email in emails:
	searchList = {'EMAIL':email, 'TIMESTAMP':time.strftime('%Y-%m-%d %H:%M:%S'), 'LCFITEMAIL':LCFITEMAIL}
	mess = str(Template.Template(messt, searchList=searchList))

	mserver = smtplib.SMTP('smtp.demog.berkeley.edu')
	mserver.set_debuglevel(0)
	headers = "Subject: %s\r\n\r\n" % subj
	mserver.sendmail(from_addr='lcfit@demog.berkeley.edu', to_addrs=email, msg=headers+mess)
	mserver.quit()

