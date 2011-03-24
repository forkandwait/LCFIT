#!/bin/sh 

## create an lcfit object, crap out if doesn't work.  Meant to be run
##   in a cron job, where an error will cause an email to be sent
##
## "inter" passed as an option leaves the working files around to be
##    inspected "interactively"

set -e -u

## help on positional 
if [[ ${1:-ack} == help ]]; then
    echo 'curl_lcfit.sh -- test rudimentary connections to LCFIT'
    echo '    CTIMEOUT=${1:-12}'
    echo '    MAXTIME=${2:-4}'
    echo '    INTER=${3:-"auto"}'
    echo '    LCFITURL=${4:-"http://lcfit.demog.berkeley.edu/lcfit/lc"}'
    exit 2
fi

## Hardcoded stuff
ID="$(date +'%Y%m%d%H%M%s')-$RANDOM-$$"
COOKIEF="lcfit_cookies.$ID"
OUTF="lcfit_output.$ID"

## Command line stuff
CTIMEOUT=${1:-12}               # Curl timeout
MAXTIME=${2:-4}                   # How many seconds over which we return non-zero and output to the user
INTER=${3:-"auto"}               # Whether to save files ("inter") or delete ("auto") at end 
LCFITURL=${4:-"http://lcfit.demog.berkeley.edu/lcfit/lc"}

## start time
STARTT=$(date +%s)

## Log in and do some stuff, currently just grab the index of runs.
##   Should use the helpful curl return codes more ....
echo "Logging in" >> $OUTF
curl --max-time $CTIMEOUT --silent -S --fail -b "$COOKIEF" -c "$COOKIEF" -d "USERNAME=webbs&PASSWORD=foobar" \
    "$LCFITURL/LoginProcess" 1>>$OUTF

echo "Getting index" >> $OUTF
curl --max-time $CTIMEOUT --silent -S --fail -b "$COOKIEF" -c "$COOKIEF"  \
    "$LCFITURL/index" 1>>$OUTF

STOPT=$(date +%s)
ELAPSET=$(expr $STOPT - $STARTT ) 
echo "Timing: $ELAPSET seconds." >> "lcfit_stats.$ID"
echo "curl_lcfit timing ($(date)): $ELAPSET seconds." > "$HOME/curl_lcfit.dat.txt"

if [[ $ELAPSET > $MAXTIME ]]; then
    echo "curl_lcfit: taking a long time: $ELAPSET seconds. $(date)"
    exit 1
fi

rm *.$ID    