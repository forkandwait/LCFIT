from LcConfig import *

ageList = ', '.join([str(x) for x in LARRY_AGES])

LARRY_DUMP_HELP = """
This is a dump of all of the variables that are created when you do a
Lee-Carter analysis.  First there is a one list of list of all the
variables.  Then there is a section in which each with annotation is
printed, with its description; this section is sorted by order of
interest.  After that is a section that contains all the remaining
variables which are not annotated (and probably of no interest except
to the programmer); it is sorted alphabetically and lacks explanatory
notes."""

LARRY_VAR_ANNOTATION_SINGLESEX = [
	['ax', 'Vector of ax values for ages = ' + ageList],
	['bx', 'Vector of bx values for ages = ' + ageList],
	['kt', 'Principle component of time series with adjustment by life expectancy'],
	['kt_unfit', 'Principle component of time series directly from SVD without adjustment'],
	['e0sFromEmpiricalNmx', 'Life expectancy calculated directly from rates'],
	['medianE0Projected', 'Median projected life expectancy - deterministic'],
	['nmx_projected_stochastic_median_final', 'Last year mx from projection - stochastic'],
	['nmx_projectedMedianFinal', 'Last year mx from projection - deterministic'],
	['lnmx', 'Log rates from sample.  Years go down, and ages go across.'],
	['nmx', 'Original parsed rates from sample'],
	]

LARRY_VAR_ANNOTATION_COHERENT = [
	['R_S', 'List of R_S for each individual pop'],
	['R_S_terms', ''],
	['R_C', 'List of R_C for each individual pop'],
	['R_AC', 'List of R_AC for each individual pop'],
	['combinedLc', 'LC results for the weighted average mx'],
	['individualLc', 'List of LC results for each set of rates (structured as a "dictionary"'],
	['individualResidualLc', 'List of LC results on the residuals for each population'],
	['Simulation', 'Dict with all the simulation data and parameter.  ' + \
	 '"e0_comb" are the percentile e0''s for the combined population.  ' + \
	 '"e0_indiv" are percentile e0''s for each given coherent population.'],
]

LARRY_VAR_ANNOTATION_MF = [
	['axComb', 'Combined sex: vector of ax values for ages = ' + ageList],
	['bxComb', 'Combined sex: vector of bx values for ages = ' + ageList],
	['ktComb', 'Combined sex: principle component of time series with adjustment by life expectancy'],
	['kt_unfitComb', 'Combined sex: principle component of time series directly from SVD without adjustment'],
	['e0sFromEmpiricalNmxComb', 'Combined sex: life expectancy calculated directly from rates'],

	['nmx_projected_stochastic_median_final_F', 'Last year Female mx from projection - stochastic'],
	['nmx_projected_median_final_F', 'Last year Female mx from projection - deterministic'],
	['nmx_projected_stochastic_median_final_M', 'Last year Male mx from projection - stochastic'],
	['nmx_projected_median_final_M', 'Last year Male mx from projection - deterministic'],
	
	['lnmxComb', 'Combined sex: log rates from sample.  Years go down.  Ages go across.  Cut and paste for a regular looking table.'],
	['nmxComb', 'Combined sex: original parsed rates from sample'],

	['axFem', 'Female: vector of ax values for ages = ' + ageList],
	['bxFem', 'Female: vector of bx values for ages = ' + ageList],
	['ktFem', 'Female: principle component of time series with adjustment by life expectancy'],
	['kt_unfitFem', 'Female: principle component of time series directly from SVD without adjustment'],
	['e0sFromEmpiricalNmxFem', 'Female: life expectancy calculated directly from rates'],
	['meanE0ProjectedFem', 'Female: mean projected life expectancy'], 
	['lnmxFem', 'Female: log rates from sample.  Years go down.  Ages go across.  Cut and paste for a regular looking table.'],
	['nmxFem', 'Female: original parsed rates from sample'],

	['axMale', 'Male: vector of ax values for ages = ' + ageList],
	['bxMale', 'Male: vector of bx values for ages = ' + ageList],
	['ktMale', 'Male: principle component of time series with adjustment by life expectancy'],
	['kt_unfitMale', 'Male: principle component of time series directly from SVD without adjustment'],
	['e0sFromEmpiricalNmxMale', 'Male: life expectancy calculated directly from rates'],
	['meanE0ProjectedMale', 'Male: mean projected life expectancy'], 
	['lnmxMale', 'Male: log rates from sample.  Years go down.  Ages go across.  Cut and paste for a regular looking table.'],
	['nmxMale', 'Male: original parsed rates from sample'],
	]
