## LCFIT
'''
This file dispatches the code that makes up the LCFIT application.
Every variable defined in this file that has a __call__ method
corresponds to a page and is automatically run and passed parameters
that appear through GET and POST (thanks to mod_python).  Normally,
each page would be defined by using a "def():", but in this app, each
object has a __call__ method, so it looks like a function to mod_python.

When you see something like:

Index = LcPageObjects.LcIndex(formTemplate=LARRYTEMPLATEDIR + "/Index.tmpl")
 
what that means is that the variable Index holds a class that "walks
like and talks like" a function.  This function is run when the user
browses to $HOST/lcfit/lc/index/; this function is also passed any
parameters that might be sent as GET or POST data.  The formTemplate
(and other parameters) defines some state of the object that is
retained between calls.  E.G., the application will keep using this
file to display the pages, but the pages will remember that they have
a given template.

When there are multiple templates passed to the instantiating thing,
usually one of them is "inside" the other.  This is tricky - maybe too
tricky - but better comments should make it easier to understand.

Now this is the only file that lives in the apache tree -- the others
now live in te LARRY_LIBRARY_PATH.  This was done so that there is
less security risk, cleaner development, etc.

'''


#############################################
## Infrastructure imports
#############################################

import sys
LARRY_LIBRARY_PATH='/home/webbs/lcfit.git/INTERNET_APPLICATION'	# this is where all the executable files live
sys.path.append(LARRY_LIBRARY_PATH)		# This tells us how to find these executables

# Constants, system modules, etc
from LcConfig import *
syslog.syslog('lc.py executing.')

## Import mod_python infrastructure
from mod_python import apache
from mod_python.Session import Session
from mod_python import util

import Cheetah.Template as Template
import cProfile

os.environ['HOME'] = LARRYDATADIR # Need to provide a directory for pylab to cache fonts

import LcUtil							# Utility functions, including lifetable
import LcPageObjects # Module provides the objects which have __call__
                     # and display pages from URLs

# Modules which provide the objects that store the all the forecast
# data.  These are the "meat" of the application, holding everything,
# doing all the SVDs and other analyses, and (as pickled binaries)
# storing each the results for each forecast.
import LcSinglePopObject
import LcMFPopObject
import LcCoherentPopObject
import LcHMDObject

# Import the module that handles the database connection and assign
# its reference to a variable; this reference will be passed to all
# objects that might need a database connection.  Note that when we
# instantiate it here, we are establishing a connection to the
# Postgres DB as part of that instantiation (see the module code for
# details under __init__).
import LcDB
try:
	lcdb = LcDB.LcObjDB(LARRYDBNAME)
except Exception, e:
	syslog.syslog(str(e))
	util.redirect(req, "http://www.yahoo.com")
	raise
	exit

############ Pages ###########################

"""Note that these are all 'callable' objects, so modpython runs their
__call__ method and prints what ever that prints as the server is
running.  What we see below is the pages' initialization (templates,
database connections, etc).  See above."""

############################### General navigation #######################

#####################################################
### Index, with alias to an upper case page name ####
#####################################################
Index = LcPageObjects.LcIndex(formTemplate=LARRYTEMPLATEDIR + '/Index.tmpl',
							  navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl',
							  lcdb=lcdb,
							  title='LCFIT Index')
index = Index

#####################################################
### Login stuff ##
#####################################################

LoginForm = LcPageObjects.LcLoginForm(
formTemplate=LARRYTEMPLATEDIR + '/LoginForm.tmpl',
	title='LCFIT Login Form')
LoginProcess = LcPageObjects.LcLoginProcess(
	redirectTarget='index',
	messageTemplate=LARRYTEMPLATEDIR + '/LoginError.tmpl',
	lcdb = lcdb)
Login = LoginForm

Logout = LcPageObjects.LcLogout(
	lcdb=lcdb, redirectTarget='../../') # this redirect puts at the top of the html tree


#####################################################
### Registration ###
#####################################################
Registration = LcPageObjects.LcRegistrationForm(formTemplate=LARRYTEMPLATEDIR + '/RegistrationForm.tmpl',
												title='LCFIT Registration Form')
RegistrationProcess = LcPageObjects.LcRegistrationProcess(lcdb=lcdb, errorTemplate=LARRYTEMPLATEDIR + \
														  '/Error.tmpl', redirectTarget='../../Registration-ThankYou.html') 

