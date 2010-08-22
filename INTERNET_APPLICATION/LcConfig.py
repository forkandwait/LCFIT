"""
This module:

* imports the standard libraries for all the other modules;

* sets up logging, signal handling, numpy and matplotlib, Coale-Guo style extension;

* holds all the constants;

* defines LCFIT specific exceptions;

"""
################################################################
## standard libraries

import cPickle
import copy
import datetime
import logging
import md5
import os
import pprint
import random
import re
import shelve
import string
import smtplib
import sys
#import syslog
import time
import textwrap
import traceback 
import types

########################
## Set up sysloging -- at INFO usually
## TODO: make plain logging, since syslog depends on a server
# syslog.openlog('LCFIT', syslog.LOG_PID | syslog.LOG_NOWAIT | syslog.LOG_NDELAY)
# syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_NOTICE))
# syslog.syslog(syslog.LOG_DEBUG, 'LcConfig.py executing')

LARRY_LOGFILENAME='/home/webbs/lcfitlog'
logging.basicConfig(filename=LARRY_LOGFILENAME, level=logging.DEBUG)
logging.debug("LcConfig.py executing.")


################################################################
## Signal handlers for debugging -- USR1 pauses() the process, USR2 does 
import signal
def usr1(sig, stack):
	logging.info( 'Received usr1: %s' % sig)
	signal.pause()
	return True
def usr2(sig, stack):
	logging.info( 'Received usr2: %s' % sig)
	return True
signal.signal(signal.SIGUSR1, usr1)
signal.signal(signal.SIGUSR2, usr2)

################################################################
## numpy, scipy, matplotlib, pylab config stuff
import numpy as N
import scipy as S 
import scipy.stats as ST
N.set_printoptions(linewidth=1000000, threshold=1000000, precision=6) # Stupid interactive stuff
PYLABHOME = '/tmp'						# For the font cache
os.environ['HOME'] = PYLABHOME	  # Where we store font cache for pylab 
MPLCONFIGDIR = '/tmp'					# For who knows what
os.environ['MPLCONFIGDIR'] = MPLCONFIGDIR
import matplotlib as MPL
try:
	MPL.use('Agg')	   # matplotlib will use the Agg backend for rendering
except RuntimeError, e:
	logging.critical ('Error trying to run MPL.use(): \"%s\"' % e)
	raise
import pylab as PL 


################################################################
## Constants:

# For emailing registration alerts
LARRY_ADMIN_EMAIL = 'lcfit@demog.berkeley.edu'

# If True, give a backtrace instead of a nice error
LcHardErrors = False

# Do Profiling?
LARRY_DO_PROFILE = False

# Do we want to LcDB block waiting for USR2 at various weird times?
LARRY_TEST_RECONNECT=False	

## Form keys
##
## Note that these often provide the names of parameter, so name
## accordingly
LARRY_USERNAME_KEY          = 'USERNAME'
LARRY_PASSWORD_KEY          = 'PASSWORD'
LARRY_OBJECT_ID_KEY         = 'LC_OBJECT_ID'
LARRY_OBJECT_COMMENTS_KEY   = 'notes'
LARRY_IMAGE_NAME_KEY        = 'LC_IMAGE_NAME'
LARRY_ERROR_MESSAGE_KEY     = 'LC_ERROR_MESSAGE'
LARRY_AGE_CUTOFF_KEY        = 'ageCutoff'	# For specifying age cutoff wrt kanisto etc
LARRY_STEPS_FORWARD_KEY     = 'stepsForward'
LARRY_GENDER_KEY            = 'gender'
LARRY_NUMRUNS_KEY           = 'numberRuns'
LARRY_CONFIDENCE_INTERVAL_KEY = 'projConfidenceInterval'
LARRY_UNSELECTED_VALUE      = 'Unselected'
LARRY_FLATTEN_BX_KEY        = 'DO_FLATTEN_BX'

