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
import logging.handlers
import os
import pprint
import random
import re
import shelve
import string
import smtplib
import sys
import time
import textwrap
import traceback 
import types

import hashlib
md5 = hashlib.md5()


from LcLog import lcfitlogger

########################
## numpy, scipy, matplotlib, pylab config stuff
########################
import numpy as N
import scipy as S 

import scipy.special as SP

import scipy.optimize

import scipy.interpolate

import scipy.stats as ST

def lcfitz(p):
	return S.sqrt(2) * SP.erfinv(2*p-1)
def _lstsq(x, y):
	_x = x.reshape(x.size,1)
	_x = N.hstack([_x, N.ones([_x.size, 1])])
	_y = y.reshape(y.size,1)
	_out = N.linalg.lstsq(_x, _y)
	return(_out[0], _out[1]); 
#x=N.random.rand(1,12)
#(_c0_1, _c1_1) = _lstsq(x[0,:-1], x[0,1:])
#(_c0_2, _c1_2, _xfjf, _xkfjh, _iwue) = ST.linregress(x[0,:-1], x[0,1:])
#(c1, c0, r, two_tail_p, stderr_est) = ST.linregress(_kt[:-1],_kt[1:])

N.set_printoptions(linewidth=1000000, threshold=1000000, precision=6) # Stupid interactive stuff
PYLABHOME = '/tmp'						# For the font cache
os.environ['HOME'] = PYLABHOME	  # Where we store font cache for pylab 
MPLCONFIGDIR = '/tmp'					# For who knows what
os.environ['MPLCONFIGDIR'] = MPLCONFIGDIR

import matplotlib as MPL
try:
	MPL.use('Agg')	   # matplotlib will use the Agg backend for rendering
except RuntimeError, e:
	lcfitlogger.critical ('Error trying to run MPL.use(): \"%s\"' % e)
	raise
import pylab as PL 


########################
## Constants
########################

# For emailing registration alerts
LCFIT_ADMIN_EMAIL = 'lcfit@demog.berkeley.edu'

# SMTP Server
LCFIT_SMTP = "smtp.demog.berkeley.edu"

# If True, give a backtrace instead of a nice error
LcHardErrors = False

# Do Profiling?
LCFIT_DO_PROFILE = False

# Do we want to LcDB block waiting for USR2 at various weird times?
LCFIT_TEST_RECONNECT=False	

## Form keys
##
## Note that these often provide the names of parameter, so name
## accordingly
LCFIT_USERNAME_KEY          = 'USERNAME'
LCFIT_PASSWORD_KEY          = 'PASSWORD'
LCFIT_OBJECT_ID_KEY         = 'LC_OBJECT_ID'
LCFIT_OBJECT_COMMENTS_KEY   = 'notes'
LCFIT_IMAGE_NAME_KEY        = 'LC_IMAGE_NAME'
LCFIT_ERROR_MESSAGE_KEY     = 'LC_ERROR_MESSAGE'
LCFIT_AGE_CUTOFF_KEY        = 'ageCutoff'	# For specifying age cutoff wrt kanisto etc
LCFIT_STEPS_FORWARD_KEY     = 'stepsForward'
LCFIT_GENDER_KEY            = 'gender'
LCFIT_NUMRUNS_KEY           = 'numberRuns'
LCFIT_CONFIDENCE_INTERVAL_KEY = 'projConfidenceInterval'
LCFIT_UNSELECTED_VALUE      = 'Unselected'
LCFIT_FLATTEN_BX_KEY        = 'DO_FLATTEN_BX'

"""DELETE thing for passing objects between forms"""
LCFIT_OBJECT_SERIALNO_PREFIX = 'OBJECT_SERIALNO:' # Used for prefixing object serial numbers used in forms
LCFIT_OBJECT_SERIALNO_PREFIX_RE = re.compile('^' + LCFIT_OBJECT_SERIALNO_PREFIX + '\s*')  

## Session keys and stuff
LCFIT_SESS_LAST_CREATED_ID = 'last_created'	# id of the latest object
LCFIT_SESSION_KEY = 'SessionID'
LCFIT_SESSION_TIMEOUT = 24 * 60 * 60 	# A fulll day of seconds

## Template Placeholder Names
LCFIT_FORM_TARGET_PLACEHOLDER = 'TARGET' # Where the form sends you when you hit submit
LCFIT_ERROR_MESSAGE_PLACHOLDER = 'ERROR_MESSAGE' # Duh
LCFIT_NAV_MAIN_PLACEHOLDER = 'MAIN'		# Where the whatever page gets expanded inside Application
LCFIT_OBJECTLIST_PLACEHOLDER = "OBJECT_LIST" # The list of lists that have info about saved objects
LCFIT_OBJECTCOLNAMES_PLACEHOLDER = "OBJECT_COLNAMES" # The column names of such
LCFIT_TITLE_PLACEHOLDER = "TITLE"