#####################################################
### Show the __str__ representation of an object within the navigation/Application template
#####################################################
ShowResults = LcPageObjects.LcDisplay(lcdb=lcdb, navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl')

#####################################################
### List all of the objects within the navigation/Application template
#####################################################
ListObjects = LcPageObjects.LcList(lcdb=lcdb,
								   navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl',
								   objectListTemplate = LARRYTEMPLATEDIR + '/ObjectList.tmpl',
								   title='LCFIT Object List')
## Hack to enable profiling 
def ListObjectsProfile(req):
	ret = cProfile.runctx('ListObjects(req)', globals(), locals(), filename='/tmp/ListObjectProf')
	return ret

#####################################################
### Delete an object
#####################################################
DeleteObject = LcPageObjects.LcDelete(lcdb=lcdb,
									  redirectTarget=LARRY_WWW_LIST_OBJECTS)

#####################################################
### Displays an image, with no regard for which forecast it belongs too
#####################################################
image = LcPageObjects.LcDisplayImage(lcdb=lcdb)

#####################################################
### Dump the data on an object
#####################################################
ObjectDump = LcPageObjects.LcDumpText(lcdb=lcdb)

#####################################################
### Input single population rates
#####################################################
InputRates=LcPageObjects.LcForm(redirectTarget='ProcessRates',
								formTemplate=LARRYTEMPLATEDIR + '/InputRates.tmpl',
								navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl',
								lcdb = lcdb,
								title='LCFIT Death Rate Input (Single Sex)')
#####################################################
## Input M & F rates
#####################################################
InputRatesMF=LcPageObjects.LcForm(redirectTarget='ProcessRatesMF',
								formTemplate=LARRYTEMPLATEDIR + '/InputRatesMF.tmpl',
								navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl',
								lcdb = lcdb,
								title='LCFIT Death Rate Input (MF)')

#####################################################
## Input coherent rates
#####################################################
InputRatesCoherent=LcPageObjects.LcForm(redirectTarget='ProcessRatesCoherent',
										formTemplate=LARRYTEMPLATEDIR + '/InputRatesCoherent.tmpl',
										navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl',
										lcdb = lcdb,
										title='LCFIT Death Rate Input (Coherent)')

#####################################################
## Process single populaton rates, store big object result,  and redirect to ListObjects
#####################################################
ProcessRates_ = LcPageObjects.LcProcess(targetClass=LcSinglePopObject.LcSinglePop,
									   redirectTarget=LARRY_WWW_LIST_OBJECTS,
									   lcdb=lcdb)
# Profiling hack
def ProcessRates(req):					
	if LARRY_DO_PROFILE:
		ret = cProfile.runctx('ProcessRates_(req)',
							  globals(), locals(), filename='/tmp/ProcessRatesSingleProf')
		return ret
	else:
		return ProcessRates_(req)
	return

#####################################################
## Process male/female rates
#####################################################
ProcessRatesMF = LcPageObjects.LcProcess(targetClass=LcMFPopObject.LcMFPop,
										 redirectTarget=LARRY_WWW_LIST_OBJECTS,
										 lcdb=lcdb)

#####################################################
## Process coherent sets of rates
#####################################################
ProcessRatesCoherent_ = LcPageObjects.LcProcess(targetClass=LcCoherentPopObject.LcCoherentPop,
												redirectTarget=LARRY_WWW_LIST_OBJECTS,
												lcdb=lcdb)
# Profiling hack
def ProcessRatesCoherent(req):					
	if LARRY_DO_PROFILE:
		ret = cProfile.runctx('ProcessRatesCoherent_(req)',
							  globals(), locals(), filename='/tmp/ProcessRatesCoherentProf')
		return ret
	else:
		return ProcessRatesCoherent_(req)
	return


############################### HMD converter #########################
## Get the rates
#####################################################
InputHMD = LcPageObjects.LcForm(redirectTarget='ProcessHMD',
								formTemplate=LARRYTEMPLATEDIR + '/InputHMD.tmpl',
								navTemplate=LARRYTEMPLATEDIR + '/Application.tmpl',
								lcdb = lcdb,
								title='LCFIT HMD Converter')

#####################################################
## Process HMD rates and redirect to ListObjects
#####################################################
ProcessHMD= LcPageObjects.LcProcess(targetClass=LcHMDObject.HMD,
									redirectTarget=LARRY_WWW_LIST_OBJECTS,
									lcdb=lcdb)

#####################################################
## Error Infrastructure
#####################################################
LoginError = LcPageObjects.LcError(template=LARRYTEMPLATEDIR+'/Error.tmpl', title="LCFIT Login Error Messages")
Error = LcPageObjects.LcError(template=LARRYTEMPLATEDIR+'/Error.tmpl', title="LCFIT Misc Error Messages")

#################################################
## main procedure.
## Should never get here, as this code is just for a library
#################################################
if __name__ == '__main__':
    pass
