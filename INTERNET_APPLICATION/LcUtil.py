""" Lots of utility functions that are not specific to the LCFIT
algorithm per se"""

from LcConfig import * 
import scipy.optimize
import scipy.interpolate
import LcExtension

#LcException = Exception

def Diagnose(*printVars):
	outvars = ["%s\n" % str(x).translate(string.maketrans('<>', '{}')) for x in printVars ]
	raise Exception, "%s" % pprint.pformat(outvars, width=-1)

def D(*v):
	Diagnose(*v)

def Warn(*printVars):
	#sys.stderr.write("\n%s\n" % pprint.pformat(printVars))
	#sys.stderr.flush()
	return

def listTypes(kw):
	TR = string.maketrans('<>', '{}')
	assert type(kw) == types.DictType, \
		   LcException("must be dict type like from locals().  Is: %s" % type(kw))
	LL = [(str(type(kw[k])).translate(TR), k) for k in kw.keys()]
	LL.sort()
	raise Exception, "%s" % pprint.pformat(LL, width=2)
	
def logit(a):
	assert 0 <= a <= 1,  Exception("a must be a probability 0<=a<=1.  a=%s" % a)
	return N.log(a/(1-a))

def goodRows(a):
	assert type(a) == N.ndarray, Exception("a must be an array: type(a):" % a)
	return 	


def adjustAx(mx, gender='combined'):
	numAgeWidths = LARRY_DEFAULT_NO_AGEWIDTHS
	
	# Going to let qx[2] float as 2.6 since can't go to a previous x
	ax_new = N.array([0.0] * numAgeWidths, N.float64)
	ax_old = N.array([0.0] * numAgeWidths, N.float64)
	qx = N.array([0.0] * numAgeWidths, N.float64)
	dx = N.array([0.0] * numAgeWidths, N.float64)
	lx = N.array([0.0] * numAgeWidths, N.float64)
	dx_old = N.array([0.0] * numAgeWidths, N.float64)
	dx = N.array([0.0] * numAgeWidths, N.float64)
	
	
	# estimate ax as 2.5, store as ax_old
	if gender == 'combined':
		ax_new[0] = (0.045 + 0.053)/2 + ((2.684 + 2.800)/2)*mx[0]	# punt -- average m, f from "Demography" p48
		ax_new[1] = (1.651 + 1.522)/2 + ((2.816 + 1.518)/2)*mx[0] # punt -- ditto...
	elif gender == 'male':
		ax_new[0] = 0.045 + 2.684 * mx[0]
		ax_new[1] = 1.651 + 2.816 * mx[0]
	elif gender == 'female':
		ax_new[0] = 0.053 + 2.800 * mx[0]
		ax_new[1] = 1.522 + 1.518 * mx[0]
	ax_new[2:17] = 5.0 * N.array([.46, .54, .57, .49, .50, .52, .54, .54, .54, .53, .52, .52, .52, .51, .51])
	ax_new[18:-2] = N.array([2.27, 2.19, 2.08, 1.95]) # Australia 1927.  1966: 2.31 2.23 1.88 1.63 1.41 1.35
	ax_new[-2] = 1.6					# Averaging and eyeballing Rus, Jap, US begining and end of data
	ax_new[-1] = 1.6					# ditto
	#logging.debug( "%s" % ax_new)
	"""
	AgeF-USM-USF-JM-JF-RusM-Rus
	start 105 1.60 1.54 1.24 1.21 1.81 1.79 avg=1.531666667
	end   105 1.63 1.65 1.61 1.52 1.36 1.41 avg=1.53
	start 110 1.69 1.61 1.20 1.17 2.21 2.21 avg=1.681666667
	end   110 1.61 1.70 1.53 1.47 1.29 1.38 avg=1.496666667

	From HMD
	"""

	iter_repeats = 1
	while iter_repeats <= 7:

		# ** calculate qx from mx and ax
		qx[0] = mx[0] / (1+(1-ax_old[0])*mx[0])
		qx[1] = mx[1] / (1+(4-ax_old[1])*mx[1])
		qx[2:-1] = (5*mx[2:-1]) / (1 + (5-ax_old[2:-1])*mx[2:-1])
		qx[-1] = 1.0
		qx[qx >= 1.0] = 1.0 				# Sanity
		qx[qx <= 0.0] = 0.0				# Sanity
		
		# calculate lx from qx
		lx[0] = 1
		lx[1:] = N.cumprod(1.0-qx[0:-1])

		# estimate dx
		dx = -N.diff(N.concatenate((lx, [0.0])))
		dx[dx<=0.0] = 0.00001			# XXX Otherwise we get inf's 

		# use polynomial thing to estimate ax_new
		ax_old[...] = ax_new[...]
		for i in range(2, len(ax_old)-2):
			ax_new[i] = ( (-(5.0/24.0)*dx[i-1]) + (2.5*dx[i]) + ((5.0/24.0)*dx[i+1]) )/dx[i]
			pass

		# find difference between ax_new and ax_old
		ax_diff = ax_old - ax_new
		ax_distance = N.sum(ax_diff**2)

		# if difference is small return ax_new
		if ax_distance < 0.1:
			if True:
				pass
				#logging.debug( "\n\nSuccess!\nax iteration (%s): %s\n" % (iter_repeats, ax_new))
			return (ax_new, qx, dx, lx)
		else:
			# How many times around?
			iter_repeats += 1
			ax_old[...] = ax_new[...]
			dx_old[...] = dx[...]
			# check for reasonable ax
			if (ax_new < 0.001).any():	# Seems that this should never be true yet it works without it....
				#raise Exception("ax lt 0.001.  iter = %s <br> \nmx: %s<br>\nax: %s" % (iter_repeats, mx, ax_new))
				pass
			pass
	
		# All done, looping again
		pass

	"""
	#  OLD CODE.  spine, CHECKING FOR between 0 and 1 and adjusting if not
	nqx[0] = nmx[0] / (1 + (qx0_intercept - qx0_slope * nmx[0]) * nmx[0]) # 0-1 age .93, 1.7. based on lfexpt.m
	nqx[1] = 4*nmx[1]/(1+(LARRY_DEFAULT_AGEWIDTH/2)*nmx[1])	# 1-4
	"""
	raise Exception
	logging.warning("\n\nFailure!\nax iteration (%s): \n%s\n" % (iter_repeats, pprint.pformat((ax_new, qx, mx, lx), width=10)))
	raise LcException('ax not settling down. <br>ax_distance: %s, iter_repeats: %s<br>ax_dif: %s<br>new: %s<br>old: %s <br>lx: %s <br>qx: %s<br>mx: %s<br>' % \
					  (ax_distance, iter_repeats, ax_diff, ax_new, ax_old, lx, qx, mx))


