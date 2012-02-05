
## Call like this: gawk  -f hmd-refmt.awk -v ST=1956 -v FIN=2000 -v MISS=0 -v SEX=M|F|T hmdusa.txt

BEGIN {
	if (SEX == "F")
		SEXVAR = 3
	else if (SEX == "M")
		SEXVAR = 4
	else 
		SEXVAR = 5
}

## Print the header, save for later
FNR == 1 {
	MISS = 0
	HEAD = $0
	print "##" HEAD
}

## Print each matching year, collecting rates into a an array and print out at 110+
$1 >= ST && $1 <= FIN && $1 !~ /-/ {
	if ($SEXVAR == ".")
		$SEXVAR = 1.0009
	if ($2 == "0") {
		ASFR = $SEXVAR 
	} else if ($2 == "110+") {
		gsub(/+/, " ", $1) 
		ASFR = ASFR " \t" $SEXVAR 
		print  ASFR " \t# " $1
	} else {
		ASFR = ASFR " \t" $SEXVAR
	}	
} 

## Print a header again
END {
}

