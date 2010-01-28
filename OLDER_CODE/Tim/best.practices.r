# This file is best.practices.r
# Tim Miller, March 2, 2001.

# Estimating and forecasting mortality by single
# year of age for both sexes combined using the Lee-Carter method

# Step 00: Create functions

# Life table derives from mortality rates

lifetable.1mx <- function(nmx){
        n <- 1
	len.m <- length(nmx) - 1
	age <- seq(0, len.m)
        a0 <- 0.07 + (1.7*nmx[1]) # per Keyfitz
	nax <- c(a0, rep(0.5, len.m) )
        nqx <- (n * nmx)/(1 + ((n-nax) * nmx))
	nqx[nqx > 1] <- 1
        lx<- c(1,cumprod(1-nqx[1:len.m]))
	ndx <- -diff(c(lx,0))
        nLx <- (lx * n) - (ndx * (n - nax))
	Tx <- rev(cumsum(rev(nLx)))
	ex <- Tx/lx
	result <- data.frame(age = age, nqx = nqx, lx = lx, ndx = ndx,
                nLx = nLx, Tx = Tx, ex = ex)
	return(result)
}

get.e0 <- function(x) {return(lifetable.1mx(x)$ex[1])}

estimate.leecarter <- function(nmx){
        # Use only mortality below age 85
	nmx <- nmx[, 1:85]
	log.nmx <- log(nmx)
	ax <- apply(log.nmx, 2, mean)
	swept.mx <- sweep(log.nmx, 2, ax)
	svd.mx <- svd(swept.mx)
	bx <- svd.mx$v[, 1]/sum(svd.mx$v[, 1])
	kt <- svd.mx$d[1] * svd.mx$u[, 1] * sum(svd.mx$v[, 1])
	result <- list(ax = ax, bx = bx, kt = kt)
	return(result)
}

nmx.from.lc <- function (kt,ax,bx){
        # ages 0 to 84
        nmx.part1 <- exp((bx * kt) + ax)
        # ages 85 to 119 based on modified Coale-Guo
        # Need a better method!  This is temporary.
        nmx.part2 <- rep(0,35)
        m83 <- nmx.part1[84]
        m84 <- nmx.part1[85]
        #Set 1m105 based on 1m84 (average value for last 20 years)
        m105 <- 0.421 + m84
        #Estimate k84 
        k84 <- log(m84/m83)
        # solve for R
        R <- - ( log(m83/m105) + ((105-83)*k84) ) / (sum(seq(1,(105-84))))
        x <- seq(85,119)
        for (cnt in 1:35){
        nmx.part2[cnt] <- m83 * 
         exp (((x[cnt]-83)*k84) + (R*sum(seq(1,(x[cnt]-84)))))
        }
	nmx <- c(nmx.part1, nmx.part2)
        return (nmx)}

# Find kt given e(0) via iterative search
find.kt <- function (e0,ax,bx){
        step.size <- 20
        guess.kt <- 0
        last.guess <- c("high")
        while(abs(how.close)>.001){
        nmx <- nmx.from.lc(guess.kt,ax,bx)
	guess.e0 <- get.e0(nmx)
        how.close <- e0 - guess.e0
        if (how.close>0){
        # our guess is too low and must decrease kt
          if (last.guess==c("low")) {step.size <- step.size/2}
          guess.kt <- guess.kt - step.size
          last.guess<- c("high")}
        if (how.close<0){
        # our guess is too high and must increase kt
          if (last.guess==c("high")) {step.size <- step.size/2}
          guess.kt <- guess.kt + step.size
          last.guess <- c("low")}
      }
        return (guess.kt)}

# Step 0:  Get the data

# From Berkeley Mortality Database read in mortality data
# by single year of age 0 to 119 from 1900 to 1995

us.mx.1900.1995 <- read.table("mx.1x1",header=T)