"""DELETE weird functionals """
LARRY_LT_FUNC_TYPE_KEY = 'ltFuncType'
LARRY_LT_FUNC_PARAM1_KEY = 'beginFuncParam'	# E.g. x for e(x), or age of child dependency
LARRY_LT_FUNC_PARAM2_KEY = 'endFuncParam'	# E.g. the adult part of dependency
"""DELETE thing for passing objects between forms"""
LARRY_OBJECT_SERIALNO_PREFIX = 'OBJECT_SERIALNO:' # Used for prefixing object serial numbers used in forms
LARRY_OBJECT_SERIALNO_PREFIX_RE = re.compile('^' + LARRY_OBJECT_SERIALNO_PREFIX + '\s*')  

## Session keys and stuff
LARRY_SESS_LAST_CREATED_ID = 'last_created'	# id of the latest object
LARRY_SESSION_KEY = 'SessionID'
LARRY_SESSION_TIMEOUT = 24 * 60 * 60 	# A fulll day of seconds

## Template Placeholder Names
LARRY_FORM_TARGET_PLACEHOLDER = 'TARGET' # Where the form sends you when you hit submit
LARRY_ERROR_MESSAGE_PLACHOLDER = 'ERROR_MESSAGE' # Duh
LARRY_NAV_MAIN_PLACEHOLDER = 'MAIN'		# Where the whatever page gets expanded inside Application
LARRY_OBJECTLIST_PLACEHOLDER = "OBJECT_LIST" # The list of lists that have info about saved objects
LARRY_OBJECTCOLNAMES_PLACEHOLDER = "OBJECT_COLNAMES" # The column names of such
LARRY_TITLE_PLACEHOLDER = "TITLE"

## Important URL components in http space
LARRYWWWHOME = '/lcfit/lc'				# Application root
LARRYWWWDATA = '/lcfit-data'			# Data root

LARRY_WWW_DELETE_OBJECT = '/lcfit/lc/DeleteObject'
LARRY_WWW_DISPLAY_IMAGE = '/lcfit/lc/image'
LARRY_WWW_DISPLAY_OBJECT = '/lcfit/lc/ShowResults'
LARRY_WWW_DOCUMENTATION = '/lcfit/lc/Documentation'
LARRY_WWW_HMD_CONVERTER = '/lcfit/lc/InputHMD'
LARRY_WWW_HMD_PROCESS = '/lcfit/lc/ProcessHMD'
LARRY_WWW_HOME =  '/lcfit/lc'
LARRY_WWW_INDEX = '/lcfit/lc/Index'
LARRY_WWW_INPUT_RATES = '/lcfit/lc/InputRates'
LARRY_WWW_INPUT_RATES_COHERENT = '/lcfit/lc/InputRatesCoherent'
LARRY_WWW_INPUT_RATES_MF = '/lcfit/lc/InputRatesMF'
LARRY_WWW_LIST_OBJECTS = '/lcfit/lc/ListObjects'
LARRY_WWW_LOGIN = '/lcfit/lc/Login'
LARRY_WWW_LOGIN_ERROR= '/lcfit/lc/LoginError'
LARRY_WWW_LOGIN_FORM = '/lcfit/lc/LoginForm'
LARRY_WWW_LOGIN_PROCESS = '/lcfit/lc/LoginProcess'
LARRY_WWW_LOGOUT = '/lcfit/lc/Logout'
LARRY_WWW_OBJECT_DUMP = '/lcfit/lc/ObjectDump'
LARRY_WWW_RATES_COHERENT_PROCESS = '/lcfit/lc/ProcessRatesCoherent'
LARRY_WWW_RATES_MF_PROCESS = '/lcfit/lc/ProcessRatesMF'
LARRY_WWW_RATES_PROCESS = '/lcfit/lc/ProcessRates'
LARRY_WWW_REG_FORM = '/lcfit/lc/RegistrationForm'
LARRY_WWW_REG_PROCESS = '/lcfit/lc/RegistrationProcess'

