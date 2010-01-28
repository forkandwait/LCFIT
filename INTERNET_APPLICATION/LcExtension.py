"""
This module is hereby the repository for all the mx extension code.
THis includes all of the Coale Guo versions, etc.  The module's architecture is:

(1) all the extension functions take a vector of mx and a standard
    parameter list and have a standard name.

(2) these functions are listed in a module level hash with a reference
    to the func; the default algorithm is set module-wide.

(3) the caller just uses one f() to extend either a matrix or vector
    of mx, and this data is munged and passed to the appropriate
    extension f.

So if you want to add a new extension algorithm, write it and store it in here.

"""
from LcConfig import *
sys.path.append('.')
sys.path.append('..')

# This imports strangely if we try to use LcUtil, so define it here
def Diagnose(*printVars):
	outvars = [str(x).translate(string.maketrans('<>', '{}')) for x in printVars ]
	raise Exception, "%s" % pprint.pformat(outvars, width=-1)
D = Diagnose

###############################################
## Infrastructure -- module variables and useful
##   functions
###############################################

# Match name of function that can be used for mx extension
EXTENSION_PREFIX_RE = re.compile('^mxExtend_.*$')

# Hash of name - func for such things.  Fill in after the functions are defined below.
EXTENSION_METHODS = {}

# CHOSEN EXTENSION METHOD
EXTENSION_NAME = ''

## 
def qxLessThanOne(mxData, doThis=False):
	"""Adjust mx so that qx won't be greater than 1.0, by capping the death rates at all ages."""
	if doThis:
		if mxData[23] > 0.78:
			mxData[23] = 0.78
		if mxData[22] > 0.66:
			mxData[22] = 0.66
		tmp = mxData[:21]
		tmp[tmp>0.4] = 0.4
		mxData[:21] = tmp
		pass
	else:
		pass
	return mxData


##
def extendMx(mxData, extName=None, **kwargs):
	''' Extends a copy of mxData, converting to array if necessary,
	using the module level choice for extension.'''

	global EXTENSION_METHODS
	global EXTENSION_NAME
	
	if extName is None:
		eFunc = EXTENSION_METHODS[EXTENSION_NAME]
	else:
		if EXTENSION_METHODS.has_key(extName):
			eFunc = EXTENSION_METHODS[extName]
		else:
			raise LcException("Unavailable mx extension name: %s.  \n\tAllowed extensions: %s" % \
							  (extName, EXTENSION_METHODS.keys()))
		
	mxArray = convertMxData(mxData)
	if len(mxArray.shape) == 1:
		mxArray = qxLessThanOne(mxArray)
		return eFunc(mxArray, **kwargs)
	elif len(mxArray.shape) == 2:
		collector = [] 
		for row in mxArray:
			row = qxLessThanOne(row)
			## Check ext data?
			collector.append(eFunc(row, **kwargs))
			## Check ext result?
		return N.array(collector, N.float)
	else:
		raise LcException('extendMx:  bad data: %s' % mxData)


##
def convertMxData(mxData):
	''' Converts Mx data into either a vector, for single year data,
	or a Year x Age matrix, for multi-year data.'''
	
   	try:
		mxArray = N.array(copy.copy(mxData), N.float)
	except TypeError:
		raise LcException("Unable to convert mxData to array.  MxData: %s" % mxData)
	if (len(mxArray.shape) not in (1,2)):
		raise LcException("Weird shape in mxArray: %s.  mxArray: %s" % (mxData.shape, mxData))
	assert not N.isinf(mxArray).any(), AssertionError("infinite data in mxArray: %s" % mxArray)
	return mxArray

		
##

def setExtensionName(name):
	"""Sets the name of the extension function that will be used by
	default."""
	
	global EXTENSION_NAME
	global EXTENSION_METHODS
	if name in EXTENSION_METHODS.keys():
		oldName = EXTENSION_NAME
		EXTENSION_NAME=name
	else:
		raise LcException("Unallowed extension name: %s. Allowed: %s" % (name, EXTENSION_METHODS.keys()))
	
	#raise Exception("wtf?")
	return oldName