def lifeTable (nmxp,  ageCutoff=None, extensionMethod=LARRY_DEFAULT_EXTENSION_METHOD,
			   ltFuncType='ex', beginFuncParam=0, endFuncParam=0,
			   numAgeWidths = LARRY_DEFAULT_NO_AGEWIDTHS,
			   gender='combined', ax_calc_alg='graduated',
			   ageWidth=5, qxMax=.7, qx0_intercept=0.93, qx0_slope=1.7):

	'''
	From a given nMx schedule, calc and return a functional or the
	full LT.  The columns for a full LT are nmx, nqx, lx, nLx, Ex.

	extensionMethod=[LARRY_DEFAULT_EXTENSION_METHOD]

	ltFuncType=["ex", "lx", "lxPercent", "depRatio", "full"]

	closeRate must be an age with "ex" and "lx"; a percentile with "lxPercent",
	a pair of ages (young and old) with "depRatio".


	XXX Full of magic numbers!
	'''
	#logging.debug( 'gender: %s' % gender)

	assert N.isfinite(nmxp).all(), AssertionError("%s" % pprint.pformat(locals()))
	assert len(nmxp.shape) == 1, AssertionError(
		"Bad shape for nmxp: %s. Should be %s" % (str(nmxp.shape), '(x,)'))
	if gender not in ('combined', 'male', 'female'):
		raise LcException("Bad value for gender in lifeTable(): %s" % gender)
	if N.isnan(nmxp).any() or N.isinf(nmxp).any():
		raise "Bad mx: %s" % nmxp
	
	# Copy nmx to avoid modifying a reference
	nmx = nmxp.copy()
	
	# set nmx's that creep in as inf to something big
	nmx[N.isinf(nmx)] = LARRY_INF_NMX_REPLACEMENT
	assert N.isfinite(nmx).all(), AssertionError("%s" % pprint.pformat(locals())) 

	# extend nmx out to appropriate age widths.  Filling with stuff to
	# make it break if they are not replaced in the Kannisto
	# extension thing
	neededSlots = numAgeWidths - nmx.shape[0]
	if neededSlots > 0:
		nmx.resize(numAgeWidths)
		
	# Set up data structures
	nqx = N.array([1.0] * numAgeWidths, N.float64)
	lx =  N.array([0.0] * numAgeWidths, N.float64)
	nLx = N.array([0.0] * numAgeWidths, N.float64)
	ndx = N.array([0.0] * numAgeWidths, N.float64)
	Ex = N.array([0.0] * numAgeWidths, N.float64)
	Tx = N.array([0.0] * numAgeWidths, N.float64)
	ax = N.array([0.0] * numAgeWidths, N.float64)

	# Extend bad data ages
	if ageCutoff:
		nmxOld = copy.copy(nmx)
		nmx = LcExtension.extendMx(nmx, extName=extensionMethod, ageCutoff=ageCutoff)	
		assert N.isfinite(nmx).all() and (nmx>0).all(), \
			   AssertionError("%s" % pprint.pformat(locals())) 

	# Graduate and get important stuff
	(ax, qx, dx, lx) = adjustAx(nmx, gender=gender)
	#raise pprint.pformat((ax, qx, dx, lx))

	# Everything ->  nLx
	if ax_calc_alg == 'LiNan':						# Default
		for i in range(len(nLx)-1):
			nLx[i] = (lx[i] - lx[i+1])/nmx[i]
			pass
		nLx[-1] = lx[-1]/nmx[-1]
		pass
	elif ax_calc_alg == 'graduated':								# Not usually entered
		nLx[0] = lx[0] - ax[0] * ndx[0]
		nLx[1] = lx[1] - ax[1] * ndx[1]
		nLx[2:-1] = (lx[2:-1] * 5) - (ndx[2:-1] * ax[2:-1]) # Magic numbers 5, 2.5: age width and multiplier 
		nLx[-1] = lx[-1] / nmx[-1]
		nLx[N.where(abs(lx)<.0001)] = 0.0		# coarse
	elif ax_calc_alg == 'empirical':
		pass
	else:
		raise Exception ('Unknown ax_calc_alg: %s' % ax_calc_ag)
	# Do strange adjustment for lx where x >= 10, from lfexpt.m
	#   Set up datastructures ...
	if False:
		c = N.zeros_like(nLx)
		nLLx = N.zeros_like(nLx)
		llx = lx.copy()
		qqx = N.zeros_like(nLx)
		
		#   ... compute adjustment "c" for each age ...
		for age in range(3, len(nLLx)-1):
			if nLx[age] > 0.000001:
				c[age] = (1/(48*nLx[age])) * \
						 (nLx[age-1]-nLx[age+1]) * \
						 (nmx[age+1] - nmx[age-1])
			else:
				c[age] = c[age-1]
				pass
			pass

		#   ... recalculate lx with adj and mort rates ...
		for age in range(3, len(nLLx)-1):
			llx[age+1] = llx[age]*N.exp(-5*(nmx[age]+c[age]))
			
		#   ... recalculate Lx and qx ...
		for age in range(0, len(nLLx)-1):
			nLLx[age] = (llx[age] - llx[age+1]) / nmx[age]
			qqx[age] = (llx[age] - llx[age+1]) / llx[age]
		qqx[-1] = 1.0
		nLLx[-1] = nLLx[-2]

		#   ... copy to lx and nLx, then Finis.
		lx = llx.copy()
		nLx = nLLx.copy()
		pass
	
	# nLx -> Tx 
	Tx = N.cumsum(nLx[::-1])[::-1]		# Double reverse by indexing stride 
	
	# Tx + lx -> ex
	Ex = Tx/lx
	Ex[N.isnan(Ex)] = 0
	Ex[-1] = 1/nmx[-1]

	# Sanity
	
	assert 10 < Ex[0] < 100, \
		   AssertionError ("Unreasonable LifeExp: %s. %s" % (Ex[0], pprint.pformat(locals())))

	# Decide what to return.  For the functionals, use the parameters
	# to figure out what parts of the lifetable want.
	if ltFuncType == 'ex':
		xTmp = LARRY_AGE_INDICES[beginFuncParam]
		assert 0 <= xTmp <= max(LARRY_AGES), "Bad age: %s" % beginFuncParam 
		return (float(Ex[xTmp]))
	elif ltFuncType == 'lx':
		xTmp = LARRY_AGE_INDICES[beginFuncParam]
		assert 0 <= xTmp <= max(LARRY_AGES), "Bad age: %s" % beginFuncParam
		return (float(lx[xTmp]))
	elif ltFuncType == 'lxPercent':
		lxTmp = beginFuncParam / 100.0
		assert 0.0 < lxTmp <= 1.0, \
			   AssertionError("Bad percentile: %s." % beginFuncParam)
		lxInterp = scipy.interpolate.interp1d(lx[::-1], LARRY_AGES[::-1]) # both x and lx reversed
		return lxInterp(lxTmp).ravel()[0]
	elif ltFuncType == 'depRatio':
		xTmpYoung =  LARRY_AGE_INDICES[beginFuncParam]
		xTmpOld = LARRY_AGE_INDICES[endFuncParam]
		assert 0 <= xTmpYoung < xTmpOld <= max(LARRY_AGES), \
			   AssertionError ("Bad ages: Young: %s, Old: %s" % (beginFuncParam, endFuncParam))
		ppyYoung = N.sum(nLx[0:xTmpYoung]) # Total person years
		ppyWorking = N.sum(nLx[xTmpYoung:xTmpOld])
		ppyOld = N.sum(nLx[xTmpOld:])
		return ppyWorking / (ppyYoung + ppyOld)
	elif ltFuncType == 'full': return (S.array(zip( nmx, nqx, lx, nLx, Ex)))
	else: raise Exception, "unknown ltFuncType: %s"	% str(locals())