LARRY_PREV_PEND_ERROR_PAGE='/RegistrationError-PendingUsername.html'
LARRY_PREV_REG_ERROR_PAGE='/RegistrationError-RegisteredUsername.html'

## Important filespace stuff
APACHEFILEROOT = '/var/www/localhost/htdocs'
LARRYBASE = '/home/webbs/lcfit.git/INTERNET_APPLICATION' # Where the executable libraries (not lc.py) live
LARRYTEMPLATEDIR = LARRYBASE + '/TEMPLATES'	# Where the templates for the webpages live
LARRYDATADIR = APACHEFILEROOT + '/larry-data' # Where the temporary 

## Polymorphic components of important objects.
## Also just plain naming conventions and randomalia
LARRY_IMAGES_DICT_POLYMORPHIC_COMPONENT = "imagesDict"
LARRY_INTERNAL_ID_POLYMORPHIC_COMPONENT = "LcID"
LARRY_LCDATBASE_POLYMORPHIC_COMPONENT = "lcdb"
LARRY_FEMALE = 'female' 				# Use when you need a flag for female
LARRY_MALE = 'male'						# ditto (male)
LARRY_COMBINED = 'combined'				# ditto (female)
LARRY_INF_NMX_REPLACEMENT = 1.0

## Convenient age data
LARRY_AGES = N.array([0,1,5,10,15,20,25,30,35,40,45,
					  50,55,60,65,70,75,80,85,90,95,100,105,110], N.int16)
LARRY_AGE_INDICES = dict(zip(LARRY_AGES, range(0, len(LARRY_AGES))))
LARRY_DEFAULT_NO_AGEWIDTHS = 24 		# 0-1, 1-4, 5-9, ..., 110+
LARRY_DEFAULT_AGEWIDTH = 5 				# except for first two....
LARRY_CG_CLOSE_AGE = 110
LARRY_SSA_5m105_DIFF = {80:0.421, 85:0.300, 90:0.200, 95:0.100, 100:0.050, 105:0.0, 110:-0.100, 115:-0.200}
LARRY_PROJECTION_WIDTH = 1

## Mortality Extension stuff
LARRY_DEFAULT_EXTENSION_METHOD = 'mxExtend_Boe'	##'mxExtend_Boe' 'mxExtend_CGNan'
LARRY_DEFAULT_AGE_CUTOFF = 80          # Last age for which we use empirical data, extend if older than this, eg 85 and older

## Ages at which we will graph lnmx against year # LARRY_AGES[:-3][::-1]
LARRY_LOGNMX_GRAPHIC_AGES = [0, 1, 5, 20, 40, 60, 80, 95]	
for age in LARRY_LOGNMX_GRAPHIC_AGES:
	assert age in LARRY_AGES, "Unallowed age for graphics: %f:" % age

## Things not to put in the data dump
LARRY_NOTWANTED_ATTRIBUTE_DUMPS = {'imagesDict':0, 'rates_text':0}

## String patterns for input verification
# spaces year spaces age-width spaces rates spaces rates spaces rates spaces
LARRY_HMD_ROW_RE = re.compile("^\s*\d{4}\s+[0-9-+]{1,7}\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s*$")
LARRY_END_WS_RE = re.compile("(\n+$)|\r")	# Use this re to split on whitespace
LARRY_TAIL_WS_RE = re.compile("\s+$")	# strip tail whitespace
LARRY_HEAD_WS_RE = re.compile("^\s+")	# strip head whitespace
LARRY_EMPTY_ROW_RE = re.compile("^\s*[nN][aA]\s*$")	# For rows that represent missing years of data
LARRY_NONALLOWED_NUMBER_PATTERN = "[^\s0-9.eE-]+" # Non-allowed values for table input in form
LARRY_EMPTY_ALL_RE = re.compile("^\s*$") # Forms with empty data (possible whitespace garbage)
LARRY_COMMENT_LINE_RE = re.compile("^\s*#.*$") # Strips comments - Use on individual lines -- not on entire text
LARRY_COMMENT_TRAILING_RE = re.compile("#.*$") # Strips comments - 
LARRY_WS = re.compile("^\s*$")