def LT1YrTo5Yr(mx, multiplier=0.008):
	""" Convert 1_m_x to 5_m_x by way of a life table.  Based on Li
	Nan's code (inside his CG function)."""

	# qx ...
	q = N.zeros_like(mx)
	for i in range(0,len(q)):
		q[i] = 1 - N.exp(-(mx[i] + multiplier*(mx[i]**2)))
		pass
	assert (q>0.0).all(), AssertionError("Grr %s" % q)

	# lx ...
	lx = N.zeros_like(mx)
	lx[0] = 1.0
	for i in range(1, len(lx)):
		lx[i] = lx[i-1] * (1-q[i-1])
		pass
	
	# ... fill lx 5-year from 1-year  ...
	cnt5yr = N.int0(mx.shape[0]-1) / 5
	lx5 = N.zeros(cnt5yr+1, N.float)
	Lx5 = N.zeros(cnt5yr, N.float)
	n1index = 0
	for n5index in range(0, cnt5yr):
		Lx5[n5index] = 0
		lx5[n5index] = lx[n1index]	# Grab lx from 80, 85, etc
		for i in range(0,5):
			Lx5[n5index] = Lx5[n5index] + 0.5*(lx[n1index] + lx[n1index+1])
			n1index += 1
			pass
		pass

	# ... fill 5 yr mx from 5 yr lx ...
	mx5 = N.zeros(cnt5yr+1, N.float)
	for i in range(0, len(mx5)-1):
		assert lx5[i] >= lx5[i+1], AssertionError("%s\n%s, %s, %s" % (lx5, lx5[i-1], lx5[i], i))
		mx5[i] = (lx5[i] - lx5[i+1]) / Lx5[i] # XXX i loops around!!
		pass

	# ... return after filling end mx.
	mx5[-1] = mx[-1] 					# inf_m_5 = inf_m_1
	return mx5

def checkExtData(mx, ageCutoff, ageClose, closeRate, closeAddend, closeAddAge):

	cutoffIndex = LARRY_AGE_INDICES[ageCutoff] 

	assert ((len(mx) >= cutoffIndex)), \
		   LcException("mx vector too small. Age cutoff: %s, mx: %s." % (ageCutoff, zip(LARRY_AGES,mx)))

	assert N.isfinite(mx[0:cutoffIndex]).all(), \
		   LcException("mx vector need defined data before cutoff.  cutoff: %s. mx: %s." % (ageCutoff, mx[0:cutoffIndex]))

	assert (mx[0:cutoffIndex]>1.0e-06).all(), \
		   LcException("mx has implausibly low values (zeros?): %s." % mx[0:cutoffIndex])

	assert ((ageClose % 5 == 0) & (ageClose > 0)), \
		   LcException("Closing age must be multiple of 5 and over age 90: %s" % ageClose)

	return True

def checkExtResult(mx, mx_extended, ageCutoff, ageClose, closeRate, closeAddend, closeAddAge):

	cutoffIndex = LARRY_AGE_INDICES[ageCutoff] + 1

	assert len(mx_extended) == LARRY_AGE_INDICES[ageClose]+1, \
		   LcException("Weird mx length: %s\n%s\n" % (len(mx_extended), mx_extended))

	return True

#########################################
## Extension algorithms
#########################################
def mxExtend_Null(mx, *args, **kwargs):
	""" Return the same mx as passed in.  For testing and logical
	completion."""
	
	return mx


##
def mxExtend_Boe(mx, ageCutoff=LARRY_DEFAULT_AGE_CUTOFF, ageClose=110, closeRate=None, closeAddend=.66, closeAddAge=75):
	""" From Carl's matlab code"""

	try:
		checkExtData(mx, ageCutoff, ageClose, closeRate, closeAddend, closeAddAge)
		cutoffIndex = LARRY_AGE_INDICES[ageCutoff]

		mFinish = mStart = -1.0
	
		mx_shp = mx.shape
		mFinish = mx[cutoffIndex]			# Throws an error but I can't figure out why if cutoffindex > 
		mStart = mx[cutoffIndex-1]
		K = N.log(mFinish/mStart)
		starterInd = LARRY_AGE_INDICES[closeAddAge]
	
		if (closeRate == None):
			closeRate = closeAddend + mx[starterInd]	# CG closeout assumption, typically m_75 + .66.
			pass

		# Get important coefficients ...
		# ... "A" is the number of age groups from 80 to ageClose ...
		A = N.floor((ageClose - ageCutoff)/5)

		# ... "s" is the addend from the CG paper ...
		s = N.log(closeRate) - N.log(mFinish) - A*K	
		divisor = (A*(A+1))/2 			#  divisor = A + (A-1) + (A-2) + (A-3) + ... + 1
		s = -s / divisor      # Since we are adding recursively for each age,
							  # need units such that we multiply to get recursive effect

		# ... set up receiving infrastructure ...
		addedages = N.arange(ageCutoff+5, ageClose+5, 5)
		addedmx = N.zeros(len(addedages), N.float)
		addedmx[...] = N.nan

		# ... start the figuring of C-G at ageCutoff+5 ...
		tmp = mFinish * N.exp(K - s)
		assert N.isfinite(tmp), \
			   AssertionError("non-finite tmp: \ntmp:%s\n mFinish: %s\n K: %s\n s: %s\n mx: %s" % \
							  (tmp, mFinish, K, s, zip(LARRY_AGES, mx)))
		addedmx[0] = tmp					# age 85 ?
		tmpdiff = 0

		# ... get the rest of the ages ...
		## CANDIDATE FOR INLINE
		for i in range(2, len(addedmx)+1):
			tmpnew = tmp*N.exp(K - i*s)	# The next candidate mx.  Note that limit of this is 1.0

			if tmpnew < tmp:				# To keep from dipping after the closing age, as we zoom off to age = nmax
				tmpnew = tmp + tmpdiff
			tmpdiff = tmpnew - tmp			# Only use this if we have to avoid the post ageClose dip, used in next loop 
			tmp = tmpnew					# iteration step
			addedmx[i-1] = tmp 

		# Fix mx greater than 1.0 to be 1.0
		addedmx[addedmx>1.0] = 1.0

		# ... check for weirdness, but basically finished.
		assert N.isfinite(addedmx).all() & N.isfinite(tmp), \
			   AssertionError("locals: \n\n%s" % string.join(map(str,locals().items()), '\n')) 

		# Construct extended mx vector for return
		mx_extended = N.hstack((mx[0:cutoffIndex+1], addedmx))		# concat original unchanged with new

		# Finis
		checkExtResult(mx, mx_extended, ageCutoff, ageClose, closeRate, closeAddend, closeAddAge)
	except Exception, e:
		raise "WTF? %s\n   locals(): %s\n" % (e, pprint.pformat(locals()))

	return (mx_extended)


