                                        # Tim Miller (tmiller@demog.berkeley.edu)
## May 23, 2001

## Mortality Forecast Module:
## Estimating and forecasting mortality by single
## year of age for both sexes combined using the Lee-Carter method
attach("~tmiller/lee1/historical.usa/Data",pos=1)

## Step 00: Create functions

lifetable.1mx <- function(nmx){
  ## Derive lifetable values from single year mortality rates
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

get.e0 <- function(x) {return(lifetable.1mx(x)[1])}

estimate.leecarter <- function(nmx){
  ## Using only mortality rate below age 85, estimate Lee-Carter
  ## parameter.  Input is matrix of mortality rates, rows are dates
  ## and columns are single years of age.
  nmx <- nmx[, 1:85]
  log.nmx <- log(nmx)
  ax <- apply(log.nmx, 2, mean)      # mean across columns of log.nmx
  swept.mx <- sweep(log.nmx, 2, ax)  # sweep() subtracts ax from log.nmx, across columns (from MARGIN=2).
                                        # I guess with "/" could use for dividing std
  svd.mx <- svd(swept.mx)
  
  bx <- svd.mx[, 1]/sum(svd.mx[, 1])  # I think this would give an error...
  kt <- svd.mx[1] * svd.mx[, 1] * sum(svd.mx[, 1])
  result <- list(ax = ax, bx = bx, kt = kt)
  return(result)
}

nmx.from.kt <- function (kt,ax,bx){
  ## Derives mortality rates from kt mortality index, 
  ##   per Lee-Carter method
  nmx.part1 <- exp((bx[1:85] * kt) + ax[1:85])

  ## Use modified Coale-Guo for mortality above age 85 
  nmx.part2 <- rep(0,26) 
  m83 <- nmx.part1[84]
  m84 <- nmx.part1[85]
  ##Set 1m105 based on 1m84 
  ## (where 0.421 is the average difference between 1m84 and 1m105 observed
  ##  in SSA data from 1975-1995).
  m105 <- 0.421 + m84
  k84 <- log(m84/m83)
  R <- - ( log(m83/m105) + ((105-83)*k84) ) / (sum(1:(105-84)))

  x <- seq(85,110)
  nmx.part2 <- m83 * exp ( ((x-83)*k84) + (R*cumsum(1:(x[26]-84))) )

  nmx <- c(nmx.part1, nmx.part2)
  nmx[nmx>1] <- 1
  nmx[nmx==0] <- 1
  return(nmx)
}

iterative.kt <- function (e0,ax,bx){
  ## Given e(0), search for mortality index k(t) per Lee-Carter method
  step.size <- 20
  guess.kt <- 0
  last.guess <- c("high")
  how.close <- 5
  while(abs(how.close)>.001){
    nmx <- nmx.from.lc(guess.kt,ax,bx)
    guess.e0 <- get.e0(nmx)
    how.close <- e0 - guess.e0
    if (how.close>0){
      ## our guess is too low and must decrease kt
      if (last.guess==c("low")) {
        step.size <- step.size/2
      }
      guess.kt <- guess.kt - step.size
      last.guess<- c("high")}
    if (how.close<0){
      ## our guess is too high and must increase kt
      if (last.guess==c("high")) {
        step.size <- step.size/2
      }
      guess.kt <- guess.kt + step.size
      last.guess <- c("low")}
  }
  return (guess.kt)
}

## Step 0:  Get the data

## From Berkeley Mortality Database read in mortality data
## by single year of age 0 to 119 from 1900 to 1995
us.mx.1900.1995 <- read.table("mx.1x1",header=T)
matrix.mx.1900.1995 <- matrix(0,96,120)
for (cnt in 1:96) {
  year <- 1899+cnt
  matrix.mx.1900.1995[cnt,] <- us.mx.1900.1995[us.mx.1900.1995==year]}
dimnames (matrix.mx.1900.1995) <- list(seq(1900,1995),
                                       seq(0,119))

## Add in latest data from SSA.  The data for 1996,1997,and 1998
## are final versions as used in the 2001 Trustees Report.
## ALSO USE THE 1999 PRELIMINARY DATA!
matrix.mx.1900.1999<- rbind(matrix.mx.1900.1995,
                            ssa.1996,
                            ssa.1997,
                            ssa.1998,
                            ssa.1999)
dimnames (matrix.mx.1900.1999) <- list(seq(1900,1999),
                                       seq(0,119))


## Get Life Tables for 1900 to 1995 by 1 year age group
##  from the Berkeley Mortality Database.
combined.ltab <- read.table("~tmiller/lee1/historical.usa/utper.lt.1x1",header=T)
## ex matrix
ex.matrix.1900.1999 <- matrix(0,100,120)
for (cnt in 1:96){
  year <- 1899+cnt
  ex.matrix.1900.1999[cnt,] <- combined.ltab[combined.ltab==year]}
ex.matrix.1900.1999[97,] <- ssa.1996
ex.matrix.1900.1999[98,] <- ssa.1997
ex.matrix.1900.1999[99,] <- ssa.1998
ex.matrix.1900.1999[100,] <- ssa.1999
dimnames (ex.matrix.1900.1999) <- list(seq(1900,1999),
                                       seq(0,119))


## Test life table function
test.e0.1900.1999 <- apply(matrix.mx.1900.1999,1,get.e0)
## This graph shows that the life table function returns the correct e(0)
## values.
plot (test.e0.1900.1999)
lines (ex.matrix.1900.1999[,1])

## There appears to be a significant difference between CDC and SSA estimate's
## of life expectancy.  Since I am using SSA mortality data for the estimation,
## I will also use SSA e(0) estimates.  But this bears further investigation.

## Step 1: Estimate Lee-Carter on the data set

model <- estimate.leecarter(matrix.mx.1900.1999[51:100,])

##Step 2:  Estimate second-stage kt from e0

end.year <- 1999
start.year <- 1950
len.series <- end.year - start.year + 1
kt.secondstage <- rep(0,len.series)
for (cnt in 1:len.series){
  kt.secondstage[cnt] <- iterative.kt(ex.matrix.1900.1999[(50+cnt),1],
                                      model,model)}

## Step 3, Time series estimation of kt as (0,1,0)

kt.diff <- diff(kt.secondstage)
model.kt <- summary(lm(kt.diff ~ 1  ))
kt.drift <- model.kt[1,1]
sec <- model.kt[1,2]
see <- model.kt

## Step 4: Forecast of kt and e(0) for 122 years
## Use mortality in last year (1999) as ax values
## for the forecast. 
mort.finalyear <- matrix.mx.1900.1999[100,]

## Set initial kt for 1999 (should be nearly zero)
kt.initial <- iterative.kt(ex.matrix.1900.1999[100,1],
                           log(mort.finalyear[1:85]),model)
kt.initial.male <- iterative.kt(ssa.1999[1],
                                log(ssa.1999[1:85]),model)
kt.initial.female <- iterative.kt(ssa.1999[1],
                                  log(ssa.1999[1:85]),model)

x <- seq(0,122)
kt.stderr <- ( (x*see^2) + (x*sec)^2 )^.5
kt.forecast <- kt.initial + (x * kt.drift)
kt.lo.forecast <- kt.forecast + (1.96*kt.stderr)
kt.hi.forecast <- kt.forecast - (1.96*kt.stderr)
## This gives 95% prob interval
## For 90%, us 1.645.

e0.forecast <- rep(0,122)
e0.lo.forecast <- rep(0,122)
e0.hi.forecast <- rep(0,122)
for (cnt in 1:122){
  e0.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.forecast[cnt],
                       log(mort.finalyear[1:85]), model))
  e0.lo.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.lo.forecast[cnt],
                       log(mort.finalyear[1:85]), model))
  e0.hi.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.hi.forecast[cnt],
                       log(mort.finalyear[1:85]), model))
}

