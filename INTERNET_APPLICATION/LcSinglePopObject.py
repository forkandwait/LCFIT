#!/usr/bin/python
'''
This module provides the home for LcSinglePopObject, which takes data
in the form of text, runs an Lee-Carter infeence procedure on it, does
some forecasting, and makes some nice pictures.

This module also contains a number of module functions to support
this.
'''

## Imports ################################################
from LcConfig import * 					# Imports numpy and friends
from LcAnnotation import *
import LcExtension
LcExtension.setExtensionName(LCFIT_DEFAULT_EXTENSION_METHOD)
import LcUtil
from LcUtil import Diagnose as D
from LcUtil import listTypes as LT

sys.path.append('./TESTING')			# For test data

## Module Variables  ###### 
LcObjectINFO ='Single Population object' # Project/misc information

# Image constants
LC_IMAGE_NAME = 'lc-model.png'				# Image with kt, ax, bx, e0u
FC_IMAGE_NAME = 'lc-forecast.png'			# Image with forecasted stuff
LNMX_IMAGE_NAME = 'lc-lognmx.png'	# Emprical log nmx at various ages
MORTP_IMAGE_NAME = 'lc-mortp.png'		# Mortality profiles at begin, end, end proj 
IMGH = 150								# Height of all images
IMGW = 200								# Width of all images


## Module Functions ##################################################################

def percent_line(index):
	if index == 0 or index == 4:
		texture = '--'
		linewidth = .5
		dashstyle = (1,2)
	elif index == 1 or index == 3:
		texture = '--'
		linewidth = .5
		dashstyle = (6,2)
	else:
		texture = '-'
		linewidth = .5
		dashstyle = (None,None)
	return texture, linewidth, dashstyle

			
def LC2nMx (ax, bx, kt):
	''' Find nMx schedule given ax, bx, kt '''
	
	## Raise e to vectorised exponent derived from LC algorithm,
	## return this as nMx.
	kt = N.float64(kt)
	lcExponent = (ax + bx * kt)
	nMx = N.exp(lcExponent)

	return(nMx)

def projAr1(c0, c1, stderr_est, innov_count, start=None):
	""" Returns an array of a simulated AR(1) process."""
	if stderr_est == 0:
		errs = N.zeros(innov_count)
	else:
		errs = N.random.normal(0, stderr_est, innov_count)
	innov = N.zeros(innov_count)
	if start == None:
		start = 0 + errs[0]
	innov[0] = start
	for i in range(1,innov_count):
		innov[i] = c0 + innov[i-1]*c1 + errs[i]
		pass							
	return innov

def fitSingleKt(ax, bx, kt, nmx, lifeTableParams):
	'''
	Fit kt such that it generates empirical life expectancy based on
	nMx from input data, constrained by given ax and bx.

	Returns fitted kt.
	'''
	lifeTableParams_copy = copy.copy(lifeTableParams)
	target_e0 = LcUtil.lifeTable(nmx, **lifeTableParams_copy)
	fittedKt = LcUtil.fitX(func=LcUtil.kt2e0, target=target_e0, ax=ax, bx=bx, lifeTableParams=lifeTableParams) 
	return fittedKt


def fitMultiKt(ax, bx, kt, nmx, lifeTableParams):
	'''
	Fit kt based on empirical e0. Iterates over the kt vector and array of
	nmxs (which is 2-d), returning a new kt vector
	'''
	fittedKt = copy.copy(kt)
	fittedKt = fittedKt * 0 
	for i in range(0, nmx.shape[0]):
		fittedKt[i] = fitSingleKt(ax, bx, kt[i], nmx[i,:], lifeTableParams) # ages go across
		foomx = LC2nMx(ax=ax, bx=bx, kt=float(fittedKt[-1]))
		assert (foomx>1.0e-06).all(), \
			   AssertionError("foomx has implausibly low values: %s." % locals())
	return fittedKt


def sim_kt(SEC, SEE, drift, numRuns, stepsForward, ktStart=0,
		   projectionWidth=LCFIT_PROJECTION_WIDTH, sortflag=True):
	'''
	Make a number of stochastic projections for kt as a random walk
	with drift and and standard deviation (sdktnd) from parameters.

	Returns an array populated with these innovations.

	If sortflag is True, sorts this array along the columns, putting
	the highest kt for a given step forward in the top.	 This facilitates 
	finding percentiles for kt for a given year
	'''
	#N.random.seed()
	ktMatrix = N.zeros((numRuns, stepsForward+1), N.float64) # Empty matrix to hold everything
	
	for rowIndex in range (0, numRuns):
		stochDrift = N.random.normal(drift, SEC) 
		stochAdjustments = N.random.normal(0, SEE, stepsForward+1) + stochDrift
		ktMatrix[rowIndex,0] = ktStart	# sets the first element back to start
		for stepIndex in range (1, stepsForward+1):
			ktMatrix[rowIndex, stepIndex] = ktMatrix[rowIndex, stepIndex-1] + stochAdjustments[stepIndex]
		
	# If sortflag, sort across the columns to give a percentile
	# effect.  Use ending column to sort the entire rows with respect
	# to each other.  This means that we keep all the runs intact, but
	# sort on where the run finishes.
	if sortflag=='column-wise':
		ktMatrix.sort(0)
		pass
	elif sortflag==True or sortflag=='end-result':
		sorti = N.argsort(ktMatrix[:,-1])
		ktMatrix = ktMatrix[sorti,:]
		pass

	rmat = copy.copy(ktMatrix)
	del ktMatrix
	return rmat


def sim_kt_ar1(stdckt, c0, sda0, c1, sda1, numRuns, stepsForward, ktStart=0,
			   projectionWidth=LCFIT_PROJECTION_WIDTH, sortflag='end-result'):
	'''
	If sortflag is True, sorts this array along the columns, putting
	the highest kt for a given step forward in the top.	 This facilitates 
	finding percentiles for kt for a given year
	'''
	ktMatrix = N.zeros((numRuns, stepsForward+1), N.float64) # Empty matrix to hold everything
	ktMatrix[:,0] = 0
	#ktMatrix[:,0] = ktStart
	for rowIndex in range (0, numRuns):
		"""
		The following two lines do a single run of simulation in
		multicountry2GCS.m, but I don't understand the rationale at
		all (not that that means anything...)

		zzz=(a0+sda0*rndgce(tind,yind0))+(a1+sda1*rndgce(tind,yind0))*stokc(tind,yind0);
		stokc(tind,yind0+1)=zzz+sdckt*rndgc(tind,yind0);
		"""
		rndgc = N.random.normal(0,1,stepsForward+1)
		rndgce = N.random.normal(0,1,stepsForward+1)
		for i in range(1, stepsForward+1):			
			tmp = (c0+sda0*rndgce[i]) + (c1+sda1*rndgce[i]) * ktMatrix[rowIndex, i-1]
			ktMatrix[rowIndex,i] = tmp + stdckt*rndgc[i]
			pass
		pass
		
	# If sortflag, sort across the columns to give a percentile effect
	if sortflag=='column-wise':
		ktMatrix.sort(0)
		pass
	elif sortflag==True or sortflag=='end-result':
		sorti = N.argsort(ktMatrix[:,-1])
		ktMatrix = ktMatrix[sorti,:]
		pass

	return ktMatrix

