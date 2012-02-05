set -e 
set -u 

## config
ST=1950
FIN=2007
SEX=F
COUNTRIES="USA"
DIR=USAF

## Make a directory to keep them in
if [ ! -d $DIR ]; then
	mkdir $DIR
fi
rm -f  $DIR/pop.txt $DIR/mort.txt

## Download
for CNT in $COUNTRIES; do
	curl -# -u webbs@demog.berkeley.edu:foobar \
		"http://www.mortality.org/hmd/${CNT}/STATS/Population5.txt"  \
		| gawk  -f hmd-refmt.awk -v ST=$ST -v FIN=$FIN -v MISS=0 -v SEX=$SEX \
		>> "$DIR/pop.txt"
	echo >> "$DIR/pop.txt"
	curl -# -u webbs@demog.berkeley.edu:foobar \
		"http://www.mortality.org/hmd/${CNT}/STATS/Mx_5x1.txt" \
		| gawk  -f hmd-refmt.awk -v ST=$ST -v FIN=$FIN -v MISS=9.9 -v SEX=$SEX \
		>> "$DIR/mort.txt"
	echo >> "$DIR/mort.txt"
done

echo "$COUNTRIES" > $DIR/labels.txt

#http://www.mortality.org/hmd/AUT/STATS/Population5.txt
#http://www.mortality.org/hmd/AUT/STATS/Mx_5x1.txt

## config for real application
: <<EOF
	ST=1956
	FIN=2006
	COUNTRIES="AUT CAN DNK FIN FRATNP DEUTFRG ITA JPN NLD NOR ESP SWE CHE GBR_NP USA"
	DIR=HMDSNARF
EOF