def tablefy (dataList, headings, sideLabels=[], itemName="Item", precision=4):
	"""
	Create table of possibly inconsistently long stuff
	"""
	# Set up stuff for local environment when executing
	if dataList==None:
		raise 'dataList == None'
	
	p_opts = N.get_printoptions()
	N.set_printoptions(precision=precision)
	def formatCell(x):
		if x == LARRY_NULL_NUMBER or x is None: return '&nbsp;'
		else: return str(x)

	# Transform everything into numpy arrays
	for i, dataItem in enumerate(dataList):
		#if type(dataItem) is not N.ndarray:
		dataList[i] = N.array(dataItem)

	# Find longest dimension of all the data
	rowDim = 0
	for dataItem in dataList:
		if dataItem.shape[0] > rowDim:
			rowDim = dataItem.shape[0]

	# Create a target matrix
	colDim = len(dataList)
	statArray = S.zeros((rowDim, colDim), N.float64)
	#wtf = statArray.list()
	statArray[...] = LARRY_NULL_NUMBER
	

	# ...insert stuff into the columns, then use the matrix to build
	# an html table row by row with header and footer, using '&nbsp;'
	# for empties ....  
	for colIndex, dataItem in enumerate(dataList):
		statArray[0:dataItem.shape[0], colIndex] = dataItem 
	if type(statArray) is not N.ndarray:
		raise "wtf? %s" % statArray
	
	# ... include table headings in initial string ...
	resultsTable = "<table border='1'>\n"
	resultsTable += "<tr><th>" + itemName + "</th><th>" + '</th><th>'.join(map(str, headings)) + "</th></tr>\n" 
	for sideLabel, row in map(None, sideLabels, statArray):	
		label_s = formatCell(sideLabel)
		if type(statArray) is not N.ndarray:
			raise "wtf? %s" % statArray
		try:
			rows_s = '</td><td>'.join(map(formatCell, row))
		except Exception, e:
			raise "%s.\n%s." % (e, (row, statArray))
		resultsTable += '<tr><td>' + label_s + '</td><td>' + rows_s + '</td></tr>\n'
	resultsTable += '</table>'

	N.set_printoptions(p_opts)
	return(resultsTable)
	

