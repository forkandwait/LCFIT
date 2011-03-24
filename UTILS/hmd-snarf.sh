set -e 

## CONFIG VARIABLES
ST=1956
FIN=2006
COUNTRIES="AUT CAN DNK FIN FRATNP DEUTFRG ITA JPN NLD NOR ESP SWE CHE GBR_NP USA"
DIR=HMDSNARF
USERPASS="myusername:mypassword"


## PROGRAM CODE
if [ ! -d $DIR ]; then
	mkdir $DIR
fi
rm -f  $DIR/pop.txt $DIR/mort.txt

for CNT in $COUNTRIES; do
	curl -u $USERPASS \
		"http://www.mortality.org/hmd/${CNT}/STATS/Population5.txt"  \
		| gawk  -f hmd-refmt.awk ST=$ST FIN=$FIN MISS=0\
		>> "$DIR/pop.txt"
	echo >> "$DIR/pop.txt"
	curl -u $USERPASS \
		"http://www.mortality.org/hmd/${CNT}/STATS/Mx_5x1.txt" \
		| gawk  -f hmd-refmt.awk ST=$ST FIN=$FIN MISS=9.9 \
		>> "$DIR/mort.txt"
	echo >> "$DIR/mort.txt"
done

#http://www.mortality.org/hmd/AUT/STATS/Population5.txt
#http://www.mortality.org/hmd/AUT/STATS/Mx_5x1.txt