def mxExtend_CGNan(mx, ageCutoff=LARRY_DEFAULT_AGE_CUTOFF, ageClose=110, closeRate=-999.0, closeAddend=0.66, closeAddAge=75):
	""" From Li Nan's matlab code in Coherent package.  2006-11-20."""

	# Check OK data
	checkExtData(mx, ageCutoff, ageClose, closeRate, closeAddend, closeAddAge)
	closeIndex = LARRY_AGE_INDICES[ageClose]
	
	cutoffIndex = LARRY_AGE_INDICES[ageCutoff]
	mFinish = mx[cutoffIndex]			   
	mFirst = mx[cutoffIndex-1]
	K = 0.2 * N.log(mFinish/mFirst)	# * 0.2 because we are going to do single ages
	mStart = mx[cutoffIndex] * N.exp(3*K) # the mx we will start interpolating with 

	if (closeRate == -999.0):
		starterInd = LARRY_AGE_INDICES[closeAddAge]
		x=0.0
		foo=0.0
		closeRate=0.0
		try: 
			x = mx[int(starterInd)]
			foo = x + closeAddend 
			closeRate = foo	# CG closeout assumption, typically m_75 + .66.
		except IndexError,e:
			D(x, foo, starterInd, type(starterInd), closeRate, type(mx), e, mx)

	# Get important coefficients ...
	# ... "A" is the number of age groups from 80 to ageClose, by n=5 ...
	A = N.floor((ageClose - ageCutoff)/5) +1 
	
	# ... "HA" is the number of single year steps ...
	HA = ageClose - ageCutoff + 1 - 5		# "+1" ??; "-5" ??

	# ... cntAddends is number of times we will add "s".  Like (A*(A+1))/2 but one less in the result (1,0), (2,1), (3,3)
	cntAddends = (HA*(HA-1))/2
	sNum = N.log(closeRate) - N.log(mStart) - HA*K # 
	s = sNum / cntAddends

	# ... make and fill single year mx's ...
	mxInterp = N.zeros(HA, N.float)
	mxInterp[...] = N.nan
	for i in range(1, HA+1):				# Grr zero indexes!!!!
		prop = N.exp(i*K + s*i*(i-1)/2)
		mxInterp[i-1] = mStart * prop
		pass
	assert N.isfinite(mxInterp).all() and (mxInterp>10e-8).all() and (mxInterp<10.0).all() , \
		   "f'ed up mxInterp: %s. \n\tmFirst, mFinish, mStart: (%s, %s, %s). \n\tmx: %s." % \
		   (mxInterp, mFirst, mFinish, mStart, zip(LARRY_AGES,mx))

	# ... re-convert mx to 5 years....
	
	mx5interp = LT1YrTo5Yr(mxInterp)
	assert (mx5interp>0).all(), "Grr: %s." % ([mx5interp, mxInterp, mx])

	# ... fill out matrix and return.
	mxOut = N.zeros(closeIndex+1, N.float)
	"""
	assert mxOut[:-len(mx5interp)].shape == mx[:-len(mx5interp)].shape, \
		   AssertionError("%s %s %s %s %s %s" % \
						  ( mxOut[:-len(mx5interp)].shape,  mx[:-len(mx5interp)].shape,
							mx5interp.shape, ageClose, LARRY_AGE_INDICES[ageClose], closeIndex+1))
	"""
	keepMxIndex = closeIndex - len(mx5interp) + 1
	#D(keepMxIndex, mxOut.shape, mx5interp.shape)
	mxOut[:keepMxIndex] = mx[:keepMxIndex]
	mxOut[keepMxIndex:] = mx5interp
	
	assert (mxOut>0.0).all(), AssertionError("Grr. \n\t\tmxOut: %s, \n\t\tmx: %s, \n\t\tmx5interp: %s. %s" \
										   % (mxOut, mx, mx5interp, ageClose))
	return mxOut