matrix.mx.1900.1995 <- matrix(0,96,120)
for (cnt in 1:96) {
year <- 1899+cnt
matrix.mx.1900.1995[cnt,] <- us.mx.1900.1995$Total[us.mx.1900.1995$Year==year]}

dimnames (matrix.mx.1900.1995) <- list(seq(1900,1995),
  seq(0,119))


# Get Life Tables for 1900 to 1995 by 1 year age group
# Also from the Berkeley Mortality Database

combined.ltab <- read.table("utper.lt.1x1",header=T)

# ex matrix
ex.matrix.1900.1995 <- matrix(0,96,120)
for (cnt in 1:96){
year <- 1899+cnt
ex.matrix.1900.1995[cnt,] <- combined.ltab$ex[combined.ltab$Year==year]}

dimnames (ex.matrix.1900.1995) <- list(seq(1900,1995),
  seq(0,119))


# Test life table function
test.e0.1900.1995 <- apply(matrix.mx.1900.1995,1,get.e0)
# This graph shows that the life table function returns the correct e(0)
# values.
plot (test.e0.1900.1995)
lines (ex.matrix.1900.1995[,1])



# Step 1: Estimate Lee-Carter on the data set

model <- estimate.leecarter(matrix.mx.1900.1995[51:96,])

#Step 2:  Estimate second-stage kt from e0

end.year <- 1995
start.year <- 1950
len.series <- end.year - start.year + 1
kt.secondstage <- rep(0,len.series)

for (cnt in 1:len.series){
kt.secondstage[cnt] <- find.kt(ex.matrix.1900.1995[(cnt+50),1],
   model$ax,model$bx)}
  
# Step 3, Time series estimation of kt as (0,1,0)

kt.diff <- diff(kt.secondstage)
model.kt <- summary(lm(kt.diff ~ 1  ))
kt.drift <- model.kt$coefficients[1,1]
sec <- model.kt$coefficients[1,2]
see <- model.kt$sigma

# Step 4: Forecast of kt and e(0) for 106 years
horizon <- 106
x <- seq(0,horizon)
kt.stderr <- ( (x*see^2) + (x*sec)^2 )^.5
kt.forecast <- x * kt.drift
kt.lo.forecast <- kt.forecast + (1.96*kt.stderr)
kt.hi.forecast <- kt.forecast - (1.96*kt.stderr)
# This gives 95% prob interval
# For 90%, us 1.645.

e0.forecast <- rep(0,horizon)
e0.lo.forecast <- rep(0,horizon)
e0.hi.forecast <- rep(0,horizon)

# Use mortality in last year (1995) as ax values
# for the forecast. 
mort.finalyear <- matrix.mx.1900.1995[96,]

for (cnt in 1:horizon){
e0.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.forecast[cnt],
     log(mort.finalyear[1:85]), model$bx))
e0.lo.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.lo.forecast[cnt],
     log(mort.finalyear[1:85]), model$bx))
e0.hi.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.hi.forecast[cnt],
     log(mort.finalyear[1:85]), model$bx))
}


# Step 5:  Summary of results and parameter values

# Table of values
cbind(seq(1995,2100,5),
      e0.lo.forecast[seq(1,106,5)],
      e0.forecast[seq(1,106,5)],
      e0.hi.forecast[seq(1,106,5)])

 [1,] 1995 75.71153 75.71153 75.71153
 [2,] 2000 75.55084 76.38041 77.18527
 [3,] 2005 75.82375 77.03314 78.19238
 [4,] 2010 76.15085 77.67100 79.11500
 [5,] 2015 76.49933 78.29508 79.98811
 [6,] 2020 76.85752 78.90633 80.82515
 [7,] 2025 77.21998 79.50552 81.63296
 [8,] 2030 77.58381 80.09335 82.41554
 [9,] 2035 77.94731 80.67036 83.17543
