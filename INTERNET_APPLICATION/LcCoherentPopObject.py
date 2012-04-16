#!/usr/bin/python
'''
This module provides the home for LcCoherentObject, and a number of
module functions to support this.

Model country mortality by (1) modeling the combined mortality
(weighted by pop) and (2) modleing the the residuals of the individual
kt against the combined kt.
'''


## Imports ###############################################
from LcLog import lcfitlogger

from LcConfig import *                  # This imports numpy and friends
from LcAnnotation import *
from LcSinglePopObject import *
sys.path.append('./TESTING')            # For test data

import LcUtil
from LcUtil import Diagnose as D
import LcExtension
LcExtension.setExtensionName(LCFIT_DEFAULT_EXTENSION_METHOD)

## Module Variables  ###### 
LcObjectINFO ='LcCoherentPopObject' # Project/misc information

# Image constants
FC_IMAGE_NAME = 'lc-forecast.png'       # Image with forecasted stuff
E0S_IMAGE_NAME = 'lc-e0s.png'           # Empirical e0s for each subpopulation
E0S_FCST_IMAGE_NAME = 'lc-e0s-fcst.png' # Forecasted e0s for each subpop and combined 
LNMX_IMAGE_NAME = 'lc-lognmx.png'   # Emprical log nmx at various ages
LC_IMAGE_NAME = 'lc-model.png'          # Image with kt, ax, bx, e0u
IMGH = 150                              # Height of all images
IMGW = 200                              # Width of all images


