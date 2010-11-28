#!/bin/sh 

## create an lcfit object, crap out if doesn't work.  Meant to be run
##   in a cron job, where an error will cause an email to be sent
##
## "inter" passed as an option leaves the working files around to be
##    inspected "interactively"

set -e 

ID="$(date +'%Y%m%d%H%M%s')-$RANDOM-$$"
COOKIEF="lcfit_cookies.$ID"
LCFITURL="http://lcfit.demog.berkeley.edu/lcfit/lc"
OUTF="lcfit_output.$ID"
MAXTIME=1			# How many seconds over which we
				# return non-zero
## start time
STARTT=$(date +%s)

## Log in and do some stuff, currently just grab the index of runs.
##   Should use the helpful curl return codes more ....
echo "Logging in" >> $OUTF
curl --silent -S --fail -b "$COOKIEF" -c "$COOKIEF" -d "USERNAME=webbs&PASSWORD=foobar" \
	"$LCFITURL/LoginProcess" 1>>$OUTF

echo "Getting index" >> $OUTF
curl --silent -S --fail -b "$COOKIEF" -c "$COOKIEF"  \
	"$LCFITURL/index" 1>>$OUTF

STOPT=$(date +%s)
ELAPSET=$(expr $STOPT - $STARTT ) 
echo "Timing: $ELAPSET seconds." >> "lcfit_stats.$ID"

if [[ $ELAPSET > $MAXTIME ]]; then
    echo "curl_lcfit: taking a long time: $ELAPSET seconds."
    exit 1
fi

case "$1" in
    *inter*)
        echo "See output in $OUTF..." 
        ;;
    *)
	rm *.$ID    
	;;
esac
