"""
Converts, stores, and formats data converted from HMD format into a
more standard set of tab delimited files (year by age, one for female,
male, combined).
"""
from LcLog import lcfitlogger
from LcConfig import * 
import LcUtil
from LcUtil import Diagnose as D

def s2zero(x):
	'''
	converts a string to a float, returning 0.0 if the string is
	not parseable, eg "." in HMD
	'''
	conversionHash = {
		'.' : 1.0
		}

	# if x is in the conversion-hash, return appropriate;
	# otherwise try to convert to a float
	if conversionHash.has_key(x):
		return conversionHash[x]
	else:
		return float(x)

	
def isfull(x):
	'''Determines whether a variable holds the empty string'''

	if x == '':
		return False
	else:
		return True


def stride2MatrixList(inputMatrix, strideLength):
	'''Converts an M x N array with a (row) stride length of S into a
	N length list of M x S matrices.
	'''

	nrows = len(inputMatrix)				# rows of input array

	# Verify that array is 1 or 2 dimensions (Numeric allows for M x N
	# x K...
	if len(inputMatrix.shape) == 1:
		ncols = 1
	elif len(inputMatrix.shape) > 2:
		raise Exception, "stride2MatrixList: need 1 or 2 dim array only"
	else:
		ncols = inputMatrix.shape[1]

	# Verify that the row dim is a multiple of the stride
	if nrows % strideLength != 0:
		raise Exception, "stride2MatrixList: row count must be multiple of target col count"

	# Set up the list of appropriately sized matrices
	outputRowCount = nrows / strideLength		
	finalArrayList = []
	for colIndex in range(0, ncols):
		finalArrayList.append(N.zeros((outputRowCount, strideLength), N.float))

	# Populate the list of output matrices by distributing from the
	# hmd matrix.
	try:
		for rowIndex in range(0, nrows):
			targetRowIndex = int(rowIndex / strideLength)
			targetColIndex = int(rowIndex % strideLength)
			for outputArrayIndex in range(0, ncols): 
				finalArrayList[outputArrayIndex][targetRowIndex, targetColIndex] = \
																 inputMatrix[rowIndex,outputArrayIndex]
	except:
		print outputArrayIndex, targetRowIndex, targetColIndex
		print len(finalArrayList), finalArrayList[0].shape
		raise
	
	return(finalArrayList)
		

def hmd2lare (hmd_text, HW=24, HC=5, LW=24):
	''' HW = number of age classes in HMD, HC = number cols in HMD, LW
	= number age classes in LARE. For HMD, assuming Year, Age, F, M,
	Tot columns, 0-1, 1-4, then 5 year, 110+ as open.

	XXX doesnt add 0-1 + 1-4, then return _23_ age classes, like it
	should.	 Maybe it shouldnt?

	Overall: (1) Converts text from HMD into a matrix with same
	structure sans labels (with the stride of the matrix implying its
	age dimension. (2) Feeds that big stride matrix in
	stride2MatrixList() to create a list of separate matrices for each
	column (female, male, total).  (3) Returns that list, which is
	formatted elsewhere for display.

	'''


	try:
		# Create a lis.t to hold all the data text rows from HMD.
		rows = filter(LCFIT_HMD_ROW_RE.match, hmd_text.split('\n'))
		assert len(rows) >= 1, \
			   LcException("Empty rows.  \nhmd_text: %s.  \nrows: %s\n." % (hmd_text, rows))

		# Creates a matrix of the right size to hold all the HMD data,
		# row count = number of lines split above, col count = 3 for female, male, total
		hmd = N.zeros((len(rows), 3), N.float)

		# Calculate the number of years of data from HMD, by dividing by
		# the number of age classes.
		no_years = hmd.shape[0] / HW

		# Fill hmd (above) with the data from HMD website: Iterate over
		# all the rows, splitting each row, keeping the three rightmost
		# columns, adding these three pieces to the bottom of the big
		# array.

		# Iterate ...
		for i, row in enumerate(rows):
			# ... split, hold three rightmost ...
			tmp = N.array(map(s2zero, row.split()[2:5]))
			# ... put these at the bottom of hmd.
			hmd[i,:] = tmp
				
		# Make array for LARE: rows for 0-5, etc, with 110+ open; 3 cols
		lare = N.zeros([no_years * LW, 3], N.float)
		for y in range(0, no_years):
			lare[y*LW:y*LW+LW+1,:] = hmd[y*HW:y*HW+HW+1] 

		out = stride2MatrixList(lare, LW) # out is 3 item list of matrices -- female, male, total
		return(out)
	
	except (ValueError,), mess:
		raise LcInputException, mess