def mat2table(mat, prec=2, name=None):
	outStr = '<pre>\n'
	if name:
		outStr += 'Matrix name: %r.  ' % name
	outStr += 'Matrix dimensions: %r\n.' % (mat.shape,)
	outStr += '</pre>\n'
	
	outStr += '<table>\n'
	try:
		mat = N.around(mat, prec)
	except TypeError:
		raise "bad matrix:\n\n%r\n" %(mat,)
	if len(mat.shape) == 2:
		for r in list(mat):
			outStr += '<tr>'
			for item in list(r):
				outStr += '<td>' + str(item) + '</td>'
			outStr += '</tr>\n'
	elif len(mat.shape) == 1:
		for r in list(mat): 
			outStr += '<tr><td>' + str(r) + '</td></tr>\n'
	else:
		raise LcException, "Can't print matrices with dim > 2"
	return outStr + '</table>\n'

def mat2text(mat, indent_level=0, fieldsep=LARRY_FIELDSEP, rowsep=LARRY_ROWSEP, stanzasep=LARRY_STANZASEP):
	""" Formats a matrix.  XXX: Note that it adds terminal newlines in a strange way."""
	
	
	if len(mat.shape) == 3:
		retList = []
		matList = mat.tolist() 
		for square in matList:
			tmpString = ''
			for row in square: 
				tmpString += ("\t"*indent_level) + fieldsep.join([( "%.6f" % x) for x in row]) + '\n'
			retList.append(tmpString)
		return rowsep.join(retList) + '\n'

	elif len(mat.shape) == 2:
		matList = mat.tolist()
		tmpString = ''
		for row in matList:
			tmpString += ("\t"*indent_level) + fieldsep.join([("%.6f" % x) for x in row]) + '\n' 
		return tmpString
	
	elif len (mat.shape) == 1:
		matList = mat.tolist() 
		tmpString = ("\t"*indent_level) + fieldsep.join([("%.6f" % x) for x in matList]) + '\n'
		return tmpString
	
	elif len(mat.shape) == 0:
		tmpString = ("\t"*indent_level) + "%.6f%s" % (mat, rowsep)
		return tmpString
	
	else:
		raise Exception("Should have returned from one of the cases.")
	
	
