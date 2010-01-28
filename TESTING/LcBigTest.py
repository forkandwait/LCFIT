'''
Functions and harnesses to test the interactive portion of the LARE system.

Remember the slight weirdness of having two logins, so must register with the apache version 

Correct input and correct output.

Incorrect input and "correct" -- ie reasonable error message -- output.
'''
import HTMLParser as H
import cookielib
import copy
import datetime
import md5
import numpy
import re
import sys
import string
import time
import unittest
import urllib2 as U2
#import pysqlite2.dbapi2 as sqlite # Database for results
import sqlite3 as sqlite

from urllib import urlencode

# Lc modules
import LcTestData as LT
sys.path.append('../../INTERNET_APPLICATION')
from LcConfig import * 
import LcHTMLParser
from LcUtil import Diagnose as D

# Various constants
STRIP_RE = re.compile('/lcfit/lc/')
USERNAME = 'webbs_tester'
PASSWORD = 'foobar'
APP_URL = 'http://localhost:80'
AUTH_REALM = 'larry' 					# Set in the httpd.conf file under AuthName

RATES_TEXT_24 = copy.copy(LT.JapanFnMx24)
RATES_LIST_24 = RATES_TEXT_24.split('\n')
RATES_LIST_LIST_24 = [[float(x) for x in row.split()] for row in RATES_TEXT_24.split('\n')]
RATES_ARRAY_24 = numpy.array(RATES_LIST_LIST_24, numpy.float)

# for (1) tests and results and (2) downloaded lare objects
TEST_RESULT_SCHEMA = "Create table test_results (testId integer, test text, errcode text, err text);"
ANALYSIS_RESULT_SCHEMA = "Create table lcrun_results (testId integer, test text, lcId integer, lcData text);"

# Names of pages and pseudo-pages
FORM_NAMES = [LARRY_WWW_INPUT_RATES, LARRY_WWW_INPUT_RATES_MF, LARRY_WWW_INPUT_RATES_COHERENT, LARRY_WWW_HMD_CONVERTER]
PROCESS_NAMES = [LARRY_WWW_RATES_PROCESS, LARRY_WWW_RATES_MF_PROCESS, LARRY_WWW_RATES_COHERENT_PROCESS, LARRY_WWW_HMD_PROCESS]
LIST_NAMES = [LARRY_WWW_LIST_OBJECTS]

# Set up opener etc for the http connection, with Basic auth and cookies.
auth_handler = U2.HTTPBasicAuthHandler()
auth_handler.add_password(AUTH_REALM, APP_URL, USERNAME, PASSWORD) # realm, uri, user, passwd
cj = cookielib.CookieJar()
opener = U2.build_opener(auth_handler, U2.HTTPCookieProcessor(cj))

# ...and install it globally so it can be used with urlopen.
U2.install_opener(opener)