def project_nmx(kt, ax, bx, ageCutoff, kt_resid=None, bx_resid=None, numAgeWidths=LCFIT_DEFAULT_NO_AGEWIDTHS):
	"""
	Convert 2-d array of kt forward innovations into 3-d array of nmxs

	To get a particular age profile after running the function, need
	to pick a run and a timestep, eg self.nmx_projected[10, 12, :]
	gives 10th run, t=12, all the age spec rates.

	'Kx' and 'Bx' are for coherent.
	"""
	# Make sure kt_resid and bx_resid are either both None or are the
	# right dimensions for the residual (Coherent) process
	if kt_resid is None and bx_resid is None: # Normal case without coherent
		isCoherent = False
		kt_resid = N.zeros_like(kt)
		bx_resid = N.zeros_like(bx)
		pass
	elif (kt_resid.shape == kt.shape) and (bx_resid.shape == bx.shape):  # Coherent
		isCoherent = True
		pass 
	else:
		raise "Weird mix of kt's and bx's.  \n\nkt: %s.  \n\nkt_resid: %s  \n\nbx: %s  \n\nbx_resid: %s\n" % \
			  (kt, kt_resid, bx, bx_resid)

	# Fill 3d matrix of nmx if get 2-d matrix of kt (corresponding to run by year
	if len(kt.shape) == 2:
		numRuns, stepsForward = kt.shape[0], kt.shape[1]
		nmx_projected = N.zeros([numRuns, stepsForward, numAgeWidths], N.float64) # 3-d matrix to fill in
		for runIndex in range(0,numRuns):
			for stepIndex in range(0,stepsForward):
				nmxTmp = N.zeros((1,numAgeWidths), N.float64).ravel() 
				nmxTmp[0:len(bx)] = N.exp(kt[runIndex,stepIndex]*bx + kt_resid[runIndex,stepIndex]*bx_resid + ax)
				nmx_projected[runIndex, stepIndex, :] = LcExtension.extendMx(nmxTmp, ageCutoff=ageCutoff)
				pass
			pass
		return nmx_projected
		
	# Fill 2d matrix of nmx if have 1-d matrix of kt
	elif len(kt.shape) == 1:		# 
		nmx_projected=N.zeros((kt.shape[0], numAgeWidths), N.float64)
		for yearIndex in range(0, kt.shape[0]):
			nmxTmp = N.zeros((1,numAgeWidths), N.float64).ravel()
			nmxTmp[0:len(bx)] = N.exp(kt[yearIndex]*bx + kt_resid[yearIndex]*bx_resid + ax)
			nmxTmpExtended = LcExtension.extendMx(nmxTmp, ageCutoff=ageCutoff)
			nmx_projected[yearIndex, :] = nmxTmpExtended
		return nmx_projected

	# Fill 1d matrix of mx for single kt number
	elif len(kt.shape) == 0 and kt.size == 1:
		nmx_projected=N.zeros(numAgeWidths, N.float64)
		nmxTmp = N.zeros(numAgeWidths, N.float64)
		nmxTmp[0:len(bx)] = N.exp(kt*bx + kt_resid*bx_resid + ax)
		nmxTmpExtended = LcExtension.extendMx(nmxTmp, ageCutoff=ageCutoff)
		nmx_projected[:] = nmxTmpExtended
		return nmx_projected
	else:
		raise LcException, "Unexpected kt.shape: %r.  kt: %r. kt.size: %r" % ([kt.shape],kt, kt.size)


def lots_e0s(percentileIndices=None, lots_nmx=None, lifeTableParams=None, sortflag='end-result'):
	
	'''
	Calculates and returns a matrix of life exps from a 3-d matrix of
	innovations with nmx(run, time, age), selecting only those
	corresponding to the parameterized indexes corresponding to
	percentiles.
	
	Usage in LC:  self.e0s = lots_e0s(PTILE_INDS, self.nmx, lifeTableParams)
	'''
	if len(lots_nmx.shape) != 3:
		raise Exception("Bad nmx shape: %s" % lots_nmx.shape)
	lots_nmx = lots_nmx.copy()

	# compute all the e0s, sort on ending e0s, then return the appropriate percentiles
	stepsForward = lots_nmx.shape[1]
	numRuns = lots_nmx.shape[0]
	e0s = N.zeros([numRuns, stepsForward], N.float64)
	for i in range(0, e0s.shape[0]):	# Particular run
		for j in range(0, e0s.shape[1]): # For each projection step
			e0s[i,j] = LcUtil.lifeTable(lots_nmx[i,j,:], **lifeTableParams)
			pass
		pass

	if sortflag=='column-wise':
		e0s.sort(0)
	elif sortflag in (True, 'end-result'):
		sorti = N.argsort(e0s[:,-1])	# sort on e0 of end of run/ forecast
		e0s = e0s[sorti,:]
		pass
	else:
		pass

	if percentileIndices is None:
		return(e0s)
	else:
		return(e0s[percentileIndices,:])
	

