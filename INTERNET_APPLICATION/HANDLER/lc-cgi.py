#!/usr/bin/env python
'''
This file dispatches the code that makes up the LCFIT application.
Every variable defined in this file that has a __call__ method
corresponds to a page and is run like a function with session and form
information passed to it, and writes to the stream or redirects before
it returns.

When you see something like:

TaskH['index'] = LcPageObjects.LcIndex(formTemplate=LCFIT_TEMPLATEDIR + "/Index.tmpl")
 
what that means is that the variable TaskH['index'] holds a class that "walks
like and talks like" a function.  It will be called as Index(session,
form).  There is both a return value and an output stream.

When there are multiple templates passed to the instantiating thing,
usually one of them is "inside" the other.  This is tricky - maybe too
tricky - but better comments should make it easier to understand.

This file is simlinked from the apache tree. 
'''

## back to my old friend cgi...
import cgi, cgitb
cgitb.enable()
import Cookie

#### standard imports
import sys, logging, os, os.path

## Set up library path to relative to current, moveable directory tree
mypath = os.path.realpath(__file__.rstrip("c"))
mypathL = mypath.split(os.sep)[1:-2]
LCFIT_LIBRARY_PATH = os.path.normpath(os.path.join(os.sep, *mypathL))
sys.path.append(LCFIT_LIBRARY_PATH)  

## Import LcConfig, which includes lots of stuff -- modules, logging thing, constants
from LcConfig import *

## Tell the world we are operational
#lcfitlogger.debug("lc.py: at the top. file=%s" % mypath)

## import template languae
import Cheetah.Template as Template

## set up matplotlib and util module
os.environ['HOME'] = LCFIT_DATADIR 

## import basic LCFIT modules
import LcUtil                   # stuff, incl. lifetable
import LcPageObjects            # display pages


# Import database module and establish db connection 
import LcDB
try:
    lcdb = LcDB.LcObjDB(LCFIT_DBNAME)
except Exception, e:
    lcfitlogger.critical(str(e))
    util.redirect(req, "http://lcfit.demog.berkeley.edu")
    raise
    exit

#####################################################
### Set up the various pages in a dispatch hash 
#####################################################
TaskH = {}
TaskH['registration'] = \
    LcPageObjects.LcRegistrationForm(formTemplate=LCFIT_TEMPLATEDIR + '/RegistrationForm.tmpl', 
                                     title='LCFIT_ Registration Form')
TaskH['registrationprocess']  = \
    LcPageObjects.LcRegistrationProcess(lcdb=lcdb, 
                                        errorTemplate=LCFIT_TEMPLATEDIR + '/Error.tmpl', 
                                        redirectTarget='../../Registration-ThankYou.html') 
TaskH['login'] = \
    LcPageObjects.LcLoginForm(formTemplate=LCFIT_TEMPLATEDIR + '/LoginForm.tmpl', 
                              title='LCFIT Login Form')
TaskH['loginprocess'] = \
    LcPageObjects.LcLoginProcess(redirectTarget=LCFIT_WWW_LIST_OBJECTS, 
                                 messageTemplate=LCFIT_TEMPLATEDIR + '/LoginError.tmpl', 
                                 lcdb=lcdb)

## *********************************************************************************
## Run the cgi   
## **********************************************************************************/
if __name__ == '__main__':
    ## set up form
    form = cgi.FieldStorage()

    ## set up session 
    if os.environ.has_key("HTTP_COOKIE"):
        session = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
    else:
        session = None

    ## dispatch based on task field in form
    if form.has_key("task"):
        task = form["task"].value.lower()
        if TaskH.has_key(task):
            TaskH[task](session, form)
        else:
            print("Content-type:text/html\n\nUnkown task: %s\n" % task) 
    else:
        print("Content-type:text/html\n\nNo task parameter set\n")






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
