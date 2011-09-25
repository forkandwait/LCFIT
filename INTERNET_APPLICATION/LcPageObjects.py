'''
The classes in this module define the processes that make up LcFIT.
Each process corresponds to a page more or less.  They don"t hold
state past their execution, but rather just store stuff and then go to
another page.

The basic cycle is list -> form -> process (invisible) -> list.  There
are "form" pages, which provide a page to enter data.  These "form"
pages send their data to "process" pages, which do whatever they do
(forecasts and storing in the database, usually).  These "process"
pages then redirect to the "ListObjects" page, which is kind of
nuetral, with no state, showing all the objects and their results
already in the database; from here a user can either to go to another
"form" page or to a "display" page for a single object.

Also, the pages that handle forecasting (single, mf, coherent) inherit
from LcPage which does the validation of login session stuff.  That
might be confusing.  In Python the ()"s in the class definition are
how you know you are inheriting.
'''

import Cookie
import cgi

from LcLog import lcfitlogger
from LcConfig import *
import LcConfig                         # So that the LcConfig can be passed to the template searchlist

import LcExtension
import LcAnnotation
import LcCoherentPopObject
import LcConfig
import LcDB
import LcExtension
import LcHMDObject
import LcMFPopObject
import LcPageObjects
import LcSinglePopObject

import Cheetah.Template as Template
sys.path.append(os.getcwd())
from LcUtil import Diagnose as D
from LcUtil import Warn as W


## simple thing for writing
def httpwrite(content=None, headers=None, cookies=None):
    # check something worthwhile to output
    if headers is None and content is None:                # 0-0/1-0
        raise Exception("neither content nor headers?")

    # set up empty cookie and header for logic simplification
    if cookies is None:
        cookies = Cookie.SimpleCookie()
    if headers is None:
        headers = ''
        
    if headers is not None and content is None:            # 1-0/1-0
        # headers only -- keep cookies and headers
        sys.stdout.write(cookies.output())
        sys.stdout.write(headers)
        sys.stdout.flush()        
    
    elif content is not None:          # 0/1-0/1-1
        # content present -- do everything
        sys.stdout.write(cookies.output())
        sys.stdout.write("Content-type:text/html\n\n")
        sys.stdout.write(content)
        sys.stdout.flush()

## Import mod_python infrastructure
if __name__ != '__main__':
    pass

def f2d(form):
    """Convert a mod_python form to a simple hash"""
    formData = {}
    for k in form.keys():
        formData[k] = form[k].value 
    return formData

class LcRegistrationForm:
    """
    Display a form to register users.  Takes the data and puts it in
    the database for later evaluation.
    """
    
    def __init__(self, formTemplate, title=None):
        """Assigns instance variables"""
        self.formTemplate = formTemplate
        self.title = title
            
    def __call__(self, session=None, form=None):
        """Handle the page"""

        # Build form from template ... 
        searchList = []
        searchList.append({'TITLE':self.title})
        searchList.append({'SUBMIT_TARGET':LCFIT_WWW_REG_PROCESS}) 
        searchList.append(LcConfig.__dict__)
        formTemplate = Template.Template(file=self.formTemplate, searchList = searchList,
                                                 compilerSettings={'prioritizeSearchListOverSelf' : True})

        # ... log that we are here ...
        lcfitlogger.debug('LcRegistrationForm:  __call__')
        
        # ... write and return.
        sys.stdout.write("content-type:text/html\n\n")
        sys.stdout.write(str(formTemplate))
        sys.stdout.flush()
        return(0)

