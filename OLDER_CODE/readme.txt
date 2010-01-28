

1 Data

One matrix (time by age) of age-specific death rates (ASDR). The first row
of the matrix is the ASDR of the earliest time; ASDR is grouped by age as
0, 1-4, 5-9, 10-14, ., 80-84; age group 85+ will not be used. The second
row is the ASDR one year later than the first, and so on. The ASDR must be
continues over calendar years. The number of the historical calendar years
should be larger than three to produce nonzero variance for the random walk
model.

Example data: mxjapanfemale5094.txt, Japan female from 1950 to 1994.


Random number seed: ran_start.mat


2 Programs


mort.m - Input arguments (Data matrix, the latest yr of data, the first yr
of forecast, the length of forecast period (divided by 5), number of
trajectories)

    E.g., latest data 1993, first yr of forecast 1995, forecasting 60
    yrs, using 1000 trajectories: mort( Name of data matrix,
    1993,1995,12, 1000) Output: Forecasted ASDR in matrix (time,
    trajectory, age) Four pictures: a(x), b(x), k(t) and Eo


CoaleGt.m - To extend ASDR to age groups 85-89,., 100-104.

    The reason of not using Coale-Kisker is it deals with male and
    female, so for two-sex combined case it requires data of
    population.


Fiteo.m - To adjust k(t) from SVD to fit recorded Eo.

lfexpt.m - To calculate Eo for fiteo.m

Prctile.m - To give the value lower than which there are a given % of
trajectories.

Pict.m - To make data for pictures.