#!/usr/bin/env python
'''
This file dispatches the code that makes up the LCFIT application.
Every variable defined in this file that has a __call__ method
corresponds to a page and is run like a function with session and form
information passed to it, and writes to the stream or redirects before
it returns.

When you see something like:

Index = LcPageObjects.LcIndex(formTemplate=LCFIT_TEMPLATEDIR + "/Index.tmpl")
 
what that means is that the variable Index holds a class that "walks
like and talks like" a function.  It will be called as Index(session,
form).  There is both a return value and an output stream.

When there are multiple templates passed to the instantiating thing,
usually one of them is "inside" the other.  This is tricky - maybe too
tricky - but better comments should make it easier to understand.

This file is simlinked from the apache tree. 
'''

#### standard imports
import sys
import logging
import os
import os.path

#############################################
## Infrastructure imports
#############################################

## Import libraries relative to hard location of lc.py -- have to
## recreate it based
#LCFIT_LIBRARY_PATH='/home/webbs/lcfit.git/INTERNET_APPLICATION'    # where all the executable files live
mypath = os.path.realpath(__file__.rstrip("c"))
mypathL = mypath.split(os.sep)[1:-2]
LCFIT_LIBRARY_PATH = os.path.normpath(os.path.join(os.sep, *mypathL))
sys.path.append(LCFIT_LIBRARY_PATH)     # This tells us how to find these executables

## Import LcConfig, which includes lots of stuff -- modules, logging thing, constants
from LcConfig import *

## Tell the world we are operational
#lcfitlogger.debug("lc.py: at the top. file=%s" % mypath)


import Cheetah.Template as Template
os.environ['HOME'] = LCFIT_DATADIR # Need to provide a directory for pylab to cache fonts
import LcUtil        # Utility functions, including lifetable
import LcPageObjects # Module provides the objects which have __call__
                     # and display pages from URLs

# Modules which provide the objects that store the all the forecast
# data.  These are the "meat" of the application, holding everything,
# doing all the SVDs and other analyses, and (as pickled binaries)
# storing each the results for each forecast.


# Import the module that handles the database connection and assign
# its reference to a variable; this reference will be passed to all
# objects that might need a database connection.  Note that when we
# instantiate it here, we are establishing a connection to the
# Postgres DB as part of that instantiation (see the module code for
# details under __init__).
import LcDB
try:
    lcdb = LcDB.LcObjDB(LCFIT_DBNAME)
except Exception, e:
    lcfitlogger.critical(str(e))
    util.redirect(req, "http://lcfit.demog.berkeley.edu")
    raise
    exit

#####################################################
### Registration Page ###
#####################################################
Registration = LcPageObjects.LcRegistrationForm(formTemplate=LCFIT_TEMPLATEDIR + '/RegistrationForm.tmpl', 
    title='LCFIT_ Registration Form')
RegistrationProcess = LcPageObjects.LcRegistrationProcess(lcdb=lcdb, errorTemplate=LCFIT_TEMPLATEDIR + \
    '/Error.tmpl', redirectTarget='../../Registration-ThankYou.html') 

if __name__ == '__main__':
    print ("content-type: text/html\n\n")
    print ("let the cgi begin!")
    exit
## the following should be imported by the appropriate page object if appropriate
#import LcSinglePopObject
#import LcMFPopObject
#import LcCoherentPopObject
#import LcHMDObject


# ############################### General navigation #######################

# #####################################################
# ### Index, with alias to an upper case page name ####
# #####################################################
# Index = LcPageObjects.LcIndex(formTemplate=LCFIT_TEMPLATEDIR + '/Index.tmpl',
#                             navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
#                             lcdb=lcdb,
#                             title='LCFIT Index')
# index = Index

# #####################################################
# ### Login stuff ##
# #####################################################

# LoginForm = LcPageObjects.LcLoginForm(
#   formTemplate=LCFIT_TEMPLATEDIR + '/LoginForm.tmpl',
#   title='LCFIT Login Form')
# LoginProcess = LcPageObjects.LcLoginProcess(
#   redirectTarget='index',
#   messageTemplate=LCFIT_TEMPLATEDIR + '/LoginError.tmpl',
#   lcdb = lcdb)
# Login = LoginForm

# Logout = LcPageObjects.LcLogout(
#   lcdb=lcdb, redirectTarget='../../') # this redirect puts at the top of the html tree