class LcRegistrationProcess:
    """Puts the results in the database and redirects to a page describing the fact that registrated."""
    def __init__(self, lcdb, redirectTarget=None, title=None, errorTemplate=None):
        self.redirectTarget=redirectTarget
        self.title=title
        self.lcdb = lcdb
        self.errorTemplate = errorTemplate
        pass
    
    def __call__(self, session=None, form=None):
        """ Deal with registration data"""
        data = f2d(form)    
        
        # Log
        lcfitlogger.debug( 'LcRegistrationProcess:  __call__')
        
        ## Clean and check data, display error and return if necessary.
        for k in ['USERNAME', 'PASSWORD', 'EMAIL', 'FULLNAME', 'REASONS', 'HOWFIND', 'AFFILIATION']:
            if (not data.has_key(k)) or LCFIT_EMPTY_ALL_RE.match(data[k]): # Error
                err_mess = 'Empty strings or other bad data in form: "%s".<br>Please use the back button and correct.' % (k)
                sl = [{'TITLE':'Registration Error','LC_ERROR_MESSAGE':err_mess}]
                formTemplate = Template.Template(file=self.errorTemplate, searchList = sl,
                                                 compilerSettings={'prioritizeSearchListOverSelf' : True}) 
                sys.stdout.write("Content-type: text/html")
                sys.stdout.write(str(formTemplate))
                sys.stdout.flush()
                return(0)
            if k in ('USERNAME', 'PASSWORD'):
                data[k] = re.sub('\s*', '', data[k]) 
            data[k] = data[k].strip()
            data[k] = data[k].replace("'", "")
            
        ## Insert info into db (email will be sent by daily sweeper)
        try:
            self.lcdb.insertRegRequest(data)
        except LcDataException, e:
            lcfitlogger.error( 'Bad Registration request: %s.' % pprint.pformat(e))
            if re.match('.*pending.*', str(e)):
                sys.stdout.write("Status: 303\nLocation: %s\n\n" %  LCFIT_PREV_PEND_ERROR_PAGE)
                sys.stdout.flush()
            elif re.match('.*in-use.*', str(e)):
                sys.stdout.write("Status: 303\nLocation: %s\n\n" %  LCFIT_PREV_REG_ERROR_PAGE)
                sys.stdout.flush()
            else:
                raise

        ## Email administrator
        mserver = smtplib.SMTP(LCFIT_SMTP)
        mserver.set_debuglevel(0)
        headers = "From: %s\r\nSubject: %s\r\n\r\n" % \
                            ('LCFIT', 'LCFIT Registration Alert: %s' % time.asctime())
        message = "New user filled out registration page: \"%s\".\n\n" % data['USERNAME']
        mserver.sendmail(from_addr='no-reply@localhost', to_addrs=[EMAIL], msg=headers+message)
        mserver.quit()

        ## Redirect to a page of useful stuff
        sys.stdout.write("Status: 303\nLocation: %s\n\n" % LCFIT_REG_THX_PAGE)
        sys.stdout.flush()

        return

class LcLoginForm:
    """
    Displays a form for user login.

    It does not inherit from LcForm because of special session and DB
    interaction during initialization.
    """
    def __init__(self, formTemplate, title=None):
        """Assigns instance variables"""
        self.formTemplate = formTemplate
        self.title = title
        
    
    def __call__(self, session=None, form=None):
        """Handle the page"""

        # Log
        lcfitlogger.debug( 'LcLoginForm:  __call__')

        # Build form ... 
        searchList = []
        searchList.append({'TITLE':self.title})
        searchList.append({'SUBMIT_TARGET': LCFIT_WWW_LOGIN_PROCESS})
        searchList.append(LcConfig.__dict__)

        formTemplate = Template.Template(file=self.formTemplate, searchList = searchList,
                                         compilerSettings={'prioritizeSearchListOverSelf' : True})
        
        # ... write and return.
        httpwrite(content=str(formTemplate))
        return(0)


class LcLoginProcess:
    """
    Responsibilities:
        * Process results, starting session
        * Display appropriate error messages
        * Redirect somewhere nice
    """

    def __init__(self, redirectTarget, messageTemplate, lcdb, title=None):
        """Assigns instance variables"""
        self.redirectTarget = redirectTarget
        self.messageTemplate = messageTemplate
        self.lcdb = lcdb
        self.title = title
        
    def _hasNecessaryData(self, session=None, form=None):
        """Check to make sure all the required data for login is
        present in the form"""
        keyList = form.keys()
        
        if (LCFIT_PASSWORD_KEY not in keyList or
            form[LCFIT_PASSWORD_KEY].value == '' or
            LCFIT_USERNAME_KEY not in keyList or
            form[LCFIT_USERNAME_KEY].value == ''):
            
            W('WTF?', locals())
            return False
        else:
            return True

        formData = {}
        for k in keyList:
            formData[k] = form[k].value 
        W('Login: ', formData)
        

    def _hasValidAuth(self, session, form):
        """ Ask the database to set up a session for a valid user,
        return either True or False"""
        rval = self.lcdb.authorizeUser(form[LCFIT_USERNAME_KEY].value,
                                       form[LCFIT_PASSWORD_KEY].value,
                                       os.environ['REMOTE_ADDR'])
        if rval == False:
            return False
        else:
            return rval

    
    def __call__(self, session=None, form=None):
        """Handle the page"""
        if self._hasNecessaryData(session, form):
            # ... if authorized, use the returned ID, set session, and redirect
            authId = self._hasValidAuth(session, form)
            if type(authId) is types.IntType: 
                if session is None:
                    session = Cookie.SimpleCookie()
                session[LCFIT_SESSION_KEY] = authId
                headers = "Status: 303\nLocation: %s\n\n" % self.redirectTarget
                httpwrite(headers=headers, cookies=session, content=None)
                lcfitlogger.info( 'LcLoginProcess:  __call__.  Good auth.  Auth id: %s, username: %s.' \
                                      % (authId, form.get(LCFIT_USERNAME_KEY, 'XX')))
                return
            else:
                httpwrite(content="Could not authorize.  Go \"back\" and try again.")
                lcfitlogger.warning( 'LcLoginProcess:  __call__. Bad auth.')
                return(0)
        else:
            httpwrite(content="Incomplete Login Information.  Go \"back\" and try again.")
            lcfitlogger.warning( 'LcLoginProcess:  __call__. Incomplete data.')
            return(0)


