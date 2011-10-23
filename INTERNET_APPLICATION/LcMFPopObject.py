#!/usb/bin/python
"""
This module provides the home for LcMFPopObject, which takes three
sets of rates in the form of text: combined, female, and male.  It
derives kt and bx from the combined rates, and female and male ax from
the separated rates.  For the forecast, uses these special ax'es as
jump off for two separate simulations, with parameters derived from
combined kt and bx.

This module imports LcSinglePopObject.py to get constants applicable
to the LC inference and projection process, as well.  It uses the
module functions from LcSinglePopObject as well.
 
"""


## Imports ################################################
from LcLog import lcfitlogger
from LcConfig import * 					# THis imports numpy and friends
from LcSinglePopObject import *
import LcUtil
from LcUtil import Diagnose as D
sys.path.append('./TESTING')			# For test data

## Module Variables  ###### 
LcObjectINFO ='LcMFPopObject'


###################################################################################
class LcMFPop(LcSinglePop):
	
	def _dealWithRates(self, combinedRates, femaleRates, maleRates, **kwargs):
		""" blah """

		# Save code version info with instance.  Here because I think
		# it is screwing up based on # some weird scoping thing in MF
		self.LcObjectINFO = LcObjectINFO
		#raise(self.LcObjectINFO)

		# Combined Rates
		self.rates_textComb = combinedRates
		self.nmxComb = LcUtil.parseRates(self.rates_textComb)
		infs_or_nans = N.isinf(self.nmxComb) | N.isnan(self.nmxComb)
		assert not infs_or_nans.any(), \
			   AssertionError("why are there infs or nans in combined_nmx???:\n %r" \
							  % N.round_(self.nmxComb, 2)) 
		# F Rates
		self.rates_textFem = femaleRates
		self.nmxFem = LcUtil.parseRates(self.rates_textFem)
		infs_or_nans = N.isinf(self.nmxFem) | N.isnan(self.nmxFem)
		assert not infs_or_nans.any(), \
			   AssertionError("why are there infs or nans in female_nmx???:\n %r" \
							  % N.round_(self.nmxFem, 2)) 
		# M Rates
		self.rates_textMale = maleRates
		self.nmxMale = LcUtil.parseRates(self.rates_textMale)
		infs_or_nans = N.isinf(self.nmxMale) | N.isnan(self.nmxMale)
		assert not infs_or_nans.any(), \
			   AssertionError("why are there infs or nans in nmxMale???:\n %r" \
							  % N.round_(self.nmxMale, 2)) 
		
	
	def _do_lc(self):
		"""
		Do the inference and the simulation, saving the results as
		state in the instance.
		"""
		########## LC step #######
		## Basic LC step, combined.  Store all the results in the instance.
		(self.axComb, self.bxComb, self.ktComb, self.kt_unfitComb,
		 self.UComb, self.XComb, self.VComb, self.lnmxAdjustedComb, self.lnmxComb) = lcInfer(
			self.nmxComb, ageCutoff=self.ageCutoff, lifeTableParams=self.lifeTableParams, flattenBx=self.flattenBx) 

		## Basic LC step, combined.  Store all the results in the instance.
		(self.axFem, self.bxFem, self.ktFem, self.kt_unfitFem,
		 self.UFem, self.XFem, self.VFem, self.lnmxAdjustedFem, self.lnmxFem) = lcInfer(
			self.nmxFem, ageCutoff=self.ageCutoff, lifeTableParams=self.lifeTableParams, flattenBx=self.flattenBx) 
		
		## Basic LC step, combined.  Store all the results in the instance.
		(self.axMale, self.bxMale, self.ktMale, self.kt_unfitMale,
		 self.UMale, self.XMale, self.VMale, self.lnmxAdjustedMale, self.lnmxMale) = lcInfer(
			self.nmxMale, ageCutoff=self.ageCutoff, lifeTableParams=self.lifeTableParams, flattenBx=self.flattenBx) 
			
		jumpoffAxFem = N.log(self.nmxFem[-1,0:self.ageCutoffIndex].ravel())
		jumpoffAxMale = N.log(self.nmxMale[-1,0:self.ageCutoffIndex].ravel())

		## Derive current year stuff from LC inference results (kt etc).
		## Note use of list comprehensions.
		self.e0sFromEmpiricalNmxComb = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
												for nmxRow in self.nmxComb])
		self.e0sFromEmpiricalNmxMale = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
												for nmxRow in self.nmxMale])
		self.e0sFromEmpiricalNmxFem = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
												for nmxRow in self.nmxFem])
		self.nmxsFromKtCurrentComb = project_nmx(kt=self.ktComb, bx=self.bxComb, ax=self.axComb,
											 ageCutoff=self.ageCutoff)
		self.nmxsFromKtCurrentMale = project_nmx(kt=self.ktComb, bx=self.bxComb, ax=self.axMale,
											 ageCutoff=self.ageCutoff)
		self.nmxsFromKtCurrentFem = project_nmx(kt=self.ktComb, bx=self.bxComb, ax=self.axFem,
											 ageCutoff=self.ageCutoff)
		self.nmxsFromKtCurrent_unfitComb = project_nmx(kt=self.kt_unfitComb, bx=self.bxComb, ax=self.axComb,
												   ageCutoff=self.ageCutoff) 
		self.nmxsFromKtCurrent_unfitMale = project_nmx(kt=self.kt_unfitComb, bx=self.bxComb, ax=self.axMale,
												   ageCutoff=self.ageCutoff) 
		self.nmxsFromKtCurrent_unfitFem = project_nmx(kt=self.kt_unfitComb, bx=self.bxComb, ax=self.axFem,
												   ageCutoff=self.ageCutoff) 
		self.e0sFromKtCurrentComb = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
										 for nmxRow in self.nmxsFromKtCurrentComb])
		self.e0sFromKtCurrentMale = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
										 for nmxRow in self.nmxsFromKtCurrentMale])
		self.e0sFromKtCurrentFem = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
										 for nmxRow in self.nmxsFromKtCurrentFem])
		self.e0sFromKtCurrent_unfitComb = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
										 for nmxRow in self.nmxsFromKtCurrent_unfitComb])
		self.e0sFromKtCurrent_unfitMale = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
										 for nmxRow in self.nmxsFromKtCurrent_unfitMale])
		self.e0sFromKtCurrent_unfitFem = N.array([LcUtil.lifeTable(nmxp=nmxRow, **self.lifeTableParams)
										 for nmxRow in self.nmxsFromKtCurrent_unfitFem])
		assert len(self.e0sFromKtCurrentComb) >= 1, \
			   AssertionError("self.e0sFromKtCurrentComb: %s" % self.e0sFromKtCurrentComb)
		assert type(self.e0sFromKtCurrentComb) == N.ndarray, \
			   AssertionError("Weird type: %s" % type(self.e0sFromKtCurrentComb))

		######## Simulation ##############
		## Get random walk parameters
		self.diffedKt = S.diff(self.ktComb)
		self.drift = S.average(self.diffedKt)
		self.stdErrorEq = S.std(self.diffedKt)
		self.stdErrorCoeff = self.stdErrorEq/S.sqrt(len(self.diffedKt))
		
		## Multi run simulation with above paramenters
		self.kt_simul = sim_kt(SEC=self.stdErrorCoeff, SEE=self.stdErrorEq, drift=self.drift,
							   numRuns=self.numRuns, stepsForward=self.stepsForward, sortflag=False)
		self.nmx_projectedFem = project_nmx(kt=self.kt_simul, bx=self.bxComb, ax=jumpoffAxFem,
										 ageCutoff=self.ageCutoff)
		self.nmx_projectedMale = project_nmx(kt=self.kt_simul, bx=self.bxComb, ax=jumpoffAxMale,
										 ageCutoff=self.ageCutoff)
		self.nmx_projected_stochastic_median_final_F = project_nmx(kt=N.median(N.sort(self.kt_simul,0)),
																   bx=self.bxComb, ax=jumpoffAxFem, ageCutoff=self.ageCutoff)
		self.nmx_projected_stochastic_median_final_M = project_nmx(kt=N.median(N.sort(self.kt_simul,0)),
																   bx=self.bxComb, ax=jumpoffAxMale, ageCutoff=self.ageCutoff)

		self.e0s_projectedFem = lots_e0s(self.percentileIndices, self.nmx_projectedFem, self.lifeTableParams)
		self.e0s_projectedMale = lots_e0s(self.percentileIndices, self.nmx_projectedMale, self.lifeTableParams)
		
		## Derive analytic mean and x% forecast interval of kt
		x = S.arange(0.0, float(self.stepsForward+1))
		self.KtStdError = ((x*(self.stdErrorEq**2.0)) +
						   (x*self.stdErrorCoeff)**2.0)**.5  # kt.stderr <- ( (x*see^2) + (x*sec)^2 )^.5
		tArray = N.array([self.drift] * (self.stepsForward+1))
		tArray[0] = 0.0
		self.meanKtProjected = N.cumsum(tArray)
		self.upperKtProjected = self.meanKtProjected + (self.zscore * self.KtStdError)
		self.lowerKtProjected = self.meanKtProjected - (self.zscore * self.KtStdError)

		self.nmx_projectedMedian_F = project_nmx(kt=self.meanKtProjected, bx=self.bxComb, ax=jumpoffAxFem,
												 ageCutoff=self.ageCutoff)
		self.nmx_projectedMedian_M = project_nmx(kt=self.meanKtProjected, bx=self.bxComb, ax=jumpoffAxMale,
												 ageCutoff=self.ageCutoff)
		self.nmx_projected_median_final_F = self.nmx_projectedMedian_F[-1,:]
		self.nmx_projected_median_final_M = self.nmx_projectedMedian_M[-1,:]

		
		## Derive the projected e0s, F
		self.upperE0ProjectedFem = LcUtil.multiKt2e0(self.upperKtProjected, ax=jumpoffAxFem, bx=self.bxComb,
												  lifeTableParams=self.lifeTableParams)
		self.lowerE0ProjectedFem = LcUtil.multiKt2e0(self.lowerKtProjected, ax=jumpoffAxFem, bx=self.bxComb,
												  lifeTableParams=self.lifeTableParams)
		self.meanE0ProjectedFem =  LcUtil.multiKt2e0(self.meanKtProjected, ax=jumpoffAxFem, bx=self.bxComb,
												  lifeTableParams=self.lifeTableParams)
		## Derive the projected e0s, M
		self.upperE0ProjectedMale = LcUtil.multiKt2e0(self.upperKtProjected, ax=jumpoffAxMale, bx=self.bxComb,
												  lifeTableParams=self.lifeTableParams)
		self.lowerE0ProjectedMale = LcUtil.multiKt2e0(self.lowerKtProjected, ax=jumpoffAxMale, bx=self.bxComb,
												  lifeTableParams=self.lifeTableParams)
		self.meanE0ProjectedMale =  LcUtil.multiKt2e0(self.meanKtProjected, ax=jumpoffAxMale, bx=self.bxComb,
												  lifeTableParams=self.lifeTableParams)
		
		return							# Don't return anything useful


	def _do_graphics(self, numAgeWidths=LCFIT_DEFAULT_NO_AGEWIDTHS,
					 lcImageName=LC_IMAGE_NAME, fcImageName=FC_IMAGE_NAME,
					 lnmxImageName=LNMX_IMAGE_NAME):

		##### Font etc constants
		FONTSIZE='xx-small'
		FONT  = {'fontname'   : 'Courier',
				 'color'      : 'k',
				 'fontweight' : 'bold',
				 'fontsize'   : 'xx-small'}
		fp = MPL.font_manager.FontProperties(size=FONTSIZE)
		
		##### Set up overall graphics stuff ################
		ages = LCFIT_AGES
		years_end = self.start_year + self.nmxComb.shape[0]
		years = N.array(range(self.start_year, years_end)) 
		assert len(years) >= 1, AssertionError("years: %s" % years)
		years_fcst = N.array(range(years_end-1, years_end + self.stepsForward)) 

		##### LC Inference Graphic #########################
		# Set up sublot stuff ...
		fig = PL.figure(1)
		fig.subplots_adjust(left=0.125, right=0.9, bottom=0.1, top=0.9, wspace=0.2, hspace=1.0)
		yearsPadding = int((years[-1] - years[0])*.30) + 1
		
		# ...do subplot -- kt ...
		PL.subplot(4,1,1)
		PL.grid(True)
		PL.plot(years, self.ktComb, 'k', label='comb')
		PL.plot(years, self.ktMale, 'r', label='male')
		PL.plot(years, self.ktFem, 'b', label='fem')
		PL.xlabel('year')
		PL.title('kt, Second stage')
		PL.legend(loc='best', numpoints=4, prop=fp, pad=.1)
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE)
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((years[0], xticks[2:-2], years[-1]))
		xticks.sort()
		PL.xlim(xmin=years[0]-5, xmax=years[-1]+yearsPadding)
		(xticks, xlabels) = PL.xticks(xticks, fontsize=FONTSIZE)

		# ...subplot -- life exp ...
		PL.subplot(4,1,2)
		PL.grid(True)
		PL.plot(years, self.e0sFromEmpiricalNmxComb, 'k', label='emp comb')
		PL.plot(years, self.e0sFromEmpiricalNmxMale, 'r', label='emp male')
		PL.plot(years, self.e0sFromEmpiricalNmxFem, 'b', label='emp fem')
		pl, = PL.plot(years, self.e0sFromKtCurrent_unfitComb, 'k--', label='fit comb' )
		pl.set_dashes([4,2]) 
		pl, = PL.plot(years, self.e0sFromKtCurrent_unfitMale, 'r--', label='fit male' )
		pl.set_dashes([4,2]) 
		pl, = PL.plot(years, self.e0sFromKtCurrent_unfitFem, 'b--', label='fit fem' )
		pl.set_dashes([4,2]) 
		PL.title('E_0')
		PL.legend(loc='best', prop=fp, pad=.1)
		PL.xlabel('year')
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE) 
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((years[0], xticks[2:-2], years[-1]))
		xticks.sort() 
		PL.xticks(xticks, fontsize=FONTSIZE)
		PL.xlim(xmin=years[0]-5, xmax=years[-1]+yearsPadding)

		# ...subplot -- bx ...
		PL.subplot(4,1,3) 
		PL.plot(ages[:self.ageCutoffIndex], self.bxComb, 'x-k', label='comb')
		PL.plot(ages[:self.ageCutoffIndex], self.bxMale, 'x-r', label='male')
		PL.plot(ages[:self.ageCutoffIndex], self.bxFem, 'x-b', label='fem')
		PL.legend(loc='best', prop=fp, pad=.1)
		PL.xlabel('age')
		PL.title('bx')
		(locs, labels) = PL.yticks()
		PL.yticks(PL.array([locs[0], locs[-1]]), fontsize=FONTSIZE)
		PL.xticks(fontsize=FONTSIZE)

		# ...subplot -- ax ...
		PL.subplot(4,1,4)
		PL.plot(ages[:self.ageCutoffIndex], self.axComb, 'x-k', label='comb')
		PL.plot(ages[:self.ageCutoffIndex], self.axMale, 'x-r', label='male')
		PL.plot(ages[:self.ageCutoffIndex], self.axFem, 'x-b', label='fem')
		PL.legend(loc='best', prop=fp, pad=.1)
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
		PL.figure(2)

		# ...plot all forecast kt's on top of each other ...
		PL.subplot(2,1,1)
		PL.grid(True)
		for i in range(0, self.numRuns):
			PL.plot(years_fcst, self.kt_simul[i,:], 'k', linewidth=.25, label='_nolegend_') 
		PL.plot(years_fcst, self.lowerKtProjected, 'b--', linewidth=2.5,
				label='low combined kt: %3.1f%%' % self.percentiles[1]) # XXX Magic number
		PL.plot(years_fcst, self.meanKtProjected, 'k--', linewidth=2.5,
				label='mean combined kt: %3.1f%%' % self.percentiles[2]) # XXX Magic number 
		PL.plot(years_fcst, self.upperKtProjected, 'b--', linewidth=2.5,
				label='high combined kt: %3.1f%%' % self.percentiles[3]) # XXX Magic number
		PL.title('kt projections')
		PL.legend(prop=fp, loc='best')
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((years_fcst[0], xticks[2:-2], years_fcst[-1]))
		xticks.sort()
		PL.xticks(xticks)

		# ...plot all forecast e0's on top of each other ...
		PL.subplot(2,1,2)
		PL.grid(True)
		PL.plot(years_fcst, self.lowerE0ProjectedFem, 'b--', linewidth=2.5,
				label='mean fem e0: %3.1f%%' % self.percentiles[1]) 
		PL.plot(years_fcst, self.meanE0ProjectedFem, 'b.-', linewidth=2.5,
				label='mean fem e0: %3.1f%%' % self.percentiles[2]) 
		PL.plot(years_fcst, self.upperE0ProjectedFem, 'b--', linewidth=2.5,
				label='mean fem e0: %3.1f%%' % self.percentiles[3]) 
		for i in range(0, self.e0s_projectedFem.shape[0]):
			PL.plot(years_fcst, self.e0s_projectedFem[i, :], 'b', linewidth=.5, label='_nolegend_')

		PL.plot(years_fcst, self.lowerE0ProjectedMale, 'r--', linewidth=2.5,
				label='mean male e0: %3.1f%%' % self.percentiles[1]) 
		PL.plot(years_fcst, self.meanE0ProjectedMale, 'r.-', linewidth=2.5,
				label='mean male e0: %3.1f%%' % self.percentiles[2]) 
		PL.plot(years_fcst, self.upperE0ProjectedMale, 'r--', linewidth=2.5,
				label='mean male e0: %3.1f%%' % self.percentiles[3]) 
		for i in range(0, self.e0s_projectedMale.shape[0]):
			PL.plot(years_fcst, self.e0s_projectedMale[i, :], 'r', linewidth=.5, label='_nolegend_') 

		PL.title('e0 projections')
		PL.legend(prop=fp, loc='best')
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
		PL.figure(3)
		PL.grid(True)
		nmx_tmp = (self.nmxComb)
		nmx_kt_tmp= (self.nmxsFromKtCurrentComb) 
		colors = 'bgrcm'
		for i, age in enumerate(LCFIT_LOGNMX_GRAPHIC_AGES): 
			try:
				pl, = PL.semilogy(years, nmx_tmp[:, LCFIT_AGE_INDICES[age]],
						colors[i%len(colors)]+'-', label='Age: %i' % age)
				pl, = PL.semilogy(years, nmx_kt_tmp[:, LCFIT_AGE_INDICES[age]],
						colors[i%len(colors)]+'--', label='_nolegend_')
				pl.set_dashes([4,2])
			except IndexError, e:
				raise IndexError, "error: %s. size self.lnmx: %s.  age: %s, age index: %s." % \
					  (e, self.nmx.shape, age, LCFIT_AGE_INDICES[age])
			pass
		del nmx_tmp
		del nmx_kt_tmp
		PL.title('Within sample log nmx (combined M & F),\n(dashed=LC, full=empirical)')
		PL.legend(prop=fp, loc='best')
		PL.text(1,1, 'Dashed is recalculated mx from fit')
		(xticks, xlabels) = PL.xticks()
		xticks = N.hstack((years[0], xticks[1:-1], years[-1] + abs(xticks[0]-xticks[2])))
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

		# Delete temp directory of images
		os.rmdir(self.datapath)


	def __str__(self):
		"""Return a string that gives the content of the LC object"""
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
		year_end = (self.start_year + self.nmxComb.shape[0] - 1)
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
		dumpLink = LCFIT_WWW_OBJECT_DUMP + '&LC_OBJECT_ID=' + str(self.LcID)
		run_info += "<p><form action='%s'> <button name='LC_OBJECT_ID' value='%s'> Object Dump </button></form></p>" % \
					(dumpLink,str(self.LcID))

		# ... close run info.
		run_info += ''

		# Empirical data by year
		# image summarizing inference
		lc_img_path = LCFIT_WWW_DISPLAY_IMAGE + '&' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + LC_IMAGE_NAME
		lc_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of LC Summary %s"></a>\n' \
				   % (lc_img_path, lc_img_path, IMGH, IMGW, self.LcID)

		# image tracing log rates 
		lnmx_img_path = LCFIT_WWW_DISPLAY_IMAGE + '&' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + LNMX_IMAGE_NAME
		lnmx_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of selected LNMXes %s"></a>\n' \
				   % (lnmx_img_path, lnmx_img_path, IMGH, IMGW, self.LcID)

		# image summarizing forecast
		fc_img_path = LCFIT_WWW_DISPLAY_IMAGE + '&' + LCFIT_OBJECT_ID_KEY + '=' \
					  + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + FC_IMAGE_NAME
		fc_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of LC Summary %s"></a>\n' \
				   % (fc_img_path, fc_img_path, IMGH, IMGW, self.LcID)

		# Build html string (rather rudimentary, sorry)
		HTMLstr = '<table  border="1">\n' + \
				  '<tr><td colspan=3> <h3>LCFIT Run</h3></td>\n' + \
				  '<tr><td colspan=3>' + run_info + '</td></tr>\n' + \
				  '<tr><td colspan=3>' + lc_image + fc_image + lnmx_image + '</td></tr>\n' + \
				  '<tr><td colspan=3> Please direct questions or comments to: %s </td>\n' % EMAIL + \
				 '</table>\n'
		return HTMLstr

	def _dumpText(self):
		self.dumpString = LcUtil.dumpObject(self,
											helpParagraph=LCFIT_DUMP_HELP,
											dontDump=LCFIT_NOTWANTED_ATTRIBUTE_DUMPS,
											annoStructure=LCFIT_VAR_ANNOTATION_MF,
											fieldsep=LCFIT_FIELDSEP,
											rowsep=LCFIT_ROWSEP,
											stanzasep=LCFIT_STANZASEP)

