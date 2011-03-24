
## Call like this: gawk  -f hmd.awk ST=1956 FIN=2000 MISS=0 hmdusa.txt

## Print the header, save for later
FNR == 1 {
	HEAD = $0
	print "##" HEAD
}

## Print each matching year, collecting rates into a an array and print out at 110+
$1 >= ST && $1 <= FIN && $1 !~ /-/ {
	sub (/^\.$/, $5, $MISS)
	if ($2 == "0") {
		ASFR = $5 
	} else if ($2 == "110+") {
		ASFR = ASFR "\t" $5
		gsub(/+/, "", $1) 
		print $1 "\t" ASFR
	} else {
		ASFR = ASFR "\t" $5
	}	
} 

## Print a header again
END {
}