[10,] 2040 78.30947 81.23702 83.91433
[11,] 2045 78.66963 81.79373 84.63338
[12,] 2050 79.02737 82.34078 85.33340
[13,] 2055 79.38243 82.87844 86.01496
[14,] 2060 79.73462 83.40690 86.67844
[15,] 2065 80.08382 83.92633 87.32416
[16,] 2070 80.42998 84.43685 87.95234
[17,] 2075 80.77304 84.93856 88.56315
[18,] 2080 81.11298 85.43152 89.15675
[19,] 2085 81.44979 85.91578 89.73329
[20,] 2090 81.78346 86.39139 90.29290
[21,] 2095 82.11399 86.85837 90.83574
[22,] 2100 82.44139 87.31674 91.36198

# kt values: Initial and secondstage
cbind (seq(1950,1995),model$kt,kt.secondstage)
 [1,] 1950  23.304792     21.6796875
 [2,] 1951  22.954642     20.9960938
 [3,] 1952  22.388955     20.0244141
 [4,] 1953  19.700963     18.5156250
 [5,] 1954  15.230916     14.5703125
 [6,] 1955  14.265605     14.4335938
 [7,] 1956  13.367475     14.0527344
 [8,] 1957  14.657197     15.3417969
 [9,] 1958  13.070658     14.0625000
[10,] 1959  12.484251     13.0761719
[11,] 1960  12.513303     13.4375000
[12,] 1961   9.834913     11.2695312
[13,] 1962  10.306161     12.0703125
[14,] 1963  10.878068     13.0126953
[15,] 1964  10.097458     11.5869141
[16,] 1965   9.664103     11.4062500
[17,] 1966  10.168152     11.5869141
[18,] 1967   8.642883      9.7509766
[19,] 1968  10.188404     10.9228516
[20,] 1969   9.112819      9.0625000
[21,] 1970   7.696256      7.6025391
[22,] 1971   6.516393      6.2890625
[23,] 1972   5.962244      5.7421875
[24,] 1973   5.141341      4.4531250
[25,] 1974   1.521833      0.8496094
[26,] 1975  -1.528150     -2.2265625
[27,] 1976  -3.435031     -3.9453125
[28,] 1977  -4.856113     -6.1523438
[29,] 1978  -5.756396     -6.9531250
[30,] 1979  -8.187735     -9.6972656
[31,] 1980  -8.565745     -9.0429688
[32,] 1981 -10.709373    -11.5332031
[33,] 1982 -13.220772    -14.2187500
[34,] 1983 -14.814280    -14.2578125
[35,] 1984 -15.766258    -15.0390625
[36,] 1985 -16.098203    -15.0390625
[37,] 1986 -16.204167    -15.6250000
[38,] 1987 -16.675085    -16.4990234
[39,] 1988 -16.519651    -15.9375000
[40,] 1989 -17.713306    -17.9492188
[41,] 1990 -20.133870    -19.6875000
[42,] 1991 -20.640046    -20.7617188
[43,] 1992 -22.557741    -22.1875000
[44,] 1993 -21.032213    -20.5566406
[45,] 1994 -22.339841    -21.6406250
[46,] 1995 -22.915804    -22.2363281

# Lee-Carter Parameters
# ax, log(mort.finalyear), bx for ages 0 to 84

cbind (seq(0,84),model$ax,log(mort.finalyear[1:85]),model$bx)
   [,1]      [,2]      [,3]        [,4]