############ Fitting routines 
def kt2e0(kt, ax, bx, lifeTableParams):
	"""
	kt is a scalar. ax, bx are vectors.
	"""
	assert ax.shape == bx.shape, Exception("%r" % locals())
	nmx = S.exp(ax + (bx * kt))
	lifeTableParams_copy = copy.copy(lifeTableParams)
	return (lifeTable(nmx, **lifeTableParams_copy))


def multiKt2e0(kt, ax, bx, lifeTableParams, numAgeWidths = LARRY_DEFAULT_NO_AGEWIDTHS):
	e0s = [0] * len(kt)
	for i, k in enumerate(kt):
		nmxTmp = N.zeros((1,numAgeWidths), N.float64).ravel()
		nmxTmp[0:len(bx)] = N.exp(k * bx + ax)
		nmxTmp = LcExtension.extendMx(nmxTmp, ageCutoff=lifeTableParams['ageCutoff'])
		e0s[i] = lifeTable(nmxTmp, **lifeTableParams) 
		del nmxTmp 
	return e0s
		

def fitX(func, target, *funcArgs, **funcKwargs):
	"""
	e.g. fitX(func=kt2e0, target=77.338912, ax=ax, bx=bx) == 5.  
	"""

	def curryFuncWithTarget(func, target, *funcArgs, **funcKwargs):
		argsP = funcArgs
		kwargsP = funcKwargs
		def f(x):
			return (func(x, *argsP, **kwargsP) - target)**2
		return f 
	cf = curryFuncWithTarget(func, target, *funcArgs, **funcKwargs)
	(out, infodict, ier, mesg) = [None]*4
	try:
		(out, infodict, ier, mesg) = scipy.optimize.fsolve(
			func=cf, x0=((2*S.rand())-0.5), full_output=1, xtol=1.0e-04)
		if ier == 1:
			logging.debug( "Successful fsolve\n")
		else:
			logging.warning("Problem with fsolve. ier = %s, mesg = \"%s.\"\n %s\n" % \
						  (ier, mesg.replace('\n', ' '), infodict))
	except Exception, e:
		logging.error( "Exception with fsolve: \"%s\".  Catching and ignoring..." % e)
	return out


