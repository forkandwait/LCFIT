'''
Interface to database for LC Objects.  The overall approach is that
all objects get a reference to the same handle and use its methods to
do inserts, updates, etc.  THere is a separate function written for
each operation that we do, so that if, say, we want to insert an
forecast object we just call a method and pass the object, without
worrying about the SQL; the SQL is hidden inside the function
definition.
'''
## import all the classes that we use here.
from LcConfig import *
import LcSinglePopObject
import LcMFPopObject
import LcCoherentPopObject
import LcHMDObject

import sqlite3

	
class LcObjDB(object):
	"""
	Creates a connection to a database, and the detail, by wrapping
	SQL, initiating and deleting connections, etc.
	"""

	def __init__(self, dbname='/home/webbs/lcfit-devel.git/lcfitdb.sqlite', host = 'localhost', user='larry'):
		'''initialize with a connection string and store connection.'''
		(self._dbname, self._host, self._user) = (dbname, host, user)
		self._dbcon = sqlite3.connect(dbname)
		## create a nextval('seqname') function
		
	class Inserter:
		"""Special little class to do a single object insert, while
		making the automatically assigned serial number available to
		the outside as they call it repeatedly via clicking"""
		
		def __init__(self, dbcon, owner, comments, conn_str=''):

			self._dbcon = dbcon
			self.owner = owner
			self.comments = comments 
			self.hasInsertedAlready = False

			sql = "select nextval('dataobjects_objectserialnumber_seq')" 
			(res, self._dbcon) = try_execute(dbcon=self._dbcon, sql=sql, fetch_N='one')
			(self.serialNumber,)=res
			
		def getSerialNumber(self):
			return self.serialNumber

		def insertObject(self, instance):
			'''Pickle the __dict__ of instance, insert it into the
			database with associated stuff like serial number,
			classname, etc'''
			
			classTypeStr = instance.__class__.__name__
			if self.hasInsertedAlready:
				raise LcDataException, 'Trying to insert same object more than once'
			sql = "INSERT INTO dataObjects " +\
				  "(objectSerialNumber, owner, comments, classType, pickledData)" +\
				  "VALUES(%s, %s, %s, %s, %s)" 
			
			instString = cPickle.dumps(instance.__dict__, 0)
			inst = psycopg2.Binary(instString)
			(ret, self._dbcon) = try_execute(dbcon=self._dbcon,
											 sql=sql,
											 data=(self.serialNumber, self.owner, self.comments, classTypeStr, inst),
											 fetch_N='none')
			self.hasInsertedAlready = True
			return True
		pass

	
	def makeInserter(self, owner, comments):
		ins = LcObjDB.Inserter(self._dbcon, owner, comments, conn_str=self._dbcon_conn_str)
		return ins
	
	
	def retrieveObject(self, objectSerialNumber):
		'''Retrieve an object with a given id.  Uses the following
		Algorithm: gets the classname, instantiates an empty class,
		gets the __dict__, fills the instantiated class from this
		dict, returns the class.'''

		sql = "SELECT classtype, pickleddata FROM dataobjects WHERE objectSerialNumber = %s"
		(res, self._dbcon) = self._try_execute(sql=sql, data=(objectSerialNumber,), fetch_N='one')
		if res is None:
		    raise LcDataException, "No such data object: %s" % objectSerialNumber
		else:
			(classtype, instanceDictPickled,) = res

		instance = dict2object(classtype, instanceDictPickled)
		return instance

	# def listObjectInfo(self, owner):
	# 	"""List summary data for all objects owned by 'owner', including columnames"""

	# 	# Select the summary information for all objects from a given owner/creator

	# 	colNames = ['objectSerialNumber', 'classType', 'owner', 'date_trunc', 'comments']
	# 	sql = "SELECT objectSerialNumber, classType, owner, " +\
	# 		  " date_trunc('minute', timestampcreated)::text, comments " +\
	# 		  "FROM dataobjects " +\
	# 		  "WHERE owner = %s " +\
	# 		  "ORDER BY objectSerialNumber DESC"
	# 	(ret, self._dbcon) = self._try_execute(sql=sql, data=(owner,), fetch_N='all')
	# 	objectList = ret
		
	# 	return (colNames, objectList)


	# def listObjectsFromClass(self, className, sessionId):
	# 	""" List stored object ids for a given class belonging to owner """

	# 	sql = "SELECT objectSerialNumber " +\
	# 		  "FROM dataobjects " +\
	# 		  "WHERE classtype = %s " +\
	# 		  " AND owner = (SELECT username from currentSessions WHERE sessionID = %s) " +\
	# 		  "ORDER BY objectSerialNumber DESC"
	# 	(res, self._dbcon) = self._try_execute(sql=sql, data=(className, sessionId), fetch_N='all')
	# 	objectList = [None] * len(res)
	# 	for i, objTuple in enumerate(res):
	# 		objectList[i] = int(objTuple[0])
	# 	return objectList


	# def retrieveObjectOwner(self, objectSerialNumber):
	# 	"""Return owner of objectSerialNumber"""

	# 	sql = "SELECT owner FROM dataobjects WHERE objectSerialNumber = %s"
	# 	(res, self._dbcon) = self._try_execute(sql=sql, data=(objectSerialNumber,), fetch_N='one')
	# 	if res is None:
	# 		raise LcDataException, "retrieveObjectOwner: No rows returned for object id: %s" \
	# 			  % objectSerialNumber
	# 	else:
	# 		(owner,) = res
	# 	return owner
		

	# def deleteObject(self, objectSerialNumber):
	# 	'''Delete an object by objectSerialNumber'''
	# 	sql = "DELETE FROM dataobjects WHERE objectSerialNumber = %s"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(objectSerialNumber,), fetch_N='none')
	# 	return None


	# def insertImage(self, objectId, imageName, imageData, imageFileType):
	# 	'''insert an image associated with an object '''

	# 	sql = "INSERT INTO images (objectId, imageName, imageData, imageFileType) VALUES(%s, %s, %s, %s)" 
	# 	image = psycopg2.Binary(imageData)
	# 	(res, self._dbcon) = self._try_execute(sql, data=(objectId, imageName, image, imageFileType), fetch_N='none')
	# 	return (objectId, imageName)
		

	# def retrieveImage(self, objectId, imageName):
	# 	'''retrieves an image of a given objectId and type.
	# 	The ideas is some id, plus something like "forecast"
	# 	'''

	# 	sql = "SELECT imagedata FROM images where objectId = %s and imageName = %s"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(objectId,imageName), fetch_N='one')
	# 	if res == None:
	# 		raise LcDataException, "No such image object: '(%s, %s)'" % (objectId, imageName)
	# 	else:
	# 		(image,) = res
	# 	return image


	# def retrieveTextDump(self, objectSerialNumber):
	# 	'''retrieves an image of a given objectId and type.
	# 	The idea is some id, plus something like "forecast"
	# 	'''

	# 	## Need to select the object, unpickle it, grab the text dump
	# 	sql = "SELECT classtype, pickleddata FROM dataobjects WHERE objectSerialNumber = %s"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(objectSerialNumber,), fetch_N='one')
	# 	if res is None:
	# 		raise LcDataException, "No such data object: %s" % objectSerialNumber
	# 	(classtype, instanceDictPickled) = res
	# 	instance = dict2object(classtype, instanceDictPickled)
	# 	return instance.dumpString


	# def authorizeUser(self, username, password, ipAddress = None):
	# 	"""Set up a user session if valid, return session number from
	# 	DB if OK, return False if invalid"""

	# 	sql = "SELECT auth_lc_user(%s, %s, %s)"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(username,password,ipAddress), fetch_N='one')
	# 	self._dbcon.commit()
	# 	sessionId = res[0]
	# 	if sessionId <= 0:				# Includes -1
	# 		return False
	# 	else:
	# 		return sessionId
				
	# def logout(self, sessionId):
	# 	"""Logout"""
	# 	sql = "UPDATE currentSessions SET stoptime = now() WHERE sessionid = %s"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(sessionId,), fetch_N='none')

	# def checkSession(self, sessionId):
	# 	"""Return true if sessionId refers to an actual session, otherwise False"""
	# 	sessionId = int(sessionId)
	# 	sql = "SELECT count(*) from currentSessions where sessionId = %s and stoptime is Null"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(sessionId,), fetch_N='one')
	# 	(count,) = res
	# 	if count == 1:
	# 		return True
	# 	elif count == 0:
	# 		return 0
	# 	else:
	# 		raise LcDataException, "strange response to checkSession"

	# def retrieveUsername(self, sessionId):
	# 	'''retrieve username from session id'''
	# 	sql = "SELECT username FROM currentsessions where sessionId = %s"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(sessionId,), fetch_N='one')
	# 	if res == None:
	# 		raise LcSessionException, "Unable to find session number: %s" % sessionId
	# 	else:
	# 		(username,) = res
	# 	return username


	# def insertPageView(self, sessionId, URL, data=None):
	# 	"""Insert a record of thmd2laree page viewed, for reporting and
	# 	debugging"""
	# 	sessionId = int(sessionId)
	# 	sql = "INSERT into pageViews (sessionId, URL, datastring) values (%s, %s, %s)"
	# 	(res, self._dbcon) = self._try_execute(sql, data=(sessionId, URL, data), fetch_N='none')
	# 	return

	# def insertRegRequest(self, data):
	# 	""" Insert registration information into database """

	# 	# Check that username isn't already pending
	# 	sql = "SELECT count(*) from pending_registrations where username = %s and finished = False"
	# 	(res, self._dbcon) =self._try_execute(sql, data=(data['USERNAME'],), fetch_N='one')
	# 	if res[0] >= 1:
	# 		raise LcDataException("Username pending")

	# 	# Check that username isn't already in use
	# 	sql = "Select count(*) from authorizedusers where username = %s"
	# 	(res, self._dbcon) =self._try_execute(sql, data=(data['USERNAME'],), fetch_N='one')
	# 	if res[0] >= 1:
	# 		raise LcDataException("Username in-use")		

	# 	sql = "INSERT into pending_registrations " + \
	# 		  " (fullname, username, password, email, affiliation, reasons, howfind) " + \
	# 		  "VALUES (%s, %s, %s, %s, %s, %s, %s);"
	# 	(res, self._dbcon) = self._try_execute(sql,
	# 										   data= (data['FULLNAME'], data['USERNAME'], data['PASSWORD'],
	# 												  data['EMAIL'], data['AFFILIATION'], data['REASONS'], data['HOWFIND']),
	# 										   fetch_N='none')
	# 	return
		
if __name__ == '__main__':
	print "hello"
