########################
## Set up logging using the overly complicated python module
########################

import logging

## Logfile name
LCFIT_LOGFILENAME='/home/webbs/lcfitlog'

## initialize lcfitlogger
lcfitlogger = logging.getLogger('LCFIT')
lcfitlogger.setLevel(logging.DEBUG)

## set up handler and formatter, add to lcfitlogger
ch = logging.FileHandler(filename=LCFIT_LOGFILENAME)
ch.setLevel(logging.INFO)
_fstr = "%(name)s:%(levelname)s:%(asctime)s:%(process)d:%(thread)d:%(pathname)s(%(lineno)d)::\"%(message)s\""
formatter = logging.Formatter(_fstr)
ch.setFormatter(formatter)
lcfitlogger.addHandler(ch)

##
lcfitlogger.debug("LcLog.py")