#################
def parseDate(data):
	try:
		return int(data)
	except ValueError, e:			# This gets raised if you try to parse 'California' as a number
		raise LcInputException, e 


def parseRates(data, numAgeWidths = LARRY_DEFAULT_NO_AGEWIDTHS):
	"""
	Parse the text data and return Numeric arrays

	Allow lines to begin with NA and fill them with nans.
	"""

	# Clean head and tail of data
	data = re.sub(LARRY_HEAD_WS_RE, '', data)
	data = re.sub(LARRY_TAIL_WS_RE, '', data)
	
	# Read in data to float/nan: Split data into lines, create nan
	# matrix, look fo for 'NA' in bgin and let nan data stay or split
	# into fields and insert
	lines = re.sub(LARRY_END_WS_RE, '', data).split('\n')
	lines = [x for x in lines if not LARRY_COMMENT_LINE_RE.match(x)] # Pull out full line comments
	lines = [LARRY_COMMENT_TRAILING_RE.sub('',x) for x in lines] # Get rid of trailing comments
	
	out = N.zeros((len(lines), numAgeWidths), N.float64)
	out[...] = N.nan 
	for i, line in enumerate(lines):
		if re.match(LARRY_EMPTY_ROW_RE, line): # Leave line as all nans, to indicate missing year
			#Warn("parsing empty year: i:%i, data:%r" % (i, line))
			continue
		else:
			try:
				lineSplit = map(float, line.split())
			except ValueError, e:
				raise LcInputException('Bad value for a row of floating point numbers: "%s".' % line)
			out[i,0:len(lineSplit)] = lineSplit 
			pass
		
	# Check for reasonable values
	if (out<0).any() or N.isinf(out).any():
		raise LcInputException, "Succesffuly parsed but infs or negatives mx in array." + \
			  "Here is the parsed array: %r\n"  % (out)
			
	# Adjust for zero values, just for the hell of it
	out = out + 0.0000001
	return out


def emptyLikeWithNans(arr, nanRowsBool=None):
	'''Create an array like the '''
	a = N.empty_like(arr)
	a[...] = N.nan
	return a

def dumpObject(obj, dontDump=[], annoStructure=[], helpParagraph='', 
			   fieldsep=LARRY_FIELDSEP, rowsep=LARRY_ROWSEP, stanzasep=LARRY_STANZASEP):
	""" Dumps an object, avoids certain attributes with 'dontDump',
	sorts and annotates the dumped fields with annoStructure:
	[(fieldname1,explanation), (fieldname2, explanation), ...]."""

	# Grr -- stupid linebreaks!!
	N.set_printoptions(linewidth=1000000, threshold=1000000, precision=6) # Stupid interactive bullshit

	# Collector variables
	dataStr = ''
	tocList = []

	# annotation stuff
	annotationArray = N.array(annoStructure)	# M x 2 text array
	# Make sure annotation the right size
	assert annotationArray.size==0 or annotationArray.shape[1] == 2, \
		   AssertionError('Bad size Annotation array: %s\n\n%s\n' % (annotationArray.shape,annotationArray))

	# Figure out which variables to dump
	dontDump = set(dontDump)
	varsObject = set(obj.__dict__)
	varsObjectDumpable = varsObject.difference(dontDump)
	if  annotationArray.size != 0:	# Have annotations
		varsAnnotated = set(annotationArray[:,0])
		varsNotAnnotated = varsObjectDumpable.difference(varsAnnotated)
		
		# Make sure that all the annotation fields are also in the __dict__ 
		extraAnnotations = (varsAnnotated - varsObject)
		assert not extraAnnotations, \
			   AssertionError("Unknown variables in annotation list: %s" % sorted(list(extraAnnotations)))
	else:
		varsAnnotated = set()
		varsNotAnnotated = varsObjectDumpable
		
	# Handle annotated variables
	if not annotationArray.size == 0:
		for name, descr in annotationArray:
			dataStr += formatRecurse(item_name="%s (%s)" % (name,descr), item=obj.__dict__[name]) + '\n'
			tocList.append(name)
			pass

	dataStr += '\n----\n'
	# Handle non annotated variables
	for name in sorted(varsNotAnnotated, reverse=True):
		dataStr += formatRecurse(item_name="%s" % (name), item=obj.__dict__[name]) + '\n'
		tocList.append(name) 
		pass

	return helpParagraph + '\n---\n' + "VARIABLES DISPLAYED: " + ', '.join(tocList) + '\n---\n' + dataStr