## Important URL components in http space
LCFIT_WWW_HOME =  '/lcfit/lc'
LCFIT_WWW_INDEX = '/lcfit/lc/Index'
LCFIT_WWW_DELETE_OBJECT = '/lcfit/lc/DeleteObject'
LCFIT_WWW_DISPLAY_IMAGE = '/lcfit/lc/image'
LCFIT_WWW_DISPLAY_OBJECT = '/lcfit/lc/ShowResults'
LCFIT_WWW_DOCUMENTATION = '/lcfit/lc/Documentation'
LCFIT_WWW_HMD_CONVERTER = '/lcfit/lc/InputHMD'
LCFIT_WWW_HMD_PROCESS = '/lcfit/lc/ProcessHMD'
LCFIT_WWW_INPUT_RATES = '/lcfit/lc/InputRates'
LCFIT_WWW_INPUT_RATES_COHERENT = '/lcfit/lc/InputRatesCoherent'
LCFIT_WWW_INPUT_RATES_MF = '/lcfit/lc/InputRatesMF'
LCFIT_WWW_LIST_OBJECTS = '/lcfit/lc/ListObjects'
LCFIT_WWW_LOGIN = '/lcfit/lc/Login'
LCFIT_WWW_LOGIN_ERROR= '/lcfit/lc/LoginError'
LCFIT_WWW_LOGIN_FORM = '/lcfit/lc/LoginForm'
LCFIT_WWW_LOGIN_PROCESS = '/lcfit/lc/LoginProcess'
LCFIT_WWW_LOGOUT = '/lcfit/lc/Logout'
LCFIT_WWW_OBJECT_DUMP = '/lcfit/lc/ObjectDump'
LCFIT_WWW_RATES_COHERENT_PROCESS = '/lcfit/lc/ProcessRatesCoherent'
LCFIT_WWW_RATES_MF_PROCESS = '/lcfit/lc/ProcessRatesMF'
LCFIT_WWW_RATES_PROCESS = '/lcfit/lc/ProcessRates'
LCFIT_WWW_REG_FORM = '/lcfit/lc/RegistrationForm'
LCFIT_WWW_REG_PROCESS = '/lcfit/lc/RegistrationProcess'

LCFIT_PREV_PEND_ERROR_PAGE='/RegistrationError-PendingUsername.html'
LCFIT_PREV_REG_ERROR_PAGE='/RegistrationError-RegisteredUsername.html'

## Important filespace stuff
APACHEFILEROOT = '/var/www/localhost/htdocs'
mypath = os.path.realpath(__file__.rstrip("c"))
mypathL = mypath.split(os.sep)[1:-2]
LCFIT_BASE = os.path.normpath(os.path.join(os.sep, *mypathL)) + '/INTERNET_APPLICATION'
LCFIT_TEMPLATEDIR = LCFIT_BASE + '/TEMPLATES'	# Where the templates for the webpages live
LCFIT_DATADIR = APACHEFILEROOT + '/larry-data' # Where the temporary 

## Polymorphic components of important objects.
## Also just plain naming conventions and randomalia
LCFIT_IMAGES_DICT_POLYMORPHIC_COMPONENT = "imagesDict"
LCFIT_INTERNAL_ID_POLYMORPHIC_COMPONENT = "LcID"
LCFIT_LCDATBASE_POLYMORPHIC_COMPONENT = "lcdb"
LCFIT_FEMALE = 'female' 				# Use when you need a flag for female
LCFIT_MALE = 'male'						# ditto (male)
LCFIT_COMBINED = 'combined'				# ditto (female)
LCFIT_INF_NMX_REPLACEMENT = 1.0

## Convenient age data
LCFIT_AGES = N.array([0,1,5,10,15,20,25,30,35,40,45,
					  50,55,60,65,70,75,80,85,90,95,100,105,110], N.int16)
LCFIT_AGE_INDICES = dict(zip(LCFIT_AGES, range(0, len(LCFIT_AGES))))
LCFIT_DEFAULT_NO_AGEWIDTHS = 24 		# 0-1, 1-4, 5-9, ..., 110+
LCFIT_DEFAULT_AGEWIDTH = 5 				# except for first two....
LCFIT_CG_CLOSE_AGE = 110
LCFIT_SSA_5m105_DIFF = {80:0.421, 85:0.300, 90:0.200, 95:0.100, 100:0.050, 105:0.0, 110:-0.100, 115:-0.200}
LCFIT_PROJECTION_WIDTH = 1

## Mortality Extension stuff
LCFIT_DEFAULT_EXTENSION_METHOD = 'mxExtend_Boe'	##'mxExtend_Boe' 'mxExtend_CGNan'
LCFIT_DEFAULT_AGE_CUTOFF = 80          # Last age for which we use empirical data, extend if older than this, eg 85 and older