#####################################################
### Show the __str__ representation of an object within the navigation/Application template
#####################################################
# ShowResults = LcPageObjects.LcDisplay(lcdb=lcdb, navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl')

# #####################################################
# ### List all of the objects within the navigation/Application template
# #####################################################
# ListObjects = LcPageObjects.LcList(lcdb=lcdb,
#                                  navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
#                                  objectListTemplate = LCFIT_TEMPLATEDIR + '/ObjectList.tmpl',
#                                  title='LCFIT Object List')

# #####################################################
# ### Delete an object
# #####################################################
# DeleteObject = LcPageObjects.LcDelete(lcdb=lcdb,
#                                     redirectTarget=LCFIT_WWW_LIST_OBJECTS)

# #####################################################
# ### Displays an image, with no regard for which forecast it belongs too
# #####################################################
# image = LcPageObjects.LcDisplayImage(lcdb=lcdb)

# #####################################################
# ### Dump the data on an object
# #####################################################
# ObjectDump = LcPageObjects.LcDumpText(lcdb=lcdb)

# #####################################################
# ### Input single population rates
# #####################################################
# InputRates=LcPageObjects.LcForm(redirectTarget='ProcessRates',
#                               formTemplate=LCFIT_TEMPLATEDIR + '/InputRates.tmpl',
#                               navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
#                               lcdb = lcdb,
#                               title='LCFIT Death Rate Input (Single Sex)')

# #####################################################
# ## Input M & F rates
# #####################################################
# InputRatesMF=LcPageObjects.LcForm(redirectTarget='ProcessRatesMF',
#                               formTemplate=LCFIT_TEMPLATEDIR + '/InputRatesMF.tmpl',
#                               navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
#                               lcdb = lcdb,
#                               title='LCFIT Death Rate Input (MF)')

# #####################################################
# ## Input coherent rates
# #####################################################
# InputRatesCoherent=LcPageObjects.LcForm(redirectTarget='ProcessRatesCoherent',
#                                       formTemplate=LCFIT_TEMPLATEDIR + '/InputRatesCoherent.tmpl',
#                                       navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
#                                       lcdb = lcdb,
#                                       title='LCFIT Death Rate Input (Coherent)')

# #####################################################
# ## Process single populaton rates, store big object result,  and redirect to ListObjects
# #####################################################
# ProcessRates = LcPageObjects.LcProcess(targetClass=LcSinglePopObject.LcSinglePop,
#                                      redirectTarget=LCFIT_WWW_LIST_OBJECTS,
#                                      lcdb=lcdb)

# #####################################################
# ## Process male/female rates
# #####################################################
# ProcessRatesMF = LcPageObjects.LcProcess(targetClass=LcMFPopObject.LcMFPop,
#                                        redirectTarget=LCFIT_WWW_LIST_OBJECTS,
#                                        lcdb=lcdb)

# #####################################################
# ## Process coherent sets of rates
# #####################################################
# ProcessRatesCoherent = LcPageObjects.LcProcess(targetClass=LcCoherentPopObject.LcCoherentPop,
#                                               redirectTarget=LCFIT_WWW_LIST_OBJECTS,
#                                               lcdb=lcdb)

# ############################### HMD converter #########################
# ## Get the rates
# #####################################################
# InputHMD = LcPageObjects.LcForm(redirectTarget='ProcessHMD',
#                               formTemplate=LCFIT_TEMPLATEDIR + '/InputHMD.tmpl',
#                               navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
#                               lcdb = lcdb,
#                               title='LCFIT HMD Converter')

# #####################################################
# ## Process HMD rates and redirect to ListObjects
# #####################################################
# ProcessHMD= LcPageObjects.LcProcess(targetClass=LcHMDObject.HMD,
#                                   redirectTarget=LCFIT_WWW_LIST_OBJECTS,
#                                   lcdb=lcdb)

# #####################################################
# ## Error Infrastructure
# #####################################################
# LoginError = LcPageObjects.LcError(template=LCFIT_TEMPLATEDIR+'/Error.tmpl', title="LCFIT_ Login Error Messages")
# Error = LcPageObjects.LcError(template=LCFIT_TEMPLATEDIR+'/Error.tmpl', title="LCFIT Misc Error Messages")

#################################################
## main procedure.
## Should never get here, as this code is just for a library
#################################################