def lcInfer(nmx,  lifeTableParams, ageCutoff=None, doFit=True, returnDict=False, normalizeMx=True, flattenBx=False, doTS=False):
	"""
	Does lc inference.

	nmx -- death rates, ageCutoffIndex -- index of highest age used from nmx
	"""

	## Make sure nmx well formed ...
	nmxZeros = (nmx == 0.0)
	nmxNegs = (nmx < 0.0)
	nmx[nmxNegs | nmxZeros] = .01
	goodRowsBool = ~N.isnan(nmx).any(axis=1)
	goodRowsNum  = N.where(goodRowsBool)[0].tolist() # weird numpy.where() return
	badEntries = N.isinf(nmx) | N.isnan(nmx)
	if badEntries.any():
		raise LcException, "Inf or NAN in nmx data in rows: %s.  nmx shape: %s.  \n\nnmx: %s" % \
			  (N.where(badEntries)[0], nmx.shape, nmx)
	
	# ...transform nmx...
	if ageCutoff is None:
		ageCutoffIndex = len(nmx)		# Use all of nmx
	else:
		ageCutoffIndex = LCFIT_AGE_INDICES[ageCutoff] + 1
	lnmx = N.log(nmx[:,0:ageCutoffIndex])					# logs of nmx
	infsLmx = N.isinf(lnmx)
	nansLmx = N.isnan(lnmx)
	assert not infsLmx.any(), 'Non-finite log(nmx). nmx: %s, lnmx: %s, infs: %s' %\
		   (nmx[infsLmx], lnmx[infsLmx], infsLmx) 
	ax = N.average(lnmx[goodRowsNum,:], axis=0)
	if normalizeMx:
		lnmx_adj = lnmx - ax # Adjusted lnmx; subtraction of ax applied to each row
	else:
		lnmx_adj = lnmx					# Non adjusted lnmx.

	# ...get LC parameters...
	try:
		(u, x, v) = N.linalg.svd(lnmx_adj[goodRowsNum,0:ageCutoffIndex], full_matrices=0)
		v = v.transpose()				# scipy does svd differently than R or Matlab
	except N.linalg.LinAlgError, e:
		raise N.linalg.LinAlgError, "e: %r\n   lnmx_adj: %r" % (e, N.around(lnmx_adj.tolist(), 2))

	# ... normalize bx, flatten if flattenBx is set to True ...
	bxNormalizer = (N.sign(N.sum(v[:,0]))) * (N.sum(N.absolute(v[:,0])))
	bx = v[:,0] / bxNormalizer
	if flattenBx:
		bx[bx<0.0] = 0.001

	# ... get kt and second-stage kt, backfilling with nans for empty years of data ...
	kt_unfit = x[0] * u[:,0] * N.sum(v[:,0]) 
	ktUnfitReturn = N.empty_like(nmx[:,0])
	ktUnfitReturn[goodRowsBool] = kt_unfit
	ktUnfitReturn[~goodRowsBool] = N.nan 
	if doFit:
		kt = fitMultiKt(ax, bx, copy.copy(kt_unfit), nmx[goodRowsNum,:], lifeTableParams)
		ktFitReturn = ktUnfitReturn.copy()
		ktFitReturn[goodRowsBool] = kt
		pass
	else:
		ktFitReturn = None
		pass

	# ... get RWD and AR models of kt and ktunfit ...
	def rw(_kt):
		""" Return RWD model parameters for _kt"""
		diffedKt = S.diff(_kt)
		drift = S.average(diffedKt)
		stdErrorDrift = N.sqrt(N.cov(_kt))/N.sqrt(len(_kt))
		stdErrorEq = S.sqrt(S.cov(diffedKt))
		stdErrorCoeff = stdErrorEq/S.sqrt(len(diffedKt))	# XXX should be len(self.kt)-1?

		# Calculate residuals
		innov_sans_err = N.zeros_like(_kt)
		for i in range(1, len(_kt)):
			innov_sans_err[i] = drift + _kt[i-1]
			pass
		e = _kt - innov_sans_err
		e0 = _kt - N.mean(_kt)
		Rsq = 1 - (N.cov(e)/N.cov(_kt))
		#Rsq = 1 - (N.sum(e**2))/(N.sum(e0**2))
		#exRatio = 1 - N.cov(_kt)/stdErrorEq
		exRatio = 1 - (N.sqrt(N.sum(N.diff(_kt)**2))/(len(_kt)-1))/N.cov(_kt)
		return dict(drift=drift, stdErrorEq=stdErrorEq, stdErrorCoeff=stdErrorCoeff, stdErrorDrift=stdErrorDrift,
					Rsq=Rsq,exRatio=exRatio)

	def ar1(_kt):
		""" Return AR(1) model parameters for _kt"""
		(c1, c0, r, two_tail_p, stderr_est) = ST.linregress(_kt[:-1],_kt[1:])

		# stderr stuff from article
		stdv_kt = N.sqrt(N.cov(_kt))	# numpy.var and numpy.std are biased, for some reason
		stdError_c0 = stdv_kt / N.sqrt(len(_kt))
		stdError_c1 = stdv_kt / N.sqrt(N.sum(_kt**2))
		
		# R^2 from non-variance AR(1)
		innov_sans_err = N.zeros(len(_kt))
		innov_sans_err[0] = _kt[0]
		for i in range(1, len(_kt)):
			innov_sans_err[i] = c0+c1*_kt[i-1]
		e = _kt - innov_sans_err
		e0 = _kt - N.mean(_kt)
		sdckt = N.sqrt(N.cov(e))
		sda0 = sdckt/N.sqrt(len(_kt))
		sda1 = sdckt/N.sqrt(N.sum(_kt**2))
		#Rsq = 1 - (N.sum(e**2))/(N.sum(e0**2))
		Rsq = 1 - (N.cov(e)/N.cov(_kt))	# need to use cov not var in order to get unbiased (N-1)
		exRatio = 1 - (stderr_est**2)/N.cov(_kt)
		exRatio = None
		
		# %prob of a1>1
		# z=(1-a1)/sda1;%t-score

		# return a named dict 
		return dict(Rsq=Rsq, _kt=_kt,
					c1=c1, c0=c0, sda0=sda0, sda1=sda1,
					resid=e, model_innov=innov_sans_err,
					stdError_c0=stdError_c0, stdError_c1=stdError_c1,
					stdckt=sdckt, stderr_est=stderr_est, stdv_kt=stdv_kt, exRatio=exRatio)

	# ... RWD ....
	ktunfit_rw = rw(kt_unfit)
	if doFit: kt_rw = rw(kt)
	else: kt_rw = None

	# ... AR(1) ...
	ktunfit_ar1 = ar1(kt_unfit)
	if doFit: kt_ar1 = ar1(kt)
	else: kt_ar1 = None
	
	# ... sanity asserts.
	assert (not doFit) | (abs(sum(kt_unfit)) < .001), \
		   LcException("doFit: %s, abs(sum(kt_unfit)): %s" % (doFit, abs(sum(kt_unfit))))
	
	if returnDict == True and doTS==True:
		return(dict(ax=ax, bx=bx, ktFit=ktFitReturn, ktUnfit=ktUnfitReturn,
					U=u, X=x, V=v, logMxAdj=lnmx_adj, logMx=lnmx,
					kt_rw=kt_rw, ktunfit_rw=ktunfit_rw, kt_ar1=kt_ar1, ktunfit_ar1=ktunfit_ar1))
	elif returnDict == True and doTS==False:
		return(dict(ax=ax, bx=bx, ktFit=ktFitReturn, ktUnfit=ktUnfitReturn,
					U=u, X=x, V=v, logMxAdj=lnmx_adj, logMx=lnmx))
	elif returnDict == False and doTS==True:
		return(ax, bx, ktFitReturn, ktUnfitReturn, u, x, v, lnmx_adj, lnmx,
			   kt_rw, ktunfit_rw, kt_ar1, ktunfit_ar1)
	elif returnDict == False and doTS==False:
		return(ax, bx, ktFitReturn, ktUnfitReturn, u, x, v, lnmx_adj, lnmx)
	else:
		pass
	raise Exception("Shouldn't be here!")