def format_grid(grid, lineEnding='<br>\n', fieldSeparator='\t'):
	"""Turns an array into a string for output"""
	out_str = ''

	# Check to see if the first row has any lenght--if not, a plain
	# list; if so, a matrix (list of lists)
	try:
		grid_len = len(grid[0])
	except TypeError:				   	#
		for r in grid:
			out_str += str(r) + lineEnding
		return out_str 
	for r in grid:
		out_str += string.join(map(str, r), fieldSeparator) + lineEnding
	return out_str

class HMD(object):
	def __init__(self, hmdinput='XXX', start_year='XXX', notes='XXX', **kwargs):
		"""Get beginning state.  Note that some of this code makes it
		possible to instantiate an empty HMD object, to have its
		__dict__ filled from the database."""

		lcfitlogger.debug( 'HMD start')
		if start_year == '':
			raise LcInputException, "Must enter a start year for HMD Object"
		elif start_year == 'XXX':
			self.start_year = 0
		else:
			self.start_year = LcUtil.parseDate(start_year)
		
		if notes == '':
			raise LcInputException, "Must enter notes for HMD Object--country at least"
		elif notes == 'XXX':
			self.notes = notes

		self.datapath =	os.path.join(LCFIT_DATADIR, str(random.randint(0, 10**10)))
		
		self.tableString = ''
		self.imagesDict = {}


		if hmdinput == 'XXX':
			return
		else:
			lcfitlogger.debug( 'HMD Stop')
			self.hmdinput = hmdinput
			(self.femaleRates, self.maleRates, self.totalRates) = hmd2lare(hmdinput)
			return
		
			
	def __str__(self):

		years = range(self.start_year, self.start_year + len(self.femaleRates))
		outStr = '<p>Start Year: %r.  Notes: %r.</p>\n' % (self.start_year, self.notes)
		outStr += '<p><a href=#female>Female</a> '
		outStr += '<a href=#male>Male</a> '
		outStr += '<a href=#combined>Combined</a></p>'

		# Data in cells
		outStr += '<table border=1 style="font-family:courier; font-size:10; white-space:nowrap">'
		outStr += "<tr><td colspan=3>Below are the converted female, male, and combined death rates</td></td>\n"
		outStr += '<colgroup width="10%">\n'
		outStr += '<colgroup width="0*">\n'
		outStr += '<tr><td style="text-align:center; color: gold; background-color: blue; font-size:16;" colspan=3><a name="female">FEMALE</a></td></tr>'
		outStr += '<tr>' + \
				  '<td>' + format_grid(years) + '</td></col>' + \
				  '<td bgcolor=gray>&nbsp;</td>' + \
				  '<td>' + format_grid(self.femaleRates) + '</td>' +\
				  '</tr>'
		outStr += '<tr><td style="text-align:center; color: gold; background-color: blue; font-size:16;" colspan=3><a name="male">MALE</a></td></tr>'
		outStr += '<tr> ' + \
				  '<td>' + format_grid(years) + '</td></col>' + \
				  '<td bgcolor=gray></td>' + \
				  '<td>' + format_grid(self.maleRates) + '</td></tr>'
		outStr += '<tr><td style="text-align:center; color: gold; background-color: blue; font-size:16;" colspan=3><a name="combined">COMBINED</a></td></tr>' 
		outStr += '<tr> ' + \
				  '<td>' + format_grid(years) + '</td></col>' + \
				  '<td bgcolor=gray></td>' + \
				  '<td>' + format_grid(self.totalRates) + '</td></tr>'
		outStr += '</table>'
		return outStr