class LcLogout:
    """Logs out of the application"""
    def __init__(self, lcdb, redirectTarget):
        self.lcdb = lcdb
        self.redirectTarget = redirectTarget

    def __call__(self, req):
        req.session = Session(req)
        if req.session.has_key(LCFIT_SESSION_KEY):
            self.lcdb.logout(req.session[LCFIT_SESSION_KEY])
            lcfitlogger.debug( 'LcLogout:  __call__.  Logging out session key: %s' % req.session[LCFIT_SESSION_KEY])
        req.session.invalidate()
        lcfitlogger.warning( 'LcLogout:  __call__.  Logging out unkown session.')
        util.redirect(req, self.redirectTarget)


class LcPage(object):
    """
    Base class for most Lc pages

    Responsibilities:
        * handle pre and post conditions before each page view, especially session management.
        * handle jumps on errors.
    """ 

    def _preCondition(self, req):
        """ Do a bunch of stuff that we always want before sending a
        page as if it is OK."""

        # Confirm session, raising appropriate errors
        # I think you can hijack a session easily ...
        req.session = Session(req)
        if req.session.is_new():
            req.session.invalidate()
            raise LcSessionException, "new session--expected initialized"
        if not req.session.has_key(LCFIT_SESSION_KEY):
            req.session.invalidate()
            raise LcSessionException, "no session id stored in cookie"
        if not self.lcdb.checkSession(req.session[LCFIT_SESSION_KEY]):
            req.session.invalidate()
            raise LcSessionException, "unable to validate session id with database"

        # .. made it!
        self.lcdb.insertPageView(req.session[LCFIT_SESSION_KEY], req.unparsed_uri, pprint.pformat(f2d(req.form)))
        return True
        
    def _postCondition(self, req, saveDict = {}):
        for key, val in saveDict.iteritems():
            req.session[key] = val
        req.session.save()
        return True

class LcIndex(LcPage):
    """The neutral, boring page with nothing on it. Probably a good
    place for announcements, whether sitewide or user specific."""
    
    def __init__(self, formTemplate, navTemplate, lcdb, title=None):
        self.formTemplate = formTemplate
        self.navTemplate = navTemplate
        self.lcdb = lcdb
        self.title = title
        
    def __call__(self, req):
        lcfitlogger.debug( 'LcIndex:  __call__.')

        try:
            self._preCondition(req) 

            # Deal with possible error messages
            if req.form.has_key(LCFIT_ERROR_MESSAGE_KEY):
                errorMessage = req.form[LCFIT_ERROR_MESSAGE_KEY].value
            else:
                errorMessage = None
            searchList = [{LCFIT_ERROR_MESSAGE_PLACHOLDER : errorMessage,
                          'request':req, 'session':req.session, 'lcdb':self.lcdb,
                           LCFIT_TITLE_PLACEHOLDER:self.title}]         
            innerTemplate = Template.Template(file=self.formTemplate, searchList = searchList,
                                              compilerSettings={'prioritizeSearchListOverSelf' : True})
            searchList.append({LCFIT_NAV_MAIN_PLACEHOLDER : str(innerTemplate)})
            searchList.append(LcConfig)
            pageTemplate = Template.Template(file=self.navTemplate, searchList = searchList,
                                             compilerSettings={'prioritizeSearchListOverSelf' : True}) 
            self._postCondition(req)
            
            # write and return
            req.content_type = "text/html"
            req.send_http_header()
            req.write(str(pageTemplate))

        except (LcSessionException, LcAuthException): 
            util.redirect(req, LcSessionExceptionRedirect)
        except LcDataException, mess:
            if LcHardErrors:
                raise 
            else:
                redirectString = LCFIT_WWW_INDEX + '?' + LCFIT_ERROR_MESSAGE_KEY + '=' + str(mess)
                util.redirect(req, redirectString)
    