LARRY_FIELDSEP = '\t'
LARRY_ROWSEP = '\n'
LARRY_STANZASEP = '\n\n'

## Parameter for forms for creation of LcSinglePop object
## Confidence interval stuff
LARRY_POSSIBLE_CONFIDENCE_INTERVALS = [.8, .9, .95, .98, .99]
LARRY_DEFAULT_CONFIDENCE_INTERVAL = .95
LARRY_CONFIDENCE_INTERVAL = .95
LARRY_P_VAL= 1 - LARRY_CONFIDENCE_INTERVAL
LARRY_PERCENTILES = N.array([0.0, LARRY_P_VAL/2 , .5, 1.0-(LARRY_P_VAL/2), 1.0])
LARRY_ZSCORE = ST.norm.ppf(LARRY_CONFIDENCE_INTERVAL + LARRY_P_VAL/2)

## Parameter for age after which use Kanisto/CG/whatever
LARRY_POSSIBLE_AGE_CUTOFFS = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110]

LARRY_POSSIBLE_NUMRUNS = [5, 10, 20, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000]
LARRY_DEFAULT_NUMRUNS = 20

LARRY_POSSIBLE_STEPS_FORWARD = [5, 10, 25, 45, 46, 47, 48, 49, 50, 75, 100]
LARRY_DEFAULT_STEPS_FORWARD = 20

## Databse
LARRYDBNAME = 'larrydb'

## Other Constants
LARRY_IMAGE_FORMAT = 'png'

## Miscellaneious
LARRY_NULL_NUMBER = -999999
LARRY_REALLY_BIG_NUMBER = 100000.0
EMAIL = LARRY_ADMIN_EMAIL

################################################################
## Exceptions
class LcException(Exception):
	pass

# ==  "Reasonable" errors: ==
# * Input problem 
class LcInputException(LcException):
	pass 
# * Authorization or authentication problem.  
class LcAuthException(LcException):
	pass 
# * A dropped session problem. 
class LcSessionException(LcException):
	pass 
# == Errors that should only happen with handwritten GET or POST data == 
# * Database problem, especially missing data we assumed would be there
class LcDataException(LcException):
	pass 
# * Object versioning problem -- pickled objects unpickled into
# incompatible class
class LcVersionException(LcException):
	pass 
# == Errors that imply a bug or something ridiculous ==
# * An OS interface problem -- a file won't open, etc 
class LcOsException(LcException):
	pass
# * Code problem
class LcCodeException(LcException):
	pass

# Stuff to display a session error nicely
LcSessionExceptionMessage = 'Bad Session. Use the back button or try logging in again <a href=%s>here</a>.' % \
							LARRY_WWW_LOGIN_FORM
LcSessionExceptionRedirect = LARRY_WWW_LOGIN_ERROR + \
							 '?' + LARRY_ERROR_MESSAGE_KEY + \
							 '=' + LcSessionExceptionMessage

# Stuff to display a database error nicely
LcDataExceptionRedirect = LARRY_WWW_INDEX + \
						  '?' + LARRY_ERROR_MESSAGE_KEY + \
						  '=' + "Something weird happened with the database"

def make_LcDataExceptionRedirect_disconnect(mess=None):
	return LARRY_WWW_INDEX + \
		   '?' + LARRY_ERROR_MESSAGE_KEY + \
		   '=' + "Something weird happened with the database: \"%s\"" % mess

def make_LcDataExceptionRedirect(objectId = None):
	if objectId:
		return LARRY_WWW_INDEX + \
			   '?' + LARRY_ERROR_MESSAGE_KEY + \
			   '=' + 'Unknown object serial number: %s.' % objectId

# Exception that doesn't get caught
class FooException(Exception):
	def __init__ (self, mess=None):
		self.mess = mess
		return
	def __str__(self):
		return "FooException: %s" % self.mess
	pass