############
## Register allowed extension functions
for name, func in [(x,globals()[x]) for x in globals().keys() if EXTENSION_PREFIX_RE.match(x)]:
	EXTENSION_METHODS[name] = func


if __name__ == '__main__':

	import matplotlib as M
	import pylab as P
	import os
	import sys

	setExtensionName('mxExtend_CGNan')
	# The standard ages
	ages = [0,1] + range(5,115,5)

	# Check my little 1 yr to 5 yr thing. following is age 79 - 110
	sweden_1yr_1975 = N.array([ 0.0641,
								0.073 ,  0.0802,  0.0922,  0.1051,  0.1149,	# 80  -  84
								0.1267,  0.1443,  0.1599,  0.1754,  0.1858,	# 85  -  89
								0.2117,  0.2183,  0.226 ,  0.266 ,  0.3262, # 90  -  94
								0.3028,  0.376 ,  0.3714,  0.4414,  0.5078, # 95  -  99
								0.4337,  0.6747,  0.219 ,  0.871 ,  0.6   , # 100 - 104
								0.4615,  2.    ,  1.    ,  1.    ,  3.    , # 105 - 109
								1.    ])                                    # 110 (+)
   	#  Test data female n=5 sweden 1975
	#                       0        1       5        10       15      20
	#                       25       30      35       40       45
	#                       50       55      60       65       70
	#                       75       80      85       90       95
	#                       100      105     110
	
	# 1975 Female in HMD
	sweden_rates_txt = "0.007188 0.000388 0.000251 0.000259 0.000437 0.000354 " + \
					   "0.00052  0.000723 0.000981 0.001674 0.002619 " + \
					   "0.003882 0.005682 0.008934 0.015387 0.027273 " + \
					   "0.051968 0.090435 0.152816 0.233434 0.359285 " + \
					   "0.502831 1.142857 1.0"
	sweden_rates_to_110 = N.array(map(float, sweden_rates_txt.split()))
	sweden_rates_to_80 = sweden_rates_to_110[0:-6]
	# Run all the different extend methods on 5-yr mx's, and graph them together
	P.figure(1)
	coll = []							# Collect the data

	sw = N.log(LT1YrTo5Yr(sweden_1yr_1975[1:]))
	P.plot(ages[-len(sw):], sw, label='sw_via_5y')
	print EXTENSION_METHODS.keys() # mxExtend_CGNan, mxExtend_Boe
	for cg, ageCutoff, closeAddend in [(x,y,z) for x in ['mxExtend_CGNan'] for y in [80] for z in [0.66]]:
		setExtensionName(cg)
		x = extendMx(sweden_rates_to_80, ageCutoff=ageCutoff, closeAddend=closeAddend)
		assert len(x) == len(ages[0:(len(x))]), \
			   LcException("%s, %s" % (len(x), len(ages[0:(len(x))])))
		label = "%s-%s-%s" % (cg,ageCutoff,closeAddend)
		print '\n', label, '\n', N.array(zip(ages, N.log(x)))
		P.plot(ages[0:len(N.log(x))], N.log(x), label=label)
		coll.append(x)
		pass		
	
	P.grid()
	P.xlim(0, 140)
	FF = M.font_manager.FontProperties(size='xx-small')
	P.legend(loc='upper left', prop = FF)
	P.savefig('/home/webbs/public_html/%s.png' % os.path.split(__file__)[-1])
	P.close(1)

	# Confirm that the matrix extension works
	setExtensionName('mxExtend_Boe')
	M = N.array((sweden_rates_to_110, sweden_rates_to_110))
	print "double sweden rates", N.log(extendMx(M))
	#print N.log(extendMx(sweden_rates_to_110.tolist()))
	#print N.log(extendMx(M.tolist()))
	#print N.log(extendMx([1.0, 2.0]))