class LcForm(LcPage):
    '''Display a form with embedded stuff to make it work.  Works for
    arbitrary forms (mf, coherent, etc), as long as one calls it with
    different templates and process destinations.'''
    def __init__(self, redirectTarget, formTemplate, navTemplate, lcdb, title=None):
        self.redirectTarget = redirectTarget
        self.formTemplate = formTemplate
        self.navTemplate = navTemplate
        self.lcdb = lcdb
        self.title = title

        
    def __call__(self, req):
        lcfitlogger.debug( 'LcForm:  __call__')
        try:
            self._preCondition(req)
            
            # set up the templates.  First create the form (inside)
            # template, then pass an expanded str()'ed version of it
            # to navigation (outsided) template in the searchList.  A
            # little bit funky - my apologies.
            searchList = [{LCFIT_FORM_TARGET_PLACEHOLDER : self.redirectTarget,
                           'request':req,
                           'session':req.session,
                           'lcdb':self.lcdb,
                           LCFIT_TITLE_PLACEHOLDER:self.title}]
            searchList.append(LcConfig.__dict__)
            
            formTemplate = Template.Template(file=self.formTemplate, searchList = searchList,
                                             compilerSettings={'prioritizeSearchListOverSelf' : True})
            searchList.append({LCFIT_NAV_MAIN_PLACEHOLDER : str(formTemplate)})
            pageTemplate = Template.Template(file=self.navTemplate, searchList = searchList,
                                             compilerSettings={'prioritizeSearchListOverSelf' : True})

            self._postCondition(req)
            
            # write and return
            req.content_type = "text/html"
            req.send_http_header()
            req.write(str(pageTemplate))
            return apache.OK

        except (LcSessionException, LcAuthException): 
            util.redirect(req, LcSessionExceptionRedirect)


class LcProcess(LcPage):
    """Process a form, save it, and redirect to display; all of these
    specified in the parameters when it is instantiated."""
    def __init__(self, targetClass, redirectTarget,  lcdb):
        if type(targetClass) not in (types.ClassType, types.TypeType):
            raise "Bad type for targetClass: %s" % str(type(targetClass))
        self.targetClass = targetClass
        self.redirectTarget = redirectTarget
        self.lcdb = lcdb
        
    def __call__(self, req):
        """ this is a docstring """
        try:
            self._preCondition(req)

            # Convert fields that matter from req.form into dict
            formData = {}
            for k in (req.form.keys()): 
                if type(req.form[k]) == types.ListType:
                    # with a list of result, parse out selected value
                    tmpList = filter(lambda x: x != LCFIT_UNSELECTED_VALUE, req.form[k])
                    if len(tmpList) > 1:
                        raise LcInputException, \
                              "Must only select a single value. Selected: %s" % tmpList
                    elif len(tmpList) == 0:
                        pass
                    else:
                        formData[k] = tmpList[0].value
                else:
                    formData[k] = req.form[k].value
                                        
            # Create an object, passing the dict to the target class,
            # converting to regular named paramters with ** magic.
            #raise str(self.targetClass)
            obj = self.targetClass(**formData)
            
            # Stuff into the database, grabbing ownership info from
            # the session, and adjusting the internal id of the object
            # from the DB serial number.
            owner = self.lcdb.retrieveUsername(req.session[LCFIT_SESSION_KEY])
            comments = req.form[LCFIT_OBJECT_COMMENTS_KEY].value 
            
            inserter = self.lcdb.makeInserter(owner=owner, comments=comments)
            objSerialNumber = inserter.getSerialNumber()
            obj.LcID = objSerialNumber
            inserter.insertObject(obj)
            del(inserter)

            lcfitlogger.debug( 'LcProcess:  __call__.  Object ID: %s.  Datapath: %s. Class: %s' % \
                          (obj.LcID, obj.datapath, str(obj.__class__)))
            
            # Grab all the images from the new object and stuff them
            # in the database appropriately
            for name, data in obj.imagesDict.iteritems():
                self.lcdb.insertImage(objSerialNumber, name, data, LCFIT_IMAGE_FORMAT)
            
            # Check postconditions, then create a valid display URL
            # and throw a redirect
            self._postCondition(req)
            util.redirect(req, self.redirectTarget)
            
        except LcSessionException, mess:
            # if the session is expired  throw an error
            util.redirect(req, LcSessionExceptionRedirect)
        except LcInputException, mess:
            # if there is bad data, either throw a stacktrace or a useless but pretty error
            if LcHardErrors:
                raise 
            else:
                redirectString = LCFIT_WWW_INDEX + '?' + LCFIT_ERROR_MESSAGE_KEY + '=' + str(mess)
                util.redirect(req, redirectString)
        except LcDataException, mess:
            if LcHardErrors:
                raise 
            else:
                redirectString = LCFIT_WWW_INDEX + '?' + LCFIT_ERROR_MESSAGE_KEY + '=' + str(mess)
                util.redirect(req, redirectString)
        except LcException, mess:
            # otherwise, do the same 
            if LcHardErrors:
                raise
            else:
                redirectString = LCFIT_WWW_INDEX + '?' + LCFIT_ERROR_MESSAGE_KEY + '=' + "<pre>" + str(mess) + "</pre>"
                util.redirect(req, redirectString)
        pass
    