def formatRecurse(item_name, item, indent_level=0):
	"""Formats 'item', recursing over the items if it is iterable, indenting, etc."""

	# Grr -- stupid linebreaks!!
	N.set_printoptions(linewidth=1000000, threshold=1000000, precision=6) # Stupid interactive bullshit

	returnStr = ''

	#if re.match('.*bx.*', item_name):
	#	assert isinstance(item, N.ndarray), 'WTF? %s: %s' % (item_name, item)
		
   	# ... if at a base thing (scalar or matrix), return a formatted version of it at indent_level ...
	if isinstance(item, (types.IntType, types.FloatType, types.StringType, types.LongType, types.BooleanType, N.number)):
		return '\t' * indent_level + str(item_name) + '\t' + str(item) + '\n'

	# .. if a numpy array, use mat2text
	elif isinstance(item, N.ndarray):
		return '\t' * indent_level + str(item_name) + '\n' + mat2text(item, indent_level=indent_level+1) + '\n'
	
	# ... if at a dict or a list, iterate over each element, appending
	# either a count number or the key name, then appending a
	# recursive call of formatDump on the elements
	elif (type(item) is types.DictType):
		return '\t' * indent_level  + str(item_name) + '\n' + \
			   ''.join([formatRecurse(item_name=key, item=val, indent_level=indent_level+1)
						for key,val in sorted(item.iteritems())]) + '\n'
	
	elif (type(item) is types.ListType
		  or type(item) is types.TupleType
		  or isinstance(item, set)):
		return '\t' * indent_level + str(item_name) + '\n' + \
			   ''.join([formatRecurse(item_name=str(num), item=val, indent_level=indent_level+1)
						for num,val in enumerate(item)]) + '\n'

	# ... otherwise ignore it
	else:
		return ''

	return returnStr

if __name__ == '__main__':
	print 'LcUtil.py'

	mx_short = N.array([0.0208, 0.0013, 0.0006, 0.0005, 0.0007, 0.0012,
						0.0012, 0.0014, 0.0019, 0.0026, 0.0043, 0.0066, 0.0105, 0.0170,
						0.0278, 0.0479, 0.0821, 0.1417, 0.2562, 0.3873, 0.5262, 0.6443,
						0.7110, 0.7421], N.float64) # From group0s mx(1,:)'
	print 'e0 from mx_short: %s' % (lifeTable(mx_short))

	mx_long = N.array([0.02079658742137, 0.00128868634199,
					   0.00061416299465, 0.00049210540671, 0.00071345243780,
					   0.00119963287953, 0.00124033393150, 0.00144911935429,
					   0.00191817457775, 0.00263050053745, 0.00428255832515,
					   0.00661687991321, 0.01047558912858, 0.01697710484496,
					   0.02783064122818, 0.04787244816939, 0.08208186889827,
					   0.14174619371789, 0.25619714240341, 0.38727453676257,
					   0.52622000215332, 0.64425795885847, 0.71102036773448,
					   0.74208186889827], N.float64)
	print 'e0 from mx_long: %s' % (lifeTable(mx_long))
