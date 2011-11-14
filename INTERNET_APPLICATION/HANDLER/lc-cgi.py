#!/usr/bin/env python
'''
This file dispatches the code that makes up the LCFIT application.
Every variable defined in this file that has a __call__ method
corresponds to a page and is run like a function with session and form
information passed to it, and writes to the stream or redirects before
it returns.

When you see something like:

TaskH['index'] = LcPageObjects.LcIndex(formTemplate=LCFIT_TEMPLATEDIR
+ "/Index.tmpl")
 
what that means is that the variable TaskH['index'] holds a class that
"walks like and talks like" a function.  It will be called as
Index(session, form).  This duck typed function gives both a return
value and an output stream, though the return value is ignored
currently (2011-10-22).

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
import sys, logging, os, os.path, traceback

## Set up library path to relative to current, moveable directory tree
mypath = os.path.realpath(__file__.rstrip("c"))
mypathL = mypath.split(os.sep)[1:-2]
LCFIT_LIBRARY_PATH = os.path.normpath(os.path.join(os.sep, *mypathL))
sys.path.append(LCFIT_LIBRARY_PATH)  

## Import LcConfig, which includes lots of stuff -- modules, logging
## thing, constants
from LcConfig import *

## Tell the world we are operational
lcfitlogger.debug("lc.py: at the top. file=%s" % mypath)

## import template languae
import Cheetah.Template as Template

## set up matplotlib and util module
os.environ['HOME'] = LCFIT_DATADIR 

## import basic LCFIT modules
import LcUtil                   # stuff, incl. lifetable
import LcPageObjects            # display pages
import LcSinglePopObject        # simple object
import LcCoherentPopObject
import LcMFPopObject
import LcHMDObject

# Import database module and establish db connection 
import LcDB
try:
    lcdb = LcDB.LcObjDB(LCFIT_DBNAME)
except Exception, e:
    lcfitlogger.critical(str(e))
    raise


#####################################################
### Set up the various pages in a dispatch hash 
#####################################################
TaskH = {}
TaskH['registration'] = LcPageObjects.LcRegistrationForm(
    formTemplate=LCFIT_TEMPLATEDIR + '/RegistrationForm.tmpl', 
    title='LCFIT_ Registration Form')

TaskH['registrationprocess']  = LcPageObjects.LcRegistrationProcess(
    lcdb=lcdb, 
    errorTemplate=LCFIT_TEMPLATEDIR + '/Error.tmpl', 
    redirectTarget='../../Registration-ThankYou.html') 

TaskH['login'] = LcPageObjects.LcLoginForm(
    formTemplate=LCFIT_TEMPLATEDIR + '/LoginForm.tmpl', 
    title='LCFIT Login Form')

TaskH['loginprocess'] = LcPageObjects.LcLoginProcess(
    redirectTarget=LCFIT_WWW_LIST_OBJECTS, 
    messageTemplate=LCFIT_TEMPLATEDIR + '/LoginError.tmpl', 
    lcdb=lcdb)

TaskH['listobjects'] = LcPageObjects.LcList(
    lcdb=lcdb,
    navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
    objectListTemplate = LCFIT_TEMPLATEDIR + '/ObjectList.tmpl',
    title='LCFIT Object List')

TaskH['showresults'] = LcPageObjects.LcDisplay(
    lcdb=lcdb, navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl')

TaskH['displayimage'] = LcPageObjects.LcDisplayImage(lcdb=lcdb)

TaskH['inputrates'] = LcPageObjects.LcForm(
    redirectTarget='lc-cgi.py?task=processrates', 
    formTemplate=LCFIT_TEMPLATEDIR + '/InputRates.tmpl',
    navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
    lcdb = lcdb,
    title='LCFIT Death Rate Input (Single Sex)')

TaskH['processrates'] = LcPageObjects.LcProcess(
    targetClass=LcSinglePopObject.LcSinglePop,
    redirectTarget=LCFIT_WWW_LIST_OBJECTS,
    lcdb=lcdb)

TaskH['inputhmd'] = LcPageObjects.LcForm(
    redirectTarget='lc-cgi.py?task=processhmd',
    formTemplate=LCFIT_TEMPLATEDIR + '/InputHMD.tmpl',
    navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
    lcdb = lcdb,
    title='LCFIT HMD Converter')

TaskH['processhmd']= LcPageObjects.LcProcess(
    targetClass=LcHMDObject.HMD,
    redirectTarget=LCFIT_WWW_LIST_OBJECTS,
    lcdb=lcdb)

TaskH['inputratescoherent'] = LcPageObjects.LcForm(
    redirectTarget='lc-cgi.py?task=processratescoherent',
    formTemplate=LCFIT_TEMPLATEDIR + '/InputRatesCoherent.tmpl',
    navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
    lcdb = lcdb,
    title='LCFIT Death Rate Input (Coherent)')

TaskH['processratescoherent'] = LcPageObjects.LcProcess(
    targetClass=LcCoherentPopObject.LcCoherentPop,
    redirectTarget=LCFIT_WWW_LIST_OBJECTS,
    lcdb=lcdb)

TaskH['inputratesmf'] = LcPageObjects.LcForm(
    redirectTarget='lc-cgi.py?task=processratesmf',
    formTemplate=LCFIT_TEMPLATEDIR + '/InputRatesMF.tmpl',
    navTemplate=LCFIT_TEMPLATEDIR + '/Application.tmpl',
    lcdb = lcdb,
    title='LCFIT Death Rate Input (MF)')

TaskH['processratesmf'] = LcPageObjects.LcProcess(
    targetClass=LcMFPopObject.LcMFPop,
    redirectTarget=LCFIT_WWW_LIST_OBJECTS,
    lcdb=lcdb)

TaskH['deleteobject'] = LcPageObjects.LcDelete(
    lcdb=lcdb,
    redirectTarget=LCFIT_WWW_LIST_OBJECTS)

TaskH['objectdump'] = LcPageObjects.LcDumpText(lcdb=lcdb)

## ***********************************************************************
## Run the cgi   
## ***********************************************************************/
if __name__ == '__main__':
    ## set up form
    form = cgi.FieldStorage()

    ## set up session 
    if os.environ.has_key("HTTP_COOKIE"):
        session = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
    else:
        session = None

    ## dispatch based on task field in form, catch exceptions
    try:
        if form.has_key("task"):
            task = form["task"].value.lower()
            if TaskH.has_key(task):
                TaskH[task](session, form)
            else:
                sys.stdout.write(session.output().strip() + "\n")
                sys.stdout.write("Content-type:text/html\n\n")
                sys.stdout.write("<b>Unknown task: %s</b>\n" % task) 
        else:
            sys.stdout.write("Content-type:text/html\n\nNo task parameter set\n")
    except LcException, e:
        if session is not None:
            sys.stdout.write(session.output().strip() + "\n") 
        sys.stdout.write("Content-type: text/html\n\n")
        sys.stdout.write("<b>Error:</b> %s<br>" % repr(e))
        sys.stdout.flush()
        exit(0)
    except Exception:
        # catch exception, send email, re-raise
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tblist = traceback.format_exception(exc_type, exc_value, exc_traceback)
        mserver = smtplib.SMTP(LCFIT_SMTP)
        mserver.set_debuglevel(0)
        headers = "From: %s\r\nSubject: %s\r\n\r\n" % \
            ('LCFIT', 'LCFIT -- Bad Exception: %s' % time.asctime())
        message = '\n'.join(tblist)
        mserver.sendmail(from_addr='no-reply@localhost', 
                         to_addrs=['lcfit@demog.berkeley.edu'],
                         msg=headers+message)
        mserver.quit()
        raise