class LcDisplay(LcPage):
    """Grab an object and display it, using serial number"""
    def __init__(self, lcdb, navTemplate):
        self.lcdb = lcdb
        self.navTemplate = navTemplate

        
    def __call__(self, req):
        try:
            self._preCondition(req)

            # Retrieve and unpickle an object based on the targetClass
            # name and the instance serial number ...
            try:
                objId= int(req.form[LCFIT_OBJECT_ID_KEY].value)
            except:
                raise LcInputException 
            instance = self.lcdb.retrieveObject(objId)

            # ... have said instance draw itself inside the main application
            # template ...
            searchList = []
            searchList.append({LCFIT_NAV_MAIN_PLACEHOLDER : str(instance)})
            searchList.append(LcConfig)
            try:
                searchList.append({LCFIT_TITLE_PLACEHOLDER:self.title})
            except AttributeError:
                searchList.append({LCFIT_TITLE_PLACEHOLDER:'LCFIT Object ID: %i' % objId})
            pageTemplate = Template.Template(file=self.navTemplate, searchList = searchList,
                                             compilerSettings={'prioritizeSearchListOverSelf' : True})

            lcfitlogger.debug( "LcDisplay: __call__.  Object ID:  %s" % objId)

            # test postconditions and return the data 
            self._postCondition(req)
            req.content_type = "text/html"
            req.send_http_header()
            req.write(str(pageTemplate))
        except (LcSessionException,):
            lcfitlogger.error( "LcDisplay: __call__.  Error.")
            util.redirect(req, LcSessionExceptionRedirect)
        except LcDataException:
            lcfitlogger.error( "LcDisplay: __call__.  Error.  Object ID: %s" % objId)
            util.redirect(req, make_LcDataExceptionRedirect(objId))
        return True

class LcList(LcPage):
    """Display a list of the objects such that one can pick a single one to display."""
    def __init__(self, lcdb, navTemplate, objectListTemplate, title=None):
        self.lcdb = lcdb
        self.navTemplate = navTemplate
        self.objectListTemplate = objectListTemplate
        self.title = title

    def __call__(self, req):
        try:
            self._preCondition(req)

            # Get current user from cookie or however
            currentUser = self.lcdb.retrieveUsername(req.session[LCFIT_SESSION_KEY])
            
            # Get a list of forecast/ data objects for that person
            (colNames, objectInfoList) = self.lcdb.listObjectInfo(currentUser)

            # Feed that list into the appropriate template, then in turn into the main navigation template
            searchList = []
            searchList.append({LCFIT_OBJECTLIST_PLACEHOLDER : objectInfoList})
            searchList.append({LCFIT_OBJECTCOLNAMES_PLACEHOLDER : colNames})
            searchList.append({LCFIT_TITLE_PLACEHOLDER:self.title})
            searchList.append(LcConfig)
            objectListTemplate = Template.Template(file=self.objectListTemplate, searchList = searchList,
                                                   compilerSettings={'prioritizeSearchListOverSelf' : True})
            searchList.append({LCFIT_NAV_MAIN_PLACEHOLDER : str(objectListTemplate)})
            pageTemplate = Template.Template(file=self.navTemplate, searchList = searchList,
                                             compilerSettings={'prioritizeSearchListOverSelf' : True})

            # Check post conditions
            self._postCondition(req)

            lcfitlogger.debug( "LcList: __call__.  User: %s." % currentUser)

            # Write the result
            req.content_type = "text/html"
            req.send_http_header()
            req.write(str(pageTemplate)) 

        except (LcSessionException), e:
            lcfitlogger.error( "LcList: __call__.  Error.")
            util.redirect(req, LcSessionExceptionRedirect)
        except (LcDataException), e:
            lcfitlogger.error("LcList: __call__.  Error.")
            util.redirect(req, make_LcSessionExceptionRedirect_disconnect(str(e)))