0     0 -4.082499 -4.879607 0.030399448
1     1 -6.745133 -7.393888 0.026627577
2     2 -7.183973 -7.804243 0.023764971
3     3 -7.446738 -8.069307 0.024261971
4     4 -7.637021 -8.247166 0.024527989
5     5 -7.758693 -8.412833 0.024351930
6     6 -7.849287 -8.458924 0.023108389
7     7 -7.934766 -8.532307 0.022514609
8     8 -8.035887 -8.611504 0.022791567
9     9 -8.143423 -8.697517 0.023538728
10   10 -8.239521 -8.791630 0.025088781
11   11 -8.242313 -8.759265 0.024794559
12   12 -8.077892 -8.482792 0.020457001
13   13 -7.791994 -8.069307 0.014525004
14   14 -7.501817 -7.717436 0.010192864
15   15 -7.252704 -7.406982 0.007291073
16   16 -7.066068 -7.203470 0.005590303
17   17 -6.928299 -7.057416 0.004944703
18   18 -6.841996 -6.977105 0.005184927
19   19 -6.787192 -6.949619 0.005772051
20   20 -6.734575 -6.916796 0.006546056
21   21 -6.685564 -6.885994 0.007075405
22   22 -6.653481 -6.859918 0.007252730
23   23 -6.642817 -6.835435 0.006988564
24   24 -6.646024 -6.819744 0.006299687
25   25 -6.654444 -6.809722 0.005676988
26   26 -6.657340 -6.789972 0.005153541
27   27 -6.650091 -6.753319 0.004728458
28   28 -6.627567 -6.700741 0.004520552
29   29 -6.591093 -6.634679 0.004439631
30   30 -6.549966 -6.562040 0.004474250
31   31 -6.505978 -6.500292 0.004688362
32   32 -6.456637 -6.439002 0.005024263
33   33 -6.403052 -6.384211 0.005493004
34   34 -6.344376 -6.337341 0.006134751
35   35 -6.280209 -6.287179 0.006754587
36   36 -6.211095 -6.231246 0.007409183
37   37 -6.138312 -6.182625 0.008281441
38   38 -6.063771 -6.126597 0.009175527
39   39 -5.986160 -6.070941 0.010145054
40   40 -5.905267 -6.013301 0.011100571
41   41 -5.822082 -5.952629 0.011894539
42   42 -5.737275 -5.896882 0.012478709
43   43 -5.651624 -5.839946 0.012881713
44   44 -5.564846 -5.784125 0.013098793
45   45 -5.477518 -5.725721 0.013243713
46   46 -5.388728 -5.662161 0.013351681
47   47 -5.298410 -5.590543 0.013455955
48   48 -5.206982 -5.513245 0.013639813
49   49 -5.115074 -5.428654 0.013756987
50   50 -5.022345 -5.344990 0.013884991
51   51 -4.931064 -5.257175 0.013859479
52   52 -4.843774 -5.172390 0.013682556
53   53 -4.760737 -5.088543 0.013302344
54   54 -4.680325 -5.008188 0.012850745
55   55 -4.599809 -4.923037 0.012340799
56   56 -4.517618 -4.835087 0.011888923
57   57 -4.433707 -4.747310 0.011591335
58   58 -4.347714 -4.656674 0.011443224
59   59 -4.260996 -4.565661 0.011390819
60   60 -4.173956 -4.475810 0.011367450
61   61 -4.088262 -4.385392 0.011266640
62   62 -4.005367 -4.291674 0.010989053
63   63 -3.925538 -4.195381 0.010532918
64   64 -3.847654 -4.099015 0.010001636
65   65 -3.768164 -4.000472 0.009501726
66   66 -3.687688 -3.906588 0.009139773
67   67 -3.609358 -3.822319 0.008941275
68   68 -3.533153 -3.748078 0.008916365
69   69 -3.457544 -3.679523 0.009009889
70   70 -3.379538 -3.607705 0.009121829
71   71 -3.298935 -3.530885 0.009227024
72   72 -3.216858 -3.450966 0.009342964
73   73 -3.133706 -3.367869 0.009484877
74   74 -3.049290 -3.281896 0.009626375
75   75 -2.963163 -3.192599 0.009726577
76   76 -2.875602 -3.101560 0.009814721
77   77 -2.787279 -3.010501 0.009962578
78   78 -2.698498 -2.920365 0.010170804
79   79 -2.609441 -2.829879 0.010376758
80   80 -2.519904 -2.737639 0.010540875
81   81 -2.430161 -2.643485 0.010609231
82   82 -2.340486 -2.547872 0.010569831
83   83 -2.251030 -2.451572 0.010423963
84   84 -2.162010 -2.354784 0.010206697
