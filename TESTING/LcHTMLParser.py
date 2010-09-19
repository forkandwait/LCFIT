"""

Provides two classes:

1.  LcHTMLParser -- encapsulates a regular HTMLParser object,
    storing tag information depending on which tag names are passed to
    it at creation.

2.  LcHTMLChecker -- encapsulates an LcHTMLParser object, handling its
    resetting, care, and feeding with HTML, and providing checkTag()
    to determine whether a tag, with an optional attribute and an
    optional value, are present.

"""

import HTMLParser as H
import copy
import re
import sys
import string

sys.path.append('../../INTERNET_APPLICATION')
from LcUtil import Diagnose as D

class LcHTMLChecker(object):
	"""Encapsulates an HTML Parser, feeds and clears it, provides
	checkAllForTag() to check the tags and attributes in the html.

	Use case 1:
	>>> LcChecker = LcHTMLChecker(tagList=['a', 'div'])
	>>> LcChecker.feed(data=html)
	>>> assert LcChecker.checkTag(tag='div', attr='class', value='Application'), AssertionException('Whoops')
	>>> LcChecker.clearData()			# Same tags, clear the parsed html
	>>> LcChecker.feed(data=newHtml)
	>>> assert LcChecker.checkTag(tag='a', attr='href'), AssertionException('whoops') 

	"""
	
	def __init__(self, tagList, *args, **kwargs):
		"""Initializes a parser."""
		super(LcHTMLChecker, self).__init__(*args, **kwargs)
		self.hParser = LcHTMLParser()		
		self.hParser.setTagList(tagList)
		return

	def feed(self, data, *args, **kwargs):
		"""Feeds html to be checked later."""
		self.hParser.feed(data, *args, **kwargs)
		return

	def checkTag(self, tag, attr=None, value=None):
		"""Checks processed data for tag and optional attr and value."""
		
		if ((attr is None) and (value is not None)):
			raise LcException( "Can't have a value w/o attribute.")
			
		# Get big hash.  Confirm that the value under the tag is non
		# empty.  Iterate over the line numbers under the tag checking
		# for attr and value pair.  Return true on the first one that
		# matches, return false if we fall off the end.  Short
		# circuits appropriately.
		
		htmlDataDict = self.hParser.getData()
		if not htmlDataDict.has_key(tag):
			return False
		if len(htmlDataDict[tag]) >= 1:	# Found a tag
			if attr is None:
				return True
			for k,v in htmlDataDict[tag].iteritems(): # iter over the instances of the tag
				if v.has_key(attr):		# Found an attribute (key in hash) in a tag instance
					if value is None:
						return True
					if v[attr] == value: # Found the right value
						return True
		return False

	
	def reset(self):
		"""Resets the parser and clears its list of found stuff.
		Doesn't clear the list of tags sought."""
		self.hParser.clearData()
		self.hParser.reset()
		return

class LcHTMLParser(H.HTMLParser):

	def setTagList(self, retTagList=None):
		"""Sets tags of which to remember; dict (indexed by tag) of
		dicts (indexed by lineno) of dict of attribute-value pairs."""
		self._tagCount = 0
		self._tagSet = set(retTagList)

		self._tagCountHash = dict.fromkeys(retTagList, 0) 
		self._tagResultsHash = dict.fromkeys(retTagList, None)	# if {} instead of None, get many->one refs.  Grr
		for k,v in self._tagResultsHash.iteritems():
			self._tagResultsHash[k] = {}
		return

	def getData(self):
		return copy.copy(self._tagResultsHash)

	def clearData(self):
		""" Clears the data structure recording the tags already
		found.  Doesn't clear the list of tags we are seeking--use
		another instance."""
		del self._tagCountHash
		self._tagCountHash = dict.fromkeys(self._tagSet, 0)
		
		del self._tagResultsHash
		self._tagResultsHash = dict.fromkeys(self._tagSet, None)
		for k,v in self._tagResultsHash.iteritems():
			self._tagResultsHash[k] = {} 
		return
	
	def handle_starttag(self, tag, attrs):
		""" If a tag of interest, appends it to a list with info,
		otherwise nada."""
		if tag in self._tagSet:
			self._tagCountHash[tag] += 1
			self._tagResultsHash[tag][self._tagCountHash[tag]] = copy.copy(dict(attrs))
		return

	def handle_endtag(self, tag):
		""" Does nothing """
		return

	def handle_startendtag(self, tag, attrs):
		""" Does nothing """
		return

	pass


class LcObjectListParser(H.HTMLParser):
	"""Generates a list of LARE object ids and the data between the
	anchor tags."""

	from LcConfig import LCFIT_OBJECT_ID_KEY
	LC_OBJECT_ID_ATTR = LCFIT_OBJECT_ID_KEY.lower()

	def __call__(self, data, *args, **kwargs):
		self.resetObjectLinks()
		self.reset()
		self.feed(data)
		self.close()
		return self.getObjectLinks()

	def resetObjectLinks(self):
		self.objectLinks = []
		return

	def getObjectLinks(self):
		return copy.copy(self.objectLinks)

	def handle_starttag(self, tag, attrs):
		# Note that all attributes are lower cased!
		attr_hash = dict(attrs)
		if tag == 'a':
			if attr_hash.has_key(LcObjectListParser.LC_OBJECT_ID_ATTR):
				if not attr_hash.has_key('notes'):
					attr_hash['notes'] = ''
				self.objectLinks.append({'id':attr_hash[LcObjectListParser.LC_OBJECT_ID_ATTR], 'notes':attr_hash['notes']})
				pass
			pass
		return

	def handle_data(self, data):
		return

	def handle_endtag(self, tag):
		return

	pass

			
if __name__ == '__main__':
	print __name__