############################################################################################
### Coherent populations LC class
############################################################################################
class LcCoherentPop(LcSinglePop):
    """ Using LcSingle __init__"""

    def _dealWithRates(self, populations, mortRates, labels='', **kwargs):
        """ Store the population and rate data.  Create the combined rates matrix. """

        # Save code version info with instance.  Here because I think
        # it is screwing up based on # some weird scoping thing in MF
        self.LcObjectINFO = LcObjectINFO
        
        # Age cutoff
        self.ageCutoffIndex = LCFIT_AGE_INDICES[self.ageCutoff] + 1

        # Population data
        self.populationText = re.sub('\n', '\n', populations) 
        self.populationText = re.sub('\r', '', self.populationText).strip()
        self.populationText = re.sub('\n+$', '', self.populationText)
        self.populationText = re.sub('^\n+', '', self.populationText)
        if LCFIT_EMPTY_ALL_RE.search(self.populationText):
            self.useWeightedMx = False 
            self.populationTextList = []
            self.populationList = []
        else:
            self.useWeightedMx = True
            self.populationTextList = re.split('\n\n+', self.populationText) 
            self.populationList = [LcUtil.parseRates(pops) for pops in self.populationTextList]

        # Mortality data
        self.mortRatesText = re.sub('\n', '\n', mortRates) 
        self.mortRatesText = re.sub('\r', '', mortRates)
        self.mortRatesText = re.sub('\n+$', '', self.mortRatesText)
        self.mortRatesText = re.sub('^\n+', '', self.mortRatesText)
        if LCFIT_EMPTY_ALL_RE.search(self.mortRatesText):
            raise LcException("empty rates data")       
        self.mortRatesTextList = re.split('\n\n+', self.mortRatesText) # 
        self.mortRatesList = [LcUtil.parseRates(rates) for rates in self.mortRatesTextList]

        # Go over each data matrix, check input:  no weird numbers, same size.
        shapeList = []
        shapeShape = self.mortRatesList[0].shape
        for i, data in enumerate(self.populationList + self.mortRatesList):
            if data.shape != shapeShape:
                raise LcException("Inconsistent rate matrix shapes. First matrix shape: %r, current matrix [%r] shape: %r\nData: %r" % \
                                  (shapeShape, i, data.shape, data[0,:].tolist()))
            shapeList.append(data.shape)
            pass
        if self.useWeightedMx:
            if len(self.populationList) != len(self.mortRatesList):
               raise LcException("Must have pop and mx of same length.  Pop = %i, Mort = %i." % \
                                 (len(self.populationList), len(self.mortRatesList)))

        # CG and takes logs of each of the rates
        self.mortRatesListLog = []
        for i, mxMatrix in enumerate(self.mortRatesList):
            self.mortRatesList[i] = LcExtension.extendMx(mxData=mxMatrix, ageCutoff=LCFIT_DEFAULT_AGE_CUTOFF)
            self.mortRatesListLog.append(N.log(self.mortRatesList[i]))

        # Labels
        if labels == '':
            self.labels = map(str,range(1, len(self.mortRatesListLog)+1))
        else:
            self.labels = re.split('\s+', labels.strip())
            if len(self.labels) < len(self.mortRatesListLog):
                labelExtraNumbers = range(len(self.labels)+1, len(self.mortRatesListLog)+1)
                labelExtra = map(str, labelExtraNumbers)
                self.labels = self.labels + labelExtra
            elif len(self.labels) > len(self.mortRatesListLog):
                self.labels = self.labels[0:(len(self.mortRatesListLog))]

        # Years
        self.yearIndices = N.arange(1, self.mortRatesList[0].shape[0]+1, dtype=N.int0) 
        years_end = self.start_year + self.mortRatesList[-1].shape[0]
        self.years = N.array(range(self.start_year, years_end)) 
        assert len(self.years) >= 1, AssertionError("years: %s" % self.years)
        self.years_fcst = N.array(range(years_end-1, years_end + self.stepsForward)) 

        # Create an average mx matrix.  If populations empty, no
        # weights; if there is data for populations (1) check for
        # reasonableness in size and number and (2) use population as
        # weights and do the averaging.
        if  self.useWeightedMx:
            self.totalWeightedMx = N.zeros_like(self.mortRatesList[0])
            self.totalPop = N.zeros_like(self.populationList[0]) 
            for (mx, pop) in zip(self.mortRatesList, self.populationList):
                self.totalWeightedMx = self.totalWeightedMx + (mx*pop)
                self.totalPop = self.totalPop + pop
                pass
            self.averagedMx = self.totalWeightedMx/self.totalPop
        else:
            temp_mx = N.zeros_like(self.mortRatesList[0])
            for mx in self.mortRatesList:
                temp_mx += mx
            self.averagedMx = temp_mx / len(self.mortRatesList)
        self.averagedMx = LcExtension.extendMx(mxData=self.averagedMx, ageCutoff=LCFIT_DEFAULT_AGE_CUTOFF)
        self.averagedMxLog = N.log(self.averagedMx)

        # Check data for ok-ness in mortality (not population, since
        # that might be non-CG'ed and have nans).
        for i, data in enumerate(self.mortRatesList + self.mortRatesListLog + [self.averagedMxLog, self.averagedMx]):
            assert N.isfinite(data).all(), \
                   AssertionError("Bad data in mx[%r]:\n %r" % (N.round_(data, 2), i))
        # Check for weird (ie > 1.0) numbers
        for i, data in enumerate(self.mortRatesList + [self.averagedMx]):
            if not (data<1.2).all():
                raise LcException("Weird mx: \n%s\n%s" % (data[data<1.2], i))


    def _do_lc(self):
        """
        Do the inference and the simulation, saving the results as
        state in the instance.
        """

        ########## LC step #########        
        # (Note using ageCutoff=None since want the whole thing to the CG'ed end)
        #
        # Lc of combined ...
        self.combinedLc = lcInfer(self.averagedMx, self.lifeTableParams,
                                  ageCutoff=None, doFit=True, returnDict=True, flattenBx=self.flattenBx, doTS=True) 
        self.combinedLc['e0emp'] = N.apply_along_axis(LcUtil.lifeTable, 1, self.averagedMx) # Give a vector of e0, one per year
        self.combinedLc['e0kt'] = N.apply_along_axis(LcUtil.lifeTable, 1,
                                                     project_nmx(ax=self.combinedLc['ax'],
                                                                 bx=self.combinedLc['bx'],
                                                                 kt=self.combinedLc['ktFit'],
                                                                 ageCutoff=self.ageCutoff))

        if not ((self.combinedLc['e0emp'] > 10.0) & (self.combinedLc['e0emp'] < 150.0)).all():
            raise Exception("Weird e0 in averaged Mx.  \n\te0s: %s.  \n\n\tmx: %s\n" \
                            % (self.combinedLc['e0emp'], self.averagedMx))

        # ... explanation ratio -- ratio of first eigenvalue squared ...
        # over SS of all eigenvalues ...
        num = self.combinedLc['X'][0]**2
        den = N.sum(self.combinedLc['X'] * self.combinedLc['X'])
        self.proportion_first_eigenvalue_from_combined = num / den
        del num, den
        
        # ... lists that will contain stuff for each separate population ...
        self.lnmxc1List = []
        self.lnmxc2List = []
        self.individualLc = []
        self.individualResidualLc = []
        self.R_S, self.R_C, self.R_AC, self.R_Foo, self.R_AR1, self.R_RW = ([],[],[],[],[],[]) # These are epr matrix from code
        self.ktResidualBackSimulated = []
        self.coherentRsqrd = []
        self.R_S_terms = []             # For collecting diagnostics
        self.R_C_terms = []
        self.lnmxc1SubTermList = []     # From here down, all for debugging, intermediate steps
        self.lnmxc2SubTermList = []
        self.lnmxc2ListExped = []
        self.BxKt = []
        self.axMat = []
        
        for mxIndex, mx in enumerate(self.mortRatesList):
            ## For each mx calculate the LC of the given rates, the
            ## residuals off of the "common factor", and the LC of the
            ## residuals, storing each of these in its respective
            ## list.  Also calculate new mx'es, life expectancies,
            ## explanation-ratios, etc for all steps.

            # For understanding MATLAB code: % Bx,Kt are combined;
            # bxo,kto are individual standard; bxc,kc are individual
            # residual

            # Do individual lc  ( ax -- Average log mx (over years))
            self.individualLc.append(lcInfer(mx, self.lifeTableParams, ageCutoff=None,
                                             doFit=True, returnDict=True,
                                             flattenBx=self.flattenBx, doTS=True)) 
            self.individualLc[-1]['e0emp'] = N.apply_along_axis(LcUtil.lifeTable, 1, mx)
            self.individualLc[-1]['e0kt'] = N.apply_along_axis(LcUtil.lifeTable, 1,
                                                               project_nmx(ax=self.individualLc[-1]['ax'],
                                                                           bx=self.individualLc[-1]['bx'],
                                                                           kt=self.individualLc[-1]['ktFit'],
                                                                           ageCutoff=self.ageCutoff))
            # add name from labels
            self.individualLc[-1]['label'] = self.labels[mxIndex]
            
            # Calculate item by residuals, against ax ... 
            self.lnmxc1SubTermList.append(self.individualLc[-1]['ax'].reshape(1,-1))
            self.lnmxc1List.append(N.log(mx) - self.individualLc[-1]['ax'].reshape(1,-1)) # .reshape to make 1 by 24 matrix

            # ...and against ax with combined kt + bx
            self.BxKt.append(N.dot(self.combinedLc['ktFit'].reshape(-1,1),self.combinedLc['bx'].reshape(1,-1)))
            self.BxKt[-1].resize(self.averagedMx.shape)
            axMat = N.repeat(self.individualLc[-1]['ax'].reshape(1,-1), self.BxKt[-1].shape[0], 0) 
            self.axMat.append(axMat)
            self.lnmxc2SubTermList.append(self.axMat[-1] + self.BxKt[-1])
            self.lnmxc2List.append(N.log(mx) - self.lnmxc2SubTermList[-1])
            self.lnmxc2ListExped.append(N.exp(self.lnmxc2List[-1]))

            # calculate SVD of residuals, R_A and R_AC.
            # TURNED OFF AX NORMALIZATION TO MATCH MATLAB CODE
            self.individualResidualLc.append(lcInfer(N.exp(self.lnmxc2List[-1]), self.lifeTableParams,
                                                     ageCutoff=None, doFit=False, returnDict=True, normalizeMx=False,
                                                     flattenBx=False, doTS=True))

            # Explanation ratios for each country:
            # Prep all the terms for the explanation ratios ...
            (xx1, xx2, xx3, xx4, xx5) = (0,0,0,0,0)
            for yrIndex, logMxRow in enumerate(N.log(mx)): # for each row (year) ...
                xx1 += N.sum((logMxRow - self.individualLc[-1]['ax'])**2)
                xx2 += N.sum((logMxRow - self.individualLc[-1]['ax'] \
                              - self.combinedLc['bx'] * self.combinedLc['ktFit'][yrIndex])**2)
                xx3 += N.sum((logMxRow - self.individualLc[-1]['ax'] \
                              - self.combinedLc['bx'] * self.combinedLc['ktFit'][yrIndex] \
                              - self.individualResidualLc[-1]['bx'] * self.individualResidualLc[-1]['ktUnfit'][yrIndex])**2)
                xx4 += N.sum((logMxRow - self.individualLc[-1]['ax'] \
                              - self.individualLc[-1]['bx'] * self.individualLc[-1]['ktFit'][yrIndex])**2)
                xx5 += N.sum((logMxRow - self.individualLc[-1]['ax']
                              - self.individualResidualLc[-1]['bx'] * self.individualResidualLc[-1]['ktUnfit'][yrIndex])**2)
                pass
            # ... calculate and store explanation ratios for how much
            # is added by bothering with the residuals component of
            # the model.
            self.R_S.append(1-xx4/xx1)  # In the code, I think
            self.R_C.append(1-xx2/xx1) # R_C(i) (5) in paper
            self.R_AC.append(1-xx3/xx1) # R_AC(i) (7) in paper
            self.R_Foo.append(1-xx5/xx1)  # Definitely in the code
            self.R_AR1.append(self.individualResidualLc[-1]['ktunfit_ar1']['exRatio'])
            self.R_RW.append(self.individualResidualLc[-1]['ktunfit_rw']['exRatio'])
            self.R_C_terms.append((xx1, xx2, xx3))
            
            # Derive e_0 for individual country based on svd of both mx and residuals
            # using ax not from residual but from individual full mx
            self.individualResidualLc[-1]['e0kt'] = N.apply_along_axis(LcUtil.lifeTable, 1, project_nmx(
                ax=self.individualLc[-1]['ax'], 
                bx=self.individualLc[-1]['bx'],
                kt=self.individualLc[-1]['ktFit'],
                kt_resid = self.individualResidualLc[-1]['ktUnfit'],
                bx_resid = self.individualResidualLc[-1]['bx'],
                ageCutoff=self.ageCutoff))

            pass # End of cycling through the individual countries
        
        ## Simulate
        #
        # Special simulation data structure hanging off of "self":
        # simulation matrix of kt comb, simulation matrix of kt resid
        # for each sub-pop, mx's for kt comb, mx's for comb+resid of
        # each sub pop
        self.Simulation = dict(kt_comb=N.zeros((self.numRuns,self.stepsForward)),
                               kt_resid=[N.zeros((self.numRuns, self.stepsForward))]*len(self.individualResidualLc),
                               kt_comb_plus_resid=[N.zeros((self.numRuns, self.stepsForward))]*len(self.individualResidualLc),
                               mx_comb=N.zeros((self.numRuns,self.stepsForward,LCFIT_DEFAULT_NO_AGEWIDTHS)),
                               mx_indiv=[N.zeros((self.numRuns,self.stepsForward,LCFIT_DEFAULT_NO_AGEWIDTHS))]*len(self.individualResidualLc),
                               e0_comb=N.zeros((self.numRuns,self.stepsForward)),
                               e0_indiv=[N.zeros((self.numRuns,self.stepsForward))]*len(self.individualResidualLc))

        # Simulate common factor kt based on RWD params, with LcSingle.sim_kt
        self.Simulation['kt_comb'] = sim_kt(SEC=self.combinedLc['kt_rw']['stdErrorCoeff'],
                                            SEE=self.combinedLc['kt_rw']['stdErrorEq'],
                                            drift=self.combinedLc['kt_rw']['drift'],
                                            ktStart=self.combinedLc['ktFit'][-1],
                                            numRuns=self.numRuns,
                                            stepsForward=self.stepsForward,
                                            sortflag=False)

        # create e0s and mxs, sort kt_comb based on end value of projection
        self.Simulation['mx_comb'] = project_nmx(ax=self.combinedLc['ax'],
                                                 bx=self.combinedLc['bx'],
                                                 kt=self.Simulation['kt_comb'], # [:,1:] would drop the first column of kt
                                                 ageCutoff=self.ageCutoff)
        self.Simulation['e0_comb'] = lots_e0s(self.percentileIndices, self.Simulation['mx_comb'], self.lifeTableParams)

        # For each sub pop, simulate kt of resid, add them to common thingy to get mx, then get e0
        for popIndex in range(0, len(self.individualResidualLc)):
            ## Simulate residual time series . Note that we start the sim of the residual at zero
            self.Simulation['kt_resid'][popIndex] = sim_kt_ar1(stdckt=self.individualResidualLc[popIndex]['ktunfit_ar1']['stdckt'], 
                                                               c0=self.individualResidualLc[popIndex]['ktunfit_ar1']['c0'],
                                                               sda0=self.individualResidualLc[popIndex]['ktunfit_ar1']['sda0'],
                                                               c1=self.individualResidualLc[popIndex]['ktunfit_ar1']['c1'], 
                                                               sda1=self.individualResidualLc[popIndex]['ktunfit_ar1']['sda1'], 
                                                               ktStart=0,
                                                               numRuns=self.numRuns,
                                                               stepsForward=self.stepsForward,
                                                               sortflag=False)
            
            ## Derive forecast kt from forecast comb + forecast resid + offset
            kt_comb_offset = self.individualLc[popIndex]['ktFit'][-1] - self.combinedLc['ktFit'][-1]
            self.Simulation['kt_comb_plus_resid'][popIndex] = self.Simulation['kt_comb'] + self.Simulation['kt_resid'][popIndex] + kt_comb_offset 

            ## mx of above 
            self.Simulation['mx_indiv'][popIndex] = project_nmx(ax=self.individualLc[popIndex]['ax'],
                                                                bx=self.combinedLc['bx'],
                                                                kt=self.Simulation['kt_comb_plus_resid'][popIndex],
                                                                ageCutoff=self.ageCutoff) 
            ## e0
            self.Simulation['e0_indiv'][popIndex] = lots_e0s(lots_nmx=self.Simulation['mx_indiv'][popIndex],
                                                             lifeTableParams=self.lifeTableParams,
                                                             percentileIndices=self.percentileIndices,
                                                             sortflag='column-wise')
            pass
        return                          # Don't return anything useful

    def _do_graphics(self, numAgeWidths=LCFIT_DEFAULT_NO_AGEWIDTHS,
                     lcImageName=LC_IMAGE_NAME, fcImageName=FC_IMAGE_NAME,
                     lnmxImageName=LNMX_IMAGE_NAME, e0sFcstImageName=E0S_FCST_IMAGE_NAME,
                     e0sImageName=E0S_IMAGE_NAME):

        ##### Font etc constants
        FONTSIZE='xx-small'
        fp = MPL.font_manager.FontProperties(size=FONTSIZE)
        LEGEND_KW = dict(numpoints=2,  pad=.05, prop=fp)
        colors = 'bgrcmy' 
        
        ##### Set up overall graphics stuff ################
        ages = LCFIT_AGES
        years_end = self.start_year + self.averagedMx.shape[0]
        years = N.array(range(self.start_year, years_end)) 
        assert len(years) >= 1, AssertionError("years: %s" % years)
        years_fcst = N.array(range(years_end-1, years_end + self.stepsForward)) 

        #### Graphics #####################################

        ################################################################
        ## Graphic of e_0's, per country + averaged, both empirical and forecast
        fig = PL.figure(1)
        PL.grid(True, ls=":", lw=.25)
        yearsPadding = int((years[-1] - years[0])*.30) + 1

        # Empirical e_0
        pl, = PL.plot(years, self.combinedLc['e0emp'], '-k', label='combined',lw=.5)
        for i, stats in enumerate(self.individualLc):
            pl, = PL.plot(years, stats['e0emp'], colors[i%len(colors)]+'-', label=self.labels[i], lw=.5)
            pl, = PL.plot(years, self.individualResidualLc[i]['e0kt'], colors[i%len(colors)]+'-', lw=.25) # Rederived from kt resid and comb
            pl.set_dashes([4,3])
            pass

        ## Projected e_0.  I don't know why the black line seems continuous but the sub-pops aren't
        pl, = PL.plot(self.years_fcst, self.Simulation['e0_comb'][2], '-k', lw=.5)
        pl.set_dashes([4,2])
        for i, e0_stuff in enumerate(self.Simulation['e0_indiv']):
            # each population with 50% and +/-2.5%
            pl, = PL.plot(years_fcst, e0_stuff[2], colors[i%len(colors)],lw=.5)
            pl.set_dashes([1,1])
            pl, = PL.plot(years_fcst, e0_stuff[1], colors[i%len(colors)],lw=.1)
            pl.set_dashes([1,1])
            pl, = PL.plot(years_fcst, e0_stuff[3], colors[i%len(colors)],lw=.1)
            pl.set_dashes([1,1])
            pass

        ## Fix some other things on the graph...
        
        # Pad axis at right 
        axis = list(PL.axis()) 
        axis[1] = axis[1] + 20
        PL.axis(axis)

        # Titles, legends, etc
        PL.legend(loc='lower right', **LEGEND_KW)
        PL.xlabel('year')
        PL.title('E_0 comparison.\n Solid are empirical, dashed historical modeled, dotted forecast.')
        
        # ...save it and open it and store the binary.
        filename = os.path.join(self.datapath, e0sImageName) 
        PL.savefig(filename, dpi=150)
        PL.close(1)
        f = open(filename)
        self.imagesDict[e0sImageName] = f.read(-1) 
        f.close()
        os.unlink(filename)

        ##### Kt's -- empirical and forecast ######################
        PL.figure(2) # fc_image
            
        # Plot all forecast kt's: use the percentiles of the common kt and
        # the percentiles of the common kt + residual kt for each
        # sub-population.  Darken the medians.
        PL.plot()
        PL.grid(True, ls=":", lw=.1)

        # combined kt, empirical (fitted) and simulated (median) ...
        pl, = PL.plot(years, self.combinedLc['ktFit'], '-k', label='combined', lw=.75)
        pl, = PL.plot(years_fcst, self.Simulation['kt_comb'][self.percentileIndices[2]], '-k', lw=.75)
        pl.set_dashes([1,1])

        # ... stuff for each population ...
        for i, stats in enumerate(self.individualResidualLc):
            # ... empirical and simulated residuals (median) ...
            pl, = PL.plot(years, stats['ktUnfit'], colors[i%len(colors)]+'-', lw=1.25)
            pl, = PL.plot(years_fcst, self.Simulation['kt_resid'][i][self.percentileIndices[2]], colors[i%len(colors)]+'-', lw=0.75)
            pl.set_dashes([1,1])

            # ... empirical and simulated combined kt (simulated comb + simulated resid)
            pl, = PL.plot(years, 
                          self.individualLc[i]['ktFit'], 
                          colors[i%len(colors)]+'-', lw=.75, label=self.labels[i])
            pl, = PL.plot(years_fcst, 
                          self.Simulation['kt_comb_plus_resid'][i][self.percentileIndices[2]],
                          colors[i%len(colors)]+'-', lw=.75)
            pl.set_dashes([1,1])
            pass
        PL.legend(loc='lower left', **LEGEND_KW)
        PL.title('Kt: combined, residuals, combined + residual.\nSolid is empirical, dashed is forecast (median).')

        # ...save the file.
        filename = os.path.join(self.datapath, fcImageName) 
        PL.savefig(filename, dpi=150)
        PL.close(2)
        f = open(filename)
        self.imagesDict[fcImageName] = f.read(-1)
        f.close()
        os.unlink(filename)


        # Delete temp directory of images
        PL.close('all')                 # Just in case
        os.rmdir(self.datapath) 
        return


    def __str__(self):
        """Return a string that gives the content of the LC object"""

        run_info = ''
        # Info about the run/software/user/etc ...
        # ... include a link to the text dump of the object...
        dumpLink = LCFIT_WWW_OBJECT_DUMP + '&LC_OBJECT_ID=' + str(self.LcID)
        run_info += "<p><a href='%s'> Object Dump </button></a></p>" % (dumpLink,)

        # Info about the run/software/user/etc ...
        run_info += '<pre>RUN INFORMATION:\t\n'
        run_info += 'Current time:\t %s\n' % datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        run_info += 'Run time:\t %s\n' % self.timestamp 
        run_info += 'Software Id:\t %s\n' % self.LcObjectINFO
        run_info += 'Object ID:\t %s\n' % self.LcID
        run_info += '\nNotes:\t %s\n' % self.notes

        
        # ...display the scalar values of interetest ...
        run_info += '\n'
        run_info += 'First year of empirical data:\t %s\n' % self.start_year
        run_info += 'End year of empirical data:\t%s\n' % self.years[-1]
        run_info += 'End of forecast:\t%s\n' % self.years_fcst[-1]
        run_info += 'Cutoff age for age nmx extension:\t %s\n' % self.ageCutoff
        run_info += 'Lifetable age regime:\t 0-1, 1-4, 5-9, ..., 105-110, 110+\n'
        run_info += 'Percentile values for display:\t %s\n' % self.percentiles
        run_info += 'Number of projection runs:\t %s\n' % self.numRuns
        run_info += 'Number of years projected forward:\t %s\n' % self.stepsForward
        run_info += 'Width of projection step:\t %s year(s)\n' % LCFIT_PROJECTION_WIDTH
        run_info += 'Width of projection step:\t %s year(s)\n' % LCFIT_PROJECTION_WIDTH
        # ... close <pre>...
        run_info += '</pre>'

        # Explanation coefficients
        run_info += "<p>EPRs:</p>\n" + "<p>\n" + \
                    LcUtil.tablefy(dataList=N.array([self.R_S, self.R_C, self.R_AC,  self.R_RW, self.R_AR1, self.R_Foo]),
                                   sideLabels=self.labels,
                                   headings=['R_S', 'R_C', 'R_AC', 'R_RW', 'R_AR1', 'R_Foo']) + "</p>\n"
        run_info += "<p>EPCR: %s</p>\n" % self.proportion_first_eigenvalue_from_combined

        if True:
            # Ax for each input
            tmp_list =[L['ax'] for L in self.individualLc] + [self.combinedLc['ax']]
            tmp_str = LcUtil.tablefy(dataList=N.array(tmp_list),
                                        sideLabels=LCFIT_AGES,
                                        headings=self.labels + ['comb'],
                                        itemName='Age') 
            run_info += "<p>ax's:</p>\n" + "<p>\n" + tmp_str + "</p>\n"
            del tmp_list, tmp_str

            # bx for each input
            tmp_list =[L['bx'] for L in self.individualLc]  + [self.combinedLc['bx']]
            tmp_str = LcUtil.tablefy(dataList=N.array(tmp_list),
                                        sideLabels=LCFIT_AGES,
                                        headings=self.labels + ['comb'],
                                        itemName='Age') 
            run_info += "<p>bx's:</p>\n" + "<p>\n" + tmp_str + "</p>\n"
            del tmp_list, tmp_str

            # kt for each input
            tmp_list = [L['ktUnfit'] for L in self.individualResidualLc] \
                       + [self.combinedLc['ktFit'], self.combinedLc['e0emp']]
            tmp_array = N.array(tmp_list)
            tmp_str = LcUtil.tablefy(dataList=tmp_array,
                                     sideLabels=self.years,
                                     headings=self.labels + ['combination kt', 'e0-empirical'] ,
                                     itemName='Year') 
            run_info += "<p>Yearly Kt's:</p>\n" + "<p>\n" + tmp_str + "</p>\n"
            del  tmp_array, tmp_list, tmp_str

        if True:
            # AR(1) model for all residuals
            #self.individualResidualLc[i]['ktunfit_ar1']['c0, sda0, c1, sda1, Rsq, stderr_est']
            AR1_stuff = N.zeros((len(self.individualResidualLc),6))
            tmp_list = []
            tmp_headings = ['c0', 'sda0', 'c1', 'sda1', 'Rsq', 'stderr_est']
            for i, pop in enumerate(self.individualResidualLc):
                tmp_list.append([pop['ktunfit_ar1'][k] for k in tmp_headings])
            tmp_array = N.array(tmp_list, N.float_)
            run_info += "<p>AR(1) models for residuals:</p>\n" + "<p>\n" + \
                        LcUtil.tablefy(dataList=tmp_array.transpose(),
                                       sideLabels=self.labels+[],
                                       headings=tmp_headings,
                                       itemName='AR1 Model') + \
                                       "</p>\n"
            del(tmp_array, pop)

        if False:               # XXX This doesn't work!
            # forecast e0 for each input (think I switch indexing
            # conventions between inference and simulation ... not
            # good... [1]['kt_unfit'] vs ['kt_unfit'][1]
            tmp_list = [L for L in self.Simulation['e0_indiv']]
            tmp_array = N.array(tmp_list)
            tmp_str = LcUtil.tablefy(dataList=tmp_array,
                                     sideLabels=self.years,
                                     headings=self.labels,
                                     itemName='Year') 
            run_info += "<p>Yearly Forecast e0's:</p>\n" + "<p>\n" + tmp_str + "</p>\n"
            del  tmp_array, tmp_list, tmp_str


        # image summarizing forecast
        fc_img_path = LCFIT_WWW_DISPLAY_IMAGE + '&' + LCFIT_OBJECT_ID_KEY + '=' \
                      + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + FC_IMAGE_NAME
        fc_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of forecast kts %s"></a>\n' \
                   % (fc_img_path, fc_img_path, IMGH, IMGW, self.LcID)

        # image showing e0s
        e0_img_path = LCFIT_WWW_DISPLAY_IMAGE + '&' + LCFIT_OBJECT_ID_KEY + '=' \
                      + str(self.LcID) + '&' + LCFIT_IMAGE_NAME_KEY + '=' + E0S_IMAGE_NAME
        e0_image = '<a href=%s><img src="%s" height = %i width = %i alt="PNG of empirical e0s %s"></a>\n' \
                   % (e0_img_path, e0_img_path, IMGH, IMGW, self.LcID)
        
        # Build html string
        #'<tr><td colspan=3>' + lc_image + fc_image + lnmx_image + '</td></tr>\n' + \
        HTMLstr = '<table  border="1">\n' + \
                  '<tr><td colspan=3> <h3>LCFIT Run</h3></td>\n' + \
                  '<tr><td colspan=3>' + run_info + '</td></tr>\n' + \
                  '<tr><td>' + e0_image + fc_image + '</td></tr>\n' + \
                  '<tr><td colspan=3> Please direct questions or comments to: %s </td>\n' % EMAIL + \
                 '</table>\n'
        return HTMLstr


    def _dumpText(self):
        self.dumpString = LcUtil.dumpObject(self,
                                            helpParagraph=LCFIT_DUMP_HELP,
                                            dontDump=LCFIT_NOTWANTED_ATTRIBUTE_DUMPS,
                                            annoStructure=LCFIT_VAR_ANNOTATION_COHERENT,
                                            fieldsep=LCFIT_FIELDSEP,
                                            rowsep=LCFIT_ROWSEP,
                                            stanzasep=LCFIT_STANZASEP)




################################### 
if __name__ == '__main__':
    print "hello from LcSinglePopObject.py"