class LcDelete(LcPage):
    def __init__(self, lcdb, redirectTarget=LCFIT_WWW_LIST_OBJECTS):
        self.lcdb = lcdb
        self.redirectTarget = redirectTarget

    def __call__(self, req):
        try:
            self._preCondition(req)

            # Make sure appropriate user, then delete
            currentUser = self.lcdb.retrieveUsername(req.session[LCFIT_SESSION_KEY])
            objectOwner = self.lcdb.retrieveObjectOwner(int(req.form[LCFIT_OBJECT_ID_KEY].value))
            if currentUser != objectOwner:
                raise LcAuthException
            else:
                self._postCondition(req)
                objId = int(req.form[LCFIT_OBJECT_ID_KEY].value)
                self.lcdb.deleteObject(objId)
                lcfitlogger.debug( "LcDelete: __call__.  Deleted object ID: %s." % objId)
                util.redirect(req, self.redirectTarget)

        except (LcSessionException,):
            lcfitlogger.warning("LcDelete: __call__.  Error.")
            util.redirect(req, LcSessionExceptionRedirect)

        # if get LcDataException, assume clicked too many times and
        # just redirect to wherever
        except (LcDataException), mess: 
            util.redirect(req, self.redirectTarget)


class LcDisplayImage(LcPage):
    """map a URL to an image in the database and display it"""

    def __init__(self, lcdb):
        self.lcdb = lcdb

    def __call__(self, req):
        try:
            self._preCondition(req)
            objId = req.form[LCFIT_OBJECT_ID_KEY].value
            imgName = req.form[LCFIT_IMAGE_NAME_KEY].value
            data = self.lcdb.retrieveImage(objId, imgName)
            self._postCondition(req)
            req.content_type = "image/png"
            req.headers_out['Content-Disposition'] = 'inline; filename=lcobject-%s-%s' %\
                                                     (objId, imgName)
            req.set_content_length(len(data)) 
            req.send_http_header()
            req.write(data)
            return apache.OK
        except LcSessionException:
            util.redirect(req, LcSessionExceptionRedirect)
        return


class LcDumpText(LcPage):
    """Grab the text version of an LC object"""

    def __init__(self, lcdb):
        self.lcdb = lcdb

    def __call__(self, req):
        try:
            self._preCondition(req)
            objectId = int(req.form[LCFIT_OBJECT_ID_KEY].value)
            data = self.lcdb.retrieveTextDump(objectSerialNumber=objectId)
            self._postCondition(req)
            lcfitlogger.debug( "LcDumpText: __call__.  ObjectId: %s."  % objectId)

            req.content_type = "text/tab-separated-values"
            req.headers_out['Content-Disposition'] = 'attachment; filename=forecast-object-%i.txt' % objectId
            req.set_content_length(len(data))
            req.send_http_header() 
            req.write(data)
            return apache.OK
        except LcSessionException:
            util.redirect(req, LcSessionExceptionRedirect)
        return
    
class LcError:
    """Displays an error."""
    def __init__(self, template, title=None, message=''):
        self.template = template
        self.message = message
        self.title = title
        return

    def __call__(self, req, **kwargs):

        # Feed that list into the appropriate template, then in turn into the main navigation template
        searchList = []
        searchList.append(kwargs)
        searchList.append({LCFIT_TITLE_PLACEHOLDER:self.title})
        searchList.append({LCFIT_ERROR_MESSAGE_KEY:self.message})
        searchList.append(LcConfig)

        pageTemplate = Template.Template(file=self.template, searchList = searchList,
                                         compilerSettings={'prioritizeSearchListOverSelf' : True})

        lcfitlogger.debug( "LcError: __call__.")

        # Write the result
        req.content_type = "text/html"
        req.send_http_header()
        req.write(str(pageTemplate)) 
        return