############################################################################################
### Single Population LC class
############################################################################################
class LcSinglePop(object):

	def __init__(self, start_year='XXX', notes='XXX', numberRuns='XXX', stepsForward='XXX',
				 ageCutoff=str(LCFIT_DEFAULT_AGE_CUTOFF), ltFuncType='ex',
				 beginFuncParam='0', endFuncParam='0', projConfidenceInterval='.95',
				 gender='combined',
				  **kwargs):
		'''Initialize LC instance.

		"rates" is being passed through the kwargs argument.'''

		## Return out if 'XXX', assuming we want an empty object
		if 'XXX' == start_year == notes == numberRuns == stepsForward:
			return

		## Parse basic paramenters
		self.ageCutoff = int(ageCutoff)
		self.ageCutoffIndex = LCFIT_AGE_INDICES[self.ageCutoff] + 1
		self.numRuns = int(numberRuns)
		self.stepsForward = int(stepsForward)
		self.gender = gender
		self.timestamp = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S') # Save time instantiated 

		# Bx flattening.  Weird because if checkbox isn't checked, it
		# doesn't get passed at all
		if kwargs.get(LCFIT_FLATTEN_BX_KEY) == 'on':
			self.flattenBx = True
		else:
			self.flattenBx = False

		## Figure out stuff for confidence interval with interval for graphing
		self.projConfidenceInterval = float(projConfidenceInterval)
		self.pval = 1 - self.projConfidenceInterval
		self.zscore = ST.norm.ppf(self.projConfidenceInterval + (self.pval/2))
		self.tilesTemp = N.array([0.0, self.pval/2, .5, 1.0 - (self.pval/2), 1.0])
		self.percentiles = (N.around(self.tilesTemp * 100, 2)).tolist()
		self.percentileIndices = (N.around(self.tilesTemp * (self.numRuns-1))).astype(N.int16) 

		## Parameters for LT functional
		""" DELETE ME XXX """
		self.ltFuncType = ltFuncType 
		if beginFuncParam == LCFIT_UNSELECTED_VALUE:
			self.beginFuncParam = 0
		else:
			self.beginFuncParam = float(beginFuncParam)
		if endFuncParam== LCFIT_UNSELECTED_VALUE:
			self.endFuncParam = 0
		else:
			self.endFuncParam = float(endFuncParam)

		# Create hash that will hold the (floating) parameters for the
		# lifetable function, which will be constant throughout this
		# object
		self.lifeTableParams = {
			'gender':self.gender,
			'ageCutoff':self.ageCutoff, 'ltFuncType':self.ltFuncType,
			'beginFuncParam':self.beginFuncParam, 'endFuncParam':self.endFuncParam, 
			'extensionMethod':LCFIT_DEFAULT_EXTENSION_METHOD} 
				
		# Start year
		if start_year == '':
			raise LcInputException, "Must enter a start year for Lc Object"
		self.start_year_text = start_year
		try:
			self.start_year = int(start_year)
		except (ValueError), e:
			raise LcInputException, "Bad value for start date.  Make sure using integer."

		# Notes
		if notes == '':
			raise LcInputException, "Must enter notes for Lc Object--describe the data at least"
		self.notes = notes				# Arbitrary notes from user 

		# Setup directory to store results and images. Uses md5 of
		# data and other stuff for directory identifier.  Overwrite
		# duplicate directory.
		self.LcID = md5.new(str(start_year) + str(notes) + self.timestamp).hexdigest()
		self.datapath =	os.path.join(LCFIT_DATADIR, self.LcID)
		try:
			os.mkdir(self.datapath)
		except OSError, (errno, strerr): #
			if errno == 17 :
				raise OSError, "Directory already exists: %s.  Error: %s, %s" \
					  % (self.datapath, errno, strerr)
			else: raise

		# Create dict to store image names and binary data
		self.imagesDict = {}

		# Parse, store, validate, etc the rates.  Lots of side effects
		self._dealWithRates(**kwargs) 
		
		# Do the inference.	 Note that there are side effects within instance.
		self._do_lc()

		# Build the graphics.  Note lots of side effects in directories.
		self._do_graphics()

		# Create a text dump of everything for later
		self._dumpText() 

		# All done--nothing really to do
		return


	def _dealWithRates(self, rates, **kwargs):
		"""Parses the rates.  Sets up datastructures for missing data."""
		# Save code version info with instance.  Here because I think
		# it is screwing up based on # some weird scoping thing in MF
		self.LcObjectINFO = LcObjectINFO
		
		assert type(rates) == types.StringType, \
			   AssertionError("Rates should be as string for input.  Instead: %s." % type(rates))

		# Get rates from text, extend ...
		self.rates_text = rates
		self.nmx = LcUtil.parseRates(self.rates_text) 

		# ... handle missing data: if there are nans after parsing,
		# determine which years (rows) they are in ...
		self.nmxNans = N.isnan(self.nmx)
		self.goodRowsBool = (~self.nmxNans).any(axis=1)
		self.goodRowsNum = N.where(self.goodRowsBool)[0].tolist() # weird numpy.where() return
		self.yearIndices = N.arange(1, self.nmx.shape[0]+1, dtype=N.int0) # XXX 1 indexed for missing data formulas

		# ... extend everything ...
		self.nmxExtended = LcUtil.emptyLikeWithNans(self.nmx)
		tmp = LcExtension.extendMx(self.nmx[self.goodRowsNum,:], ageCutoff=self.ageCutoff)
		assert self.nmxExtended[self.goodRowsNum,:].shape == tmp.shape,  \
			   AssertionError("orig shape: %s.  extended shape: %s" \
							  % (tmp.shape, self.nmxExtended[self.goodRowsNum,:].shape))
		self.nmxExtended[self.goodRowsNum,:] = tmp
		assert (self.nmxExtended[self.goodRowsNum,:] > 0.0).all() and (N.isfinite(self.nmxExtended[self.goodRowsNum,:])).all(), \
			   AssertionError("%s" % self.nmxExtended)
		
		# ... asserts, and hopefully fall of the end (only update object state).
		self.nmxInfs = N.isinf(self.nmx)
		assert not self.nmxInfs.any(), \
			   AssertionError("why are there infs in nmx???:\n %r" % N.round_(self.nmx, 2)) 
		return None 					
	
	def _do_lc(self):
		"""
		Do the inference and the simulation, saving the results as
		state in the instance.  Note that here we are doing the LC on
		non-missing values, then reassembling the results to keep the
		missing.
		"""

		# Do LC on the good data, fill self.* with good data only (ie ignore missing data for now).
		(self.ax, self.bx, self.kt, self.kt_unfit, self.U, self.X, self.V, self.lnmxAdjusted, self.lnmx ) = lcInfer(
			nmx=self.nmxExtended[self.goodRowsNum,:],
			lifeTableParams=self.lifeTableParams,
			ageCutoff=self.ageCutoff,
			flattenBx=self.flattenBx) 
		jumpoffAx = N.log(self.nmx[-1,0:self.ageCutoffIndex].ravel()) # Use last year of death rates to calcc
		
		## Derive current year stuff from LC inference results (kt etc),
		## put those results into the good year positions, let the nans in the non-good-years float.
		self.nmxsFromKtCurrent_unfit =  N.zeros_like(self.nmxExtended)
		self.nmxsFromKtCurrent_unfit[...] = N.nan
		self.nmxsFromKtCurrent_unfit[self.goodRowsNum,:] =  project_nmx(kt=self.kt_unfit, bx=self.bx, ax=self.ax, ageCutoff=self.ageCutoff)

		self.nmxsFromKtCurrent = N.zeros_like(self.nmxExtended) # T x X
		self.nmxsFromKtCurrent[...] = N.nan
		self.nmxsFromKtCurrent[self.goodRowsNum,:] = project_nmx(kt=self.kt, bx=self.bx, ax=self.ax, ageCutoff=self.ageCutoff) 

		self.e0sFromKtCurrent = N.zeros(self.nmxExtended.shape[0])
		self.e0sFromKtCurrent[...] = N.nan
		self.e0sFromKtCurrent[self.goodRowsNum] = N.array(
			[LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams) for nmxRow in self.nmxsFromKtCurrent[self.goodRowsNum,:]])
		
		self.e0sFromKtCurrent_unfit = N.zeros(self.nmxExtended.shape[0])
		self.e0sFromKtCurrent_unfit[...] = N.nan
		self.e0sFromKtCurrent_unfit[self.goodRowsNum] = N.array(
			[LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams) for nmxRow in self.nmxsFromKtCurrent_unfit[self.goodRowsNum,:]])

		self.e0sFromEmpiricalNmx = N.zeros(self.nmxExtended.shape[0]) # T x 1
		self.e0sFromEmpiricalNmx[...] = N.nan
		self.e0sFromEmpiricalNmx[self.goodRowsNum]  = N.array(
			[LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams) for nmxRow in self.nmxExtended[self.goodRowsNum,:]])

		######## Forecast ##############
		## Get random walk parameters
		if self.goodRowsBool.all():
			# Data for all years.
			self.diffedKt = S.diff(self.kt)
			self.drift = S.average(self.diffedKt)
			self.stdErrorEq = S.std(self.diffedKt)
			self.stdErrorCoeff = self.stdErrorEq/S.sqrt(len(self.diffedKt))	# XXX should be len(self.kt)?
			pass
		else:
			# Missing data (li, Lee, Tulja2002).  Find drift from the
			# endpoints, find the standard errors from some fancy
			# stuff (using xTmp and yTmp to make the math readable
			# below).
			self.drift = (self.kt[-1] - self.kt[0])/float(len(self.yearIndices))
			xTmp = N.sum(N.square(N.diff(self.kt) - (self.drift * N.diff(self.yearIndices[self.goodRowsNum]))))
			yTmp = N.sum(N.square(N.diff(self.yearIndices[self.goodRowsNum]))) / (self.yearIndices[-1]-self.yearIndices[0])
			assert xTmp > 0.001, "xTmp < 0.001: %s." % xTmp
			assert yTmp < (self.yearIndices[-1] - self.yearIndices[0]), "yTmp < total years: yTmp: %s." % yTmp
			self.stdErrorEqSq = xTmp/(self.yearIndices[-1] - self.yearIndices[0] - yTmp)
			self.stdErrorCoeffSq = self.stdErrorEqSq/(self.yearIndices[-1]-self.yearIndices[0])
			self.stdErrorEq = N.sqrt(self.stdErrorEqSq)
			self.stdErrorCoeff = N.sqrt(self.stdErrorCoeffSq)
			pass
					
		## Simulation with above paramenters  XXX how do we handle starting kt?
		self.kt_simul = sim_kt(SEC=self.stdErrorCoeff, SEE=self.stdErrorEq, drift=self.drift, numRuns=self.numRuns, stepsForward=self.stepsForward, sortflag=False)
		self.nmx_projected = project_nmx(kt=self.kt_simul, bx=self.bx, ax=jumpoffAx, ageCutoff=self.ageCutoff)
		self.nmx_projected_stochastic_median_final = project_nmx(kt=N.median(N.sort(self.kt_simul,0)), bx=self.bx, ax=jumpoffAx, ageCutoff=self.ageCutoff)
		self.e0s_projected = lots_e0s(self.percentileIndices, self.nmx_projected, self.lifeTableParams)

		######### Other Forecasting ######
		## Derive analytic mean and 95% forecast interval of kt
		x = S.arange(0.0, float(self.stepsForward+1))
		self.KtStdError = ((x*(self.stdErrorEq**2.0)) +
						   (x*self.stdErrorCoeff)**2.0)**.5  # kt.stderr <- ( (x*see^2) + (x*sec)^2 )^.5
		tArray = N.array([self.drift] * (self.stepsForward+1))
		tArray[0] = 0.0
		self.meanKtProjected = N.cumsum(tArray)
		self.upperKtProjected = self.meanKtProjected + (self.zscore * self.KtStdError)
		self.lowerKtProjected = self.meanKtProjected - (self.zscore * self.KtStdError)

		## Derive the projected e0s -- note that "upper" and "lower" reversed wrt kt
		self.upperE0Projected = LcUtil.multiKt2e0(self.lowerKtProjected, ax=jumpoffAx, bx=self.bx,
												  lifeTableParams=self.lifeTableParams)
		self.lowerE0Projected = LcUtil.multiKt2e0(self.upperKtProjected, ax=jumpoffAx, bx=self.bx,
												  lifeTableParams=self.lifeTableParams)
		self.medianE0Projected =  LcUtil.multiKt2e0(self.meanKtProjected, ax=jumpoffAx, bx=self.bx,
												  lifeTableParams=self.lifeTableParams)
		self.nmx_projectedMedian = project_nmx(kt=self.meanKtProjected, bx=self.bx, ax=jumpoffAx,
											   ageCutoff=self.ageCutoff)
		self.nmx_projectedMedianFinal = self.nmx_projectedMedian[-1,:]
		return							# Don't return anything useful

	def _do_graphics(self, numAgeWidths=LCFIT_DEFAULT_NO_AGEWIDTHS,
					 lcImageName=LC_IMAGE_NAME,
					 fcImageName=FC_IMAGE_NAME,
					 lnmxImageName=LNMX_IMAGE_NAME,
					 mortProfileImageName=MORTP_IMAGE_NAME):

		##### Font etc constants
		FONTSIZE='xx-small'
		FONT  = {'fontname'   : 'Courier',
				 'color'      : 'k',
				 'fontweight' : 'bold',
				 'fontsize'   : 'xx-small'}
		fp = MPL.font_manager.FontProperties(size=FONTSIZE)
		
		##### Set up overall graphics stuff ################
		ages = LCFIT_AGES
		years_end = self.start_year + self.nmx.shape[0]
		self.years = N.array(range(self.start_year, years_end)) 
		years_fcst = N.array(range(years_end-1, years_end + self.stepsForward)) 
		yearsPadding = int((self.years[-1] - self.years[0])*.30) + 1
		
		# ... if working with missing data, fix up empirical kt, kt_unfit, and e0 ...
		self.kt_graph = N.zeros(self.years.shape[0])
		self.kt_graph[...] = N.nan
		self.kt_unfit_graph = N.zeros(self.years.shape[0])
		self.kt_unfit_graph[...] = N.nan
		self.e0s_emp_graph = N.zeros(self.years.shape[0])
		self.e0s_emp_graph[...] = N.nan
		self.e0s_kt_graph = N.zeros(self.years.shape[0])
		self.e0s_kt_graph[...] = N.nan
		self.e0s_kt_unfit_graph = N.zeros(self.years.shape[0])
		self.e0s_kt_unfit_graph[...] = N.nan
		if self.goodRowsBool.all():
			self.kt_graph[...] = self.kt
			self.kt_unfit_graph[...] = self.kt_unfit
			self.e0s_emp_graph[...] = self.e0sFromEmpiricalNmx
			self.e0s_kt_graph[...] = self.e0sFromKtCurrent
			self.e0s_kt_unfit_graph[...] = self.e0sFromKtCurrent_unfit
		else:
			#raise pprint.pformat((type(self.kt_graph), type(self.kt)))
			self.kt_graph[self.goodRowsBool] = self.kt 
			self.kt_unfit_graph[self.goodRowsBool] = self.kt_unfit 
			self.e0s_kt_graph[...] = self.e0sFromKtCurrent
			self.e0s_kt_unfit_graph[...] = self.e0sFromKtCurrent_unfit
			self.e0s_emp_graph[...] = self.e0sFromEmpiricalNmx
			pass		
		
		##### LC Inference Graphic #########################
		# Set up sublot stuff ...
		fig = PL.figure(1)
		fig.clf()
		fig.subplots_adjust(left=0.125, right=0.9, bottom=0.1, top=0.9, wspace=0.2, hspace=1.0)

		# ...do subplot -- kt ...
		PL.subplot(4,1,1)
		PL.grid(True)
		PL.plot(self.years, self.kt_graph, ls='steps', color='b', linewidth=1.5, label='kt 2nd Stage')
		PL.plot(self.years, self.kt_unfit_graph, ls='-', color='r', linewidth=.3, label='kt SVD')
		PL.xlabel('year')
		PL.title('kt')
		PL.legend(loc='best', numpoints=4, prop=fp, pad=.1)
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE)
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((self.years[0], xticks[2:-2], self.years[-1]))
		xticks.sort()
		PL.xlim(xmin=self.years[0]-5, xmax=self.years[-1]+yearsPadding)
		(xticks, xlabels) = PL.xticks(xticks, fontsize=FONTSIZE)
		
		# ...subplot -- life exp ...
		PL.subplot(4,1,2)
		PL.grid(True)
		PL.plot(self.years, self.e0s_emp_graph, color='b', ls='steps', lw=1.5,
				label='empirical e_0')
		PL.plot(self.years, self.e0s_kt_unfit_graph, color='r', ls='-', lw=0.5,
				label='kt(SVD) e_0' )
		PL.title('E_0')
		PL.legend(loc='best', prop=fp, pad=.1)
		PL.xlabel('year')
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE) 
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((self.years[0], xticks[2:-2], self.years[-1]))
		xticks.sort() 
		PL.xticks(xticks, fontsize=FONTSIZE)
		PL.xlim(xmin=self.years[0]-5, xmax=self.years[-1]+yearsPadding)

		# ...subplot -- bx ...
		PL.subplot(4,1,3) 
		PL.plot(ages[:self.ageCutoffIndex], self.bx, 'x-k')
		PL.xlabel('age')
		PL.title('bx')
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE)
		PL.xticks(fontsize=FONTSIZE)

		# ...subplot -- ax ...
		PL.subplot(4,1,4)
		PL.plot(ages[:self.ageCutoffIndex], self.ax, 'x-k')
		PL.xlabel('age')
		PL.title('ax')
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE)
		PL.xticks(fontsize=FONTSIZE)

		# ...save it and open it and store the binary.
		filename = os.path.join(self.datapath, lcImageName) 
		PL.savefig(filename, dpi=150)
		PL.close(1)
		f = open(filename)
		self.imagesDict[lcImageName] = f.read(-1)
		f.close()
		os.unlink(filename)

		##### Forecast kt's and e0's ######################
		fig = PL.figure(2)
		fig.clf()
		assert type(self.percentiles) == types.ListType, LcException("Percentiles: %s" % self.percentiles)
		
		# ...plot all forecast kt's on top of each other ...
		PL.subplot(2,1,1)
		PL.grid(True)
		for i in range(0, self.numRuns):
			PL.plot(years_fcst, self.kt_simul[i,:], 'k', linewidth=.25, label='_nolegend_') 
		PL.plot(years_fcst, self.lowerKtProjected, 'b--', linewidth=2.5,
				label='low kt: %3.1f%%' % self.percentiles[1]) # XXX Magic number
		PL.plot(years_fcst, self.meanKtProjected, 'k--', linewidth=2.5,
				label='mean kt: %3.1f%%' % self.percentiles[2]) # XXX Magic number 
		PL.plot(years_fcst, self.upperKtProjected, 'b--', linewidth=2.5,
				label='high kt: %3.1f%%' % self.percentiles[3]) # XXX Magic number
		PL.title('kt projections')
		PL.legend(prop=fp)
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((years_fcst[0], xticks[2:-2], years_fcst[-1]))
		xticks.sort()
		PL.xticks(xticks)

		# ...plot all forecast e0's on top of each other ...
		PL.subplot(2,1,2)
		PL.grid(True)
		PL.plot(years_fcst, self.lowerE0Projected, 'b--', linewidth=2.5,
				label='mean e0: %3.1f%%' % self.percentiles[1]) # XXX Magic numbe) 
		PL.plot(years_fcst, self.medianE0Projected, 'k--', linewidth=2.5,
				label='mean e0: %3.1f%%' % self.percentiles[2]) # XXX Magic number
		PL.plot(years_fcst, self.upperE0Projected, 'b--', linewidth=2.5,
				label='mean e0: %3.1f%%' % self.percentiles[3]) # XXX Magic number
		for i in range(0, self.e0s_projected.shape[0]):
			PL.plot(years_fcst, self.e0s_projected[i, :], 'k', linewidth=.5, label='_nolegend_')
		PL.title('%s projections' % self.lifeTableParams['ltFuncType'])
		PL.legend(prop=fp)
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((years_fcst[0], xticks[2:-2], years_fcst[-1]))
		xticks.sort()
		PL.xticks(xticks)

		# ...save the file.
		filename = os.path.join(self.datapath, fcImageName) 
		PL.savefig(filename, dpi=150)
		PL.close(2)
		f = open(filename)
		self.imagesDict[fcImageName] = f.read(-1)
		f.close()
		os.unlink(filename)
		
		##### Empirical + kt log nmx's  ######################
		# Plot them... 
		fig = PL.figure(3)
		fig.clf()
		PL.grid(True)
		nmx_tmp = copy.copy(self.nmx)
		nmx_kt_tmp = copy.copy(self.nmxsFromKtCurrent)
		colors = 'bgrcmrcm'
		clen = len(colors)
		for i, age in enumerate(LCFIT_LOGNMX_GRAPHIC_AGES): 
			try:
				pl, = PL.semilogy(self.years, nmx_tmp[:, LCFIT_AGE_INDICES[age]],
								  color=colors[i%clen], ls='steps', linewidth=1.5, label='Age: %i' % age)
				pl, = PL.semilogy(self.years, nmx_kt_tmp[:, LCFIT_AGE_INDICES[age]],
								  'k:', linewidth=.5, label='_nolegend_')
				PL.text(self.years[-1],  nmx_tmp[:, LCFIT_AGE_INDICES[age]][-1], ' %s ' % age,  fontsize=8)
				pl.set_dashes([4,2])
			except IndexError, e:
				raise IndexError, "error: %s. size self.lnmx: %s.  age: %s, age index: %s." % \
					  (e, self.nmx.shape, age, LCFIT_AGE_INDICES[age])
			pass
		PL.title('Within sample log nmx,\n(dashed=LC, full=empirical)')
		PL.legend(prop=fp, loc='best')
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((self.years[0], xticks[1:-1], self.years[-1] + abs(xticks[0]-xticks[2])))
		xticks.sort()
		PL.xticks(xticks)

		# ...save the file.
		filename = os.path.join(self.datapath, lnmxImageName) 		
		PL.savefig(filename, dpi=150)
		PL.close(3)
		f = open(filename)
		self.imagesDict[lnmxImageName] = f.read(-1)
		f.close()
		os.unlink(filename)
		
        ##### Three mortality profiles:  begin and end of data, end of projection  ######################
		# Plot them... 
		fig=PL.figure(4)
		fig.clf()
		PL.grid(True)
		PL.title('Log Mortality Profiles: begin, end, projected.')
		
		pl, = PL.semilogy(LCFIT_AGES, self.nmxExtended[0,:], 'b-', linewidth=.5, label='Yr: %i Emp. CG' % self.start_year)
		pl, = PL.semilogy(LCFIT_AGES, self.nmx[0,:], 'b--', linewidth=.5, label='_nolegend_')
		pl.set_dashes([4,2])
		pl, = PL.semilogy(LCFIT_AGES, self.nmxExtended[-1,:], 'r-', linewidth=.5, label='Yr: %i Emp. CG' % (years_end-1)) 
		pl, = PL.semilogy(LCFIT_AGES, self.nmx[-1,:], 'r--', linewidth=.5, label='_nolegend_') 
		pl.set_dashes([4,2])
		pl, = PL.semilogy(LCFIT_AGES, self.nmx_projectedMedian[-1,:], 'g', linewidth=.5,
						  label='Yr: %i Proj' % (years_end + len(self.nmx_projectedMedian[:,0])-2)) 
		PL.legend(prop=fp, loc='best')
		PL.xlabel('age')

		# ... delete all the locals for empty graphs ..
		#del kt_graph, kt_unfit_graph, e0s_emp_graph, e0s_kt_graph, e0s_kt_unfit_graph
		
		# ...save the file.
		filename = os.path.join(self.datapath, mortProfileImageName) 
		PL.savefig(filename, dpi=150)
		PL.close(3)
		f = open(filename)
		self.imagesDict[mortProfileImageName] = f.read(-1)
		f.close()
		os.unlink(filename)

		# Delete the directory in which we store temp results for the images
		os.rmdir(self.datapath)

	def __str__(self):
		"""Return a string that gives the content of the LC object"""
		
		assert type(self.percentiles) == types.ListType, LcException("Percentiles: %s" % self.percentiles)

		ltFuncType = self.lifeTableParams['ltFuncType']

		# Info about the run/software/user/etc ...
		run_info = '<pre>RUN INFORMATION:\t\n'
		run_info += 'Current time:\t %s\n' % datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		run_info += 'Run time:\t %s\n' % self.timestamp 
		run_info += 'Software Id:\t %s\n' % self.LcObjectINFO
		run_info += 'Object ID:\t %s\n' % self.LcID
		run_info += '\nNotes:\t %s\n' % self.notes

		
		# ...display the scalar values of interetest ...
		run_info += '\n'
		run_info += 'First year of empirical data:\t %s\n' % self.start_year
		year_end = (self.start_year + self.nmx.shape[0] - 1)
		run_info += 'End year of empirical data:\t%s\n' % year_end
		run_info += 'Cutoff age for age nmx extension:\t %s\n' % self.ageCutoff
		run_info += 'Lifetable age regime:\t 0-1, 1-4, 5-9, ..., 105-110, 110+\n'
		run_info += 'Projection confidence interval:\t%s\n' % self.projConfidenceInterval
		run_info +=	'Percentile values for display:\t %s\n' % self.percentiles
		run_info += 'Drift:\t %s\n' % self.drift
		run_info += 'Drift uncertainty:\t %s\n' % self.stdErrorCoeff
		run_info += 'Standard error of innovations:\t %s\n'  % self.stdErrorEq 
		run_info += 'Number of projection runs:\t %s\n' % self.numRuns
		run_info += 'Number of years projected forward:\t %s\n' % self.stepsForward
		run_info += 'Width of projection step:\t %s year(s)\n' % LCFIT_PROJECTION_WIDTH
		run_info += 'Width of projection step:\t %s year(s)\n' % LCFIT_PROJECTION_WIDTH

		# ... close <pre>...
		run_info += '</pre>'

		# ... include a link to the text dump of the object...
		dumpLink = LCFIT_WWW_OBJECT_DUMP + '?LC_OBJECT_ID=' + str(self.LcID)
		run_info += "<p><form action='%s'> <button name='LC_OBJECT_ID' value='%s'> Object Dump </button></form></p>" % \
					(dumpLink,str(self.LcID))

		# ... close run info.
		run_info += ''

		# Empirical data by year
		yearlyDataList =  [self.years, self.kt_graph, self.kt_unfit_graph, self.e0s_emp_graph,
						   self.e0s_kt_unfit_graph]
		yearlyHeadings = ['Year', 'kt, after second stage', 'kt, from SVD',
						  '%s, from second stage kt' % ltFuncType,
						  '%s, from empirical nmx' % ltFuncType ]
		yearlyResultsTable = LcUtil.tablefy(dataList = yearlyDataList, headings=yearlyHeadings)

		# Empirical data by age
		ageDataList = [LCFIT_AGES[:self.ageCutoffIndex], self.ax, self.bx]
		ageHeadings = ['age', 'ax', 'bx']
		ageResultsTable = LcUtil.tablefy(dataList = ageDataList, headings=ageHeadings)

		# Projected data by year
		projectedYears = range(self.start_year + len(self.kt_graph) - 1,
							   self.start_year + len(self.kt_graph) + self.stepsForward)
		projDataList = [projectedYears, self.lowerE0Projected, self.medianE0Projected,
						self.upperE0Projected, self.e0s_projected[2, :]]
		projHeadings = ['Year (projected)',
						'low analytical %s' % ltFuncType,
						'median analytical %s' % ltFuncType,
						'high analytical %s'  % ltFuncType,
						'median proj %s' % ltFuncType]
		projResultsTable =  LcUtil.tablefy(dataList = projDataList, headings=projHeadings)

		# image summarizing inference
		lc_img_path = LCFIT_WWW_DISPLAY_IMAGE + '?' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + LC_IMAGE_NAME
		lc_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of LC Summary %s"></a>\n' \
				   % (lc_img_path, lc_img_path, IMGH, IMGW, self.LcID)

		# image tracing log rates 
		lnmx_img_path = LCFIT_WWW_DISPLAY_IMAGE + '?' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + LNMX_IMAGE_NAME
		lnmx_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of selected LNMXes %s"></a>\n' \
				   % (lnmx_img_path, lnmx_img_path, IMGH, IMGW, self.LcID)

		# image summarizing forecast
		fc_img_path = LCFIT_WWW_DISPLAY_IMAGE + '?' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + FC_IMAGE_NAME
		fc_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of LC Summary %s"></a>\n' \
				   % (fc_img_path, fc_img_path, IMGH, IMGW, self.LcID)

		# image w/ three mortality profiles
		mortp_img_path = LCFIT_WWW_DISPLAY_IMAGE + '?' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + MORTP_IMAGE_NAME
		mortp_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of Mort Profiles %s"></a>\n' \
				   % (mortp_img_path, mortp_img_path, IMGH, IMGW, self.LcID)

		# Build html string (rather rudimentary, sorry)
		HTMLstr = '<table  border="1">\n' + \
				  '<tr><td colspan=3> <h3>LCFIT Run</h3></td>\n' + \
				  '<tr><td colspan=3>' + run_info + '</td></tr>\n' + \
				  '<tr><td colspan=3>' + lc_image + fc_image + lnmx_image + mortp_image + '</td></tr>\n' + \
				  '<tr><td colspan=3>' + yearlyResultsTable + '</td></tr>\n' + \
				  '<tr><td colspan=3>' + ageResultsTable + '</td></tr>\n' + \
				  '<tr><td colspan=3>' + projResultsTable + '</td></tr>\n' + \
				  '<tr><td colspan=3> Please direct questions or comments to: %s </td>\n' % EMAIL + \
				 '</table>\n'
		return HTMLstr


	def _dumpText(self):
		self.dumpString = LcUtil.dumpObject(self,
											helpParagraph=LCFIT_DUMP_HELP,
											dontDump=LCFIT_NOTWANTED_ATTRIBUTE_DUMPS,
											annoStructure=LCFIT_VAR_ANNOTATION_SINGLESEX,
											fieldsep=LCFIT_FIELDSEP,
											rowsep=LCFIT_ROWSEP,
											stanzasep=LCFIT_STANZASEP)

	def __getattr__(self, name):
		''' Unspecified attributes get a string return

		XXX unfortunately this works to hide useful backtraces when
		you forget to initialize the class properly and use self.x
		from within it.    

		'''
		if LcHardErrors:
			raise AttributeError('No such att: %s' % name)
		else:
			if re.match('^[a-zA-Z].*', name): 
				return 'ERROR:  NO SUCH ATTRIBUTE: %s' % name
			else:
				raise AttributeError


	def __repr__(self):
		"""Return a string that would work for a listing of these objects"""
		return "<Lee-Carter inference object>" 


	def show_html(self):
		return str(self)


		
###################################

if __name__ == '__main__':
	print "hello from LcSinglePopObject.py"