## Ages at which we will graph lnmx against year # LCFIT_AGES[:-3][::-1]
LCFIT_LOGNMX_GRAPHIC_AGES = [0, 1, 5, 20, 40, 60, 80, 95]	
for age in LCFIT_LOGNMX_GRAPHIC_AGES:
	assert age in LCFIT_AGES, "Unallowed age for graphics: %f:" % age

## Things not to put in the data dump
LCFIT_NOTWANTED_ATTRIBUTE_DUMPS = {'imagesDict':0, 'rates_text':0}

## String patterns for input verification
# spaces year spaces age-width spaces rates spaces rates spaces rates spaces
LCFIT_HMD_ROW_RE = re.compile("^\s*\d{4}\s+[0-9-+]{1,7}\s+[0-9.]+\s+[0-9.]+\s+[0-9.]+\s*$")
LCFIT_END_WS_RE = re.compile("(\n+$)|\r")	# Use this re to split on whitespace
LCFIT_TAIL_WS_RE = re.compile("\s+$")	# strip tail whitespace
LCFIT_HEAD_WS_RE = re.compile("^\s+")	# strip head whitespace
LCFIT_EMPTY_ROW_RE = re.compile("^\s*[nN][aA]\s*$")	# For rows that represent missing years of data
LCFIT_NONALLOWED_NUMBER_PATTERN = "[^\s0-9.eE-]+" # Non-allowed values for table input in form
LCFIT_EMPTY_ALL_RE = re.compile("^\s*$") # Forms with empty data (possible whitespace garbage)
LCFIT_COMMENT_LINE_RE = re.compile("^\s*#.*$") # Strips comments - Use on individual lines -- not on entire text
LCFIT_COMMENT_TRAILING_RE = re.compile("#.*$") # Strips comments - 
LCFIT_WS = re.compile("^\s*$")

LCFIT_FIELDSEP = '\t'
LCFIT_ROWSEP = '\n'
LCFIT_STANZASEP = '\n\n'

## Parameter for forms for creation of LcSinglePop object
## Confidence interval stuff
LCFIT_POSSIBLE_CONFIDENCE_INTERVALS = [.8, .9, .95, .98, .99]
LCFIT_DEFAULT_CONFIDENCE_INTERVAL = .95
LCFIT_CONFIDENCE_INTERVAL = .95
LCFIT_P_VAL= 1 - LCFIT_CONFIDENCE_INTERVAL
LCFIT_PERCENTILES = N.array([0.0, LCFIT_P_VAL/2 , .5, 1.0-(LCFIT_P_VAL/2), 1.0])
# XXXX LCFIT_ZSCORE = STD.norm.ppf(LCFIT_CONFIDENCE_INTERVAL + LCFIT_P_VAL/2)
LCFIT_ZSCORE = lcfitz(LCFIT_CONFIDENCE_INTERVAL + LCFIT_P_VAL/2)

## Parameter for age after which use Kanisto/CG/whatever
LCFIT_POSSIBLE_AGE_CUTOFFS = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110]

LCFIT_POSSIBLE_NUMRUNS = [5, 10, 20, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000]
LCFIT_DEFAULT_NUMRUNS = 20

LCFIT_POSSIBLE_STEPS_FORWARD = [5, 10, 25, 45, 46, 47, 48, 49, 50, 75, 100]
LCFIT_DEFAULT_STEPS_FORWARD = 20

## Databse
LCFIT_DBNAME = 'larrydb'

## Other Constants
LCFIT_IMAGE_FORMAT = 'png'

## Miscellaneious
LCFIT_NULL_NUMBER = -999999
LCFIT_REALLY_BIG_NUMBER = 100000.0
EMAIL = LCFIT_ADMIN_EMAIL

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
							LCFIT_WWW_LOGIN_FORM
LcSessionExceptionRedirect = LCFIT_WWW_LOGIN_ERROR + \
							 '?' + LCFIT_ERROR_MESSAGE_KEY + \
							 '=' + LcSessionExceptionMessage

# Stuff to display a database error nicely
LcDataExceptionRedirect = LCFIT_WWW_INDEX + \
						  '?' + LCFIT_ERROR_MESSAGE_KEY + \
						  '=' + "Something weird happened with the database"

def make_LcDataExceptionRedirect_disconnect(mess=None):
	return LCFIT_WWW_INDEX + \
		   '?' + LCFIT_ERROR_MESSAGE_KEY + \
		   '=' + "Something weird happened with the database: \"%s\"" % mess

def make_LcDataExceptionRedirect(objectId = None):
	if objectId:
		return LCFIT_WWW_INDEX + \
			   '?' + LCFIT_ERROR_MESSAGE_KEY + \
			   '=' + 'Unknown object serial number: %s.' % objectId

# Exception that doesn't get caught
class FooException(Exception):
	def __init__ (self, mess=None):
		self.mess = mess
		return
	def __str__(self):
		return "FooException: %s" % self.mess
	pass


