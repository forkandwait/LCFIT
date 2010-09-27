set -e 

ID="$(date +'%Y%m%d%H%M%s')-$RANDOM-$$"
COOKIEF="lcfit_cookies.$ID"
LCFITURL="http://lcfit.demog.berkeley.edu/lcfit/lc"
OUTF="lcfit_output.$ID"

echo "Logging in" >> $OUTF
curl --silent -S --fail -b "$COOKIEF" -c "$COOKIEF" -d "USERNAME=webbs&PASSWORD=foobar" \
	"$LCFITURL/LoginProcess" 1>>$OUTF

echo "Getting index" >> $OUTF
curl --silent -S --fail -b "$COOKIEF" -c "$COOKIEF"  \
	"$LCFITURL/index" 1>>$OUTF

rm *.$ID