## Forecast mortality of each sex.  I assume bx and rate of drift of
## kt are the same for both sexes.  Ax values and the starting value
## (and subsequent values) of kt mortality index are unique for each sex.
e0.male.forecast <- rep(0,122)
e0.female.forecast <- rep(0,122)
for (cnt in 1:122){
  e0.male.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.initial.male-kt.forecast[1]+kt.forecast[cnt],
                       log(ssa.1999[1:85]), model))
  e0.female.forecast[cnt] <-
    get.e0(nmx.from.lc(kt.initial.female-kt.forecast[1]+kt.forecast[cnt],
                       log(ssa.1999[1:85]), model))
}

## Test to see how closely the two-sex forecast matches the unisex forecast
## This graph shows these forecasts are extremely close to each other.
## The two-sex model shows slightly lower e(0) throughout.  By 2075,
## there is a difference of 0.2 years with the unisex forecast at 85.2 and
## the two-sex forecast at 85.0.
plot (seq(1999,2120),e0.forecast)
lines (seq(1999,2120), ((105/205)*e0.male.forecast) +
       ((100/205)*e0.female.forecast))
e0.combined.forecast <- ((105/205)*e0.male.forecast) +
  ((100/205)*e0.female.forecast)

e0.forecast[c(1999,2075)-1998]
e0.combined.forecast[c(1999,2075)-1998]
e0.lo.forecast[c(1999,2075)-1998]
e0.hi.forecast[c(1999,2075)-1998]

## In 2075, e(0) 95% prob interval = 81.2 to 88.4
## with median value of 84.9
## Compare to SSA 
((105/205)*c(77.4,80.9,85.2)) +
  ((100/205)*c(81.7,85.0,89.0))
##[1] 79.5 82.9 87.1

## write out ax, bx, kt.forecast, e0.forecasts,
##sec, see, kt.drift
##> kt.drift
##[1] -1.029377
##> sec
##[1] 0.1951575
##> see
##[1] 1.366102

##> kt.initial
##[1] 0.2001953
##> kt.initial.male
##[1] 0
##> kt.initial.female
##[1] 0.546875

mort.parameters <- cbind (log(ssa.1999[1:85]),
                          log(ssa.1999[1:85]),
                          log(ssa.1999[1:85]),
                          model)
e0.1999.2120 <- round(cbind(e0.forecast,e0.lo.forecast,e0.hi.forecast),3)

write.table (round(mort.parameters,5),"mort.parameters",sep=",")
write.table (e0.1999.2120,"e0.1999.2120",sep=",")