def P(*args):
	"""Simple print to stderr thing."""
	sys.stderr.write("---\n%s\n" % datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
	sys.stderr.write("%s" % args)
	sys.stderr.write("---\n")
	sys.stderr.flush()

# Instantiate an HTML checker for later use.
LcHTML_checker = LcHTMLParser.LcHTMLChecker(tagList=['div', 'a'])

def checkDivClass(htmlParser, data, attr, value=None):
	"""Checks for a attribute and value in the HTML data""" 
	LcHTML_checker.reset()
	LcHTML_checker.feed(data)
	tagCheck = LcHTML_checker.checkTag(tag='div', attr=attr, value=value)
	LcHTML_checker.reset()
	return tagCheck

def getData(url, urlData = None, method='POST'):
	if method == 'POST':
		url_conn = U2.urlopen(url, urlData)
	elif method == 'GET':
		if urlData is None:
			raise Exception, "GETting with empty urlData - bad"
		openStr = url + '?' + urlData
		#print openStr
		url_conn = U2.urlopen(openStr)
	else:
		raise Exception, "Unknown method: %s.  Should be either 'POST' or 'GET'." % method
	url_data = url_conn.read()
	url_conn.close()
	return (url_conn, url_data)


def lcLogin():
	""" Login, returning stuff. """
	loginStr = urlencode({LARRY_USERNAME_KEY:USERNAME, LARRY_PASSWORD_KEY:PASSWORD, 'submit': 'SUBMIT'})
	#print APP_URL + LARRY_WWW_LOGIN_PROCESS, loginStr
	url_conn, url_data = getData(APP_URL + LARRY_WWW_LOGIN_PROCESS, loginStr, method='GET')
	return (url_conn, url_data)


def lcLogout():
	"""Logout, returning stuff."""
	url_conn, url_data = getData(APP_URL + LARRY_WWW_LOGOUT)
	return (url_conn, url_data)


#############################################

class LcTestResult(unittest.TestResult):

	def __init__(self, *args, **kwargs):
		super(LcTestResult, self).__init__(*args, **kwargs)
		
		self.timestamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		self.id = int(time.time())
		self.dbconn = sqlite.connect("testLc.%s.sqlite" % self.id,
									 detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
		self.dbconn.execute(TEST_RESULT_SCHEMA)
		self.dbconn.execute(ANALYSIS_RESULT_SCHEMA)
		self.dbconn.commit()
		return
	
	def addError(self, test, err):
		self.errors.append(err)
		self.dbconn.execute("insert into test_results (testId, test, errcode, err) values (?, ?, ?, ?)",
							(self.id, 'error', str(test), str(err)))
		self.dbconn.commit()
		return

	def addFailure(self, test, err):
		self.failures.append(err)
		self.dbconn.execute("insert into test_results (testId, test, errcode, err) values (?, ?, ?, ?)",
							(self.id, 'failure', str(test), str(err)))
		self.dbconn.commit()
		return

	def addSuccess(self, test):
		self.dbconn.execute("insert into test_results (testId, test, errcode) values (?, ?, ?)",
							(self.id, 'success', str(test)))
		self.dbconn.commit()
		return


class TestLcInterface(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestLcInterface, self).__init__(*args, **kwargs)
		self.testId = int(time.time())
		
	def setUp(self):
		lcLogin()
		return

	def test01LogInOut(self):
		"""Log in and out."""

		"""Check to make sure get (0) error before login, (1)
		application and (2) application home, (3) error message after
		logout."""

		lcLogout()							# Since setUp should log us in.

		conn, data = getData(APP_URL + LARRY_WWW_INDEX)
		assert checkDivClass(LcHTML_checker, data, 'class', 'Error'), \
			   AssertionError("Tried to access page without login, should have been redirected error page.") 

		conn,data = lcLogin()
		assert checkDivClass(LcHTML_checker, data, 'class', 'Application'), \
			   AssertionError("Tried to login -- should be directed to application home, but wasn't.") 

		conn, data = lcLogout()
		assert checkDivClass(LcHTML_checker, data, 'class', 'ServerIndex'), \
			   AssertionError("Logged out.  Should have been redirected to the main page.")

		conn, data = lcLogout()
		"""assert (not checkDivClass(LcHTML_checker, data, 'class', 'ServerIndex')), \
			   AssertionError('Trying a double logout. Should STILL be on the ServerIndex main page.')"""
		
		return


	def test02ListsAndForms(self):
		"""Run through all the lists and forms to make sure they generate."""

		for pageName in FORM_NAMES + LIST_NAMES:
			divName = STRIP_RE.sub('', pageName)
			c,d = getData(APP_URL + pageName)
			assert checkDivClass(LcHTML_checker, d, 'class', divName), AssertionError('(%s) \n\n%s' % (divName, d))
			pass 
		pass

	def test03FormSubmissionSinglePopNormal(self):
		""" Test the single population thing.   Normal data"""
		formData = urlencode({'rates':RATES_TEXT_24,
							  'notes':'TestType=%s TestId=%s' % ('Normal Japan F',self.testId),
							  'start_year':'1960',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return

	def test04FormSubmissionSinglePopNormalExtraSpaces(self):
		""" Test the single population thing."""

		rates_text_24 = ' \n\n   \t\n\t\n' + RATES_TEXT_24 + '\n\n   \n \n  '
		formData = urlencode({'rates':rates_text_24,
							  'notes':'TestType=%s TestId=%s' % ('ExtraSpaces',self.testId),
							  'start_year':'1960',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return


	def test05FormSubmissionSinglePopMissing(self):
		"""Missing years, 24 ages."""
		ratesText24Missing = '\n'.join(RATES_LIST_24[0:10] + ['NA']*4 + RATES_LIST_24[10:])
		formData = urlencode({'rates':ratesText24Missing,
							  'notes':'TestType=%s TestId=%s' % ('MissingData',self.testId),
							  'start_year':'1960',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return

	def test06FormSubmissionSinglePopNeedExt(self):
		"""No missing years, need extension."""
		ratesText18 = '\n'.join([' '.join([str(x) for x in row]) for row in RATES_ARRAY_24[:,:19]])
		formData = urlencode({'rates':ratesText18,
							  'notes':'TestType=%s TestId=%s' % ('NeedExtension',self.testId),
							  'start_year':'1960',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return

	def test07FormSubmissionSinglePopExtAndMiss(self):
		"""NA's for certain years with need extension."""
		rlist = [' '.join([str(x) for x in row]) for row in RATES_ARRAY_24[:,:19]] # list of strings
		ratesText18Miss = '\n'.join(rlist[0:10] + ['NA']*4 + rlist[10:15] + ['NA'] + rlist[15:]) # put in some na's, make a big string
		formData = urlencode({'rates':ratesText18Miss,
							  'notes':'TestType=%s TestId=%s' % ('ExtensionAndMissing',self.testId),
							  'start_year':'1960',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return

	def test08FormSubmissionSinglePopBad(self):
		""" Data that should make it crap out"""

		rates_text_24 = '\n'.join(RATES_LIST_24[0:10]) + 'this line\n\n  better \n mmake it choke' + '\n'.join(RATES_LIST_24[10:])
		formData = urlencode({'rates':rates_text_24,
							  'notes':'TestType=%s TestId=%s' % ('BadDataShouldChoke',self.testId),
							  'start_year':'1960',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'Error'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d)) # Shouldn't work -- bad rates
		return


	### Coherent
	def test39FormSubmissionCoherentRich(self):
		"""Coherent with straightforward rich country data."""
		# ['austria', 'canada', 'denmark', 'england', 'finland',
		# 'france', 'germanywest', 'italy', 'japan', 'netherlands',
		# 'norway', 'spain', 'sweden', 'switzerland', 'usa'],
		formData = urlencode({'mortRates':LT.richCountryRates,
							  'populations':LT.richCountryPop,
							  'notes':'TestType=%s TestId=%s' % ('NormalCoherentRich',self.testId),
							  'labels': 'austria canada denmark england finland ' + \
										'france germanywest italy japan netherlands ' +  \
							  			'norway spain sweden switzerland usa',
							  'start_year':'1960', # Is this right?
							  'numberRuns':'100',
							  'stepsForward':'100',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_COHERENT_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return


	def test39FormSubmissionCoherentRich_unweighted(self):
		"""Unweighted coherent with straightforward rich country data."""
		# ['austria', 'canada', 'denmark', 'england', 'finland',
		# 'france', 'germanywest', 'italy', 'japan', 'netherlands',
		# 'norway', 'spain', 'sweden', 'switzerland', 'usa'],
		formData = urlencode({'mortRates':LT.richCountryRates,
							  'populations':'',
							  'notes':'TestType=%s TestId=%s' % ('NormalCoherentRich',self.testId),
							  'labels': 'austria canada denmark england finland ' + \
										'france germanywest italy japan netherlands ' +  \
							  			'norway spain sweden switzerland usa',
							  'start_year':'1960', # Is this right?
							  'numberRuns':'100',
							  'stepsForward':'100',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_COHERENT_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return

	def test40FormSubmissionCoherentSwedenMF(self):
		"""Coherent with straightforward sweden two sex country data."""

		formData = urlencode({'mortRates':LT.swedenMxMFCoherent,
							  'populations':LT.swedenPopMFCoherent,
							  'notes':'TestType=%s TestId=%s' % ('NormalCoherentSwedenMF',self.testId),
							  'labels': 'male female',
							  'start_year':'1950', 
							  'numberRuns':'100',
							  'stepsForward':'100',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_COHERENT_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return


	def test40FormSubmissionCoherentSwedenMF_unweighted(self):
		"""Unweighted coherent with straightforward sweden two sex country data."""

		formData = urlencode({'mortRates':LT.swedenMxMFCoherent,
							  'populations':'',
							  'notes':'TestType=%s TestId=%s' % ('NormalCoherentSwedenMF',self.testId),
							  'labels': 'male female',
							  'start_year':'1950', 
							  'numberRuns':'100',
							  'stepsForward':'100',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		c,d = getData(APP_URL + LARRY_WWW_RATES_COHERENT_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return


	### Two sex
	def test41FormSubmissionTwosex(self):
		"""Two sex with straightforward data."""
		
		formData = urlencode({'femaleRates':LT.swedenMxFemHMD,
							  'maleRates':LT.swedenMxMaleHMD,
							  'combinedRates':LT.swedenMxAllHMD,
							  'notes':'TestType=%s TestId=%s' % ('Normal2sexSweden',self.testId),
							  'start_year':'1950',
							  'numberRuns':'5',
							  'stepsForward':'5',
							  'ageCutoff':'80',
							  'projConfidenceInterval':'0.95'})
		#print APP_URL + LARRY_WWW_RATES_MF_PROCESS
		c,d = getData(APP_URL + LARRY_WWW_RATES_MF_PROCESS, formData)
		assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), \
			   AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return

	def test12RegistrationForm(self):
		"""Make sure registration form displays"""
		conn, data = getData("http://localhost/lcfit/lc/Registration")
		return


	def test13MissingObject(self):
		""" DISABLED Test to make sure the missing object gets a nice error AND
		the error is not a login problem."""

		lcLogin()
		
		conn, data = getData(APP_URL + LARRY_WWW_DISPLAY_OBJECT + "?LC_OBJECT_ID=-1")
		"""
		assert checkDivClass(LcHTML_checker, data, 'class', 'Error'), \
			   AssertionError("Tried to request non-existent object, should have been given error page.")
		"""
		lcLogout()
		
		return

	def test61HMD(self):
		""" Test HMD conversion """
		#raise Exception(APP_URL + LARRY_WWW_HMD_PROCESS)
		lcLogin()
		formData = urlencode({'hmdinput':LT.Japan_HMD_nMx,
							  'notes':'TestType=%s TestId=%s' % ('HMD converter',self.testId),
							  'start_year':'1960'})
		c,d = getData(APP_URL + LARRY_WWW_HMD_PROCESS, formData)
		lcLogout()
		#assert checkDivClass(LcHTML_checker, d, 'class', 'ListObjects'), AssertionError('(%s) \n\n%s' % ('ListObjects', d))
		return


	def test52ListAndDownloadDump(self):
		"""Gets dumps from all of this test run, via ObjectList, the
		display page, and the datadump."""

		# Download ListObject page ...
		c,d = getData(APP_URL + LARRY_WWW_LIST_OBJECTS)
		f=open('listHTMLdump.html', 'w')
		f.write(d)
		f.close()		

		# ... feed it to the parser which will return a list of
		# appropriate LC Object ID's ...
		P = LcHTMLParser.LcObjectListParser()
		notesIdsList = P(d)	# [{'notes':'TestId=123 TestType=blahblah', 'id':'1000'}, {etc}, {}] id is for lcObject in system
		
		# ... go over list, extract the TestId and the TestType and update the hash ...
		for row in notesIdsList:
			try:
				testIdStr = re.findall('TestId=\S+', row['notes'])[0]
				testId = string.split(testIdStr, '=')[1]
				testTypeStr = re.findall('TestType=\S+', row['notes'])[0]
				testType = string.split(testTypeStr, '=')[1]
				row['testId'] = copy.copy(testId) # updating reference, so this works
				row['testType'] = copy.copy(testType)
			except IndexError, KeyError:			# Doesn't have 
				pass
			pass

		# ... cull test ids that don't apply to us ...
		oldIdsList = copy.copy(notesIdsList)
		notesIdsList = [x for x in notesIdsList if x.has_key('testId') and int(x['testId']) == int(self.testId)]  
		assert len(notesIdsList) > 0, \
			   AssertionError("self.testId: %s.\nAll test ids: %s" %  \
							  (self.testId, [x['testId'] for x in oldIdsList if x.has_key('testId')]))
		
		# ... for each object id, create the datadump link, download,
		# and append to a text variable, and save.
		f = open('objectDump-%s.txt' % self.testId, 'w')
		for row in notesIdsList:
			c,d = getData(APP_URL + LARRY_WWW_OBJECT_DUMP, urlencode({LARRY_OBJECT_ID_KEY:row['id']})) 
			f.write('\n***\nLcID: %s\nTest ID: %s\nTest Type: %s\n\n' % (row['id'], row['testId'], row['testType']) + d)
			pass
		f.close()
		
		return



	def tearDown(self):
		lcLogout()
		return
	pass

if __name__ ==  '__main__':

	import getopt
	options, arglist = (getopt.getopt(sys.argv[1:], "ahf")) # -f to fill a database
	optDict = dict(options)

	def simpleSuite():
		suite = unittest.TestSuite()
		suite.addTest(TestLcInterface('test61HMD'))
		suite.addTest(TestLcInterface('test03FormSubmissionSinglePopNormal'))
		return suite

	
	
	if optDict.has_key('-f'):
	
		TR = LcTestResult()
		
		TS = unittest.makeSuite(TestLcInterface)
		
		TS.run(TR)

		for failure in TR.failures:
			print "Failed:", failure[0]
		
		for error in TR.errors:
			print "Error:", error[0]

		if not TR.errors and not TR.failures:
			sys.stderr.write('Ok\n')
			sys.exit(0)
		else:
			sys.exit(1)
			
	elif optDict.has_key('-h'):
		suite = simpleSuite()
		unittest.TextTestRunner(verbosity=2).run(suite)
	elif optDict.has_key('-a'):
		unittest.main()
	else:
		unittest.main()
