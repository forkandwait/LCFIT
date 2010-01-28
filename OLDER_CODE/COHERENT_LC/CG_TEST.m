function [stuff, headings, singleYrmx] = CG_TEST
% Returns swedish rates, and hopefully they match the python version

mxTest1 = [0.007188 0.000388 0.000251 ... % 0-1, 1-4, 5-9
		   0.000259 0.000437 0.000354 ... % 10-14, 15-19, 20-24
		   0.00052 0.000723 0.000981 ... % 25-29, 30-34, 35-39
		   0.001674 0.002619 0.003882 ... % 40-44, 45-49, 50-54
		   0.005682 0.008934 0.015387 ... % 55-59, 60-64, 65-69
		   0.027273 0.051968 0.090435 ... % 70-74, 75-79, 80-84
		   0.152816 0.233434 0.359285 ... % 85-89, 90-94, 95-99
		   0.502831 1.142857 1.0];		% 100-104, 105-109, 110+

agesTo105 = [0, 1, 5:5:105, -110];		% Open age interval?
agesTo80 = [0,1,5:5:80];

% "mx_rates" = sweden rates to 105, "mx_ages" = sweden ages to 105 / close, "age_close" = 105, "value_close" = default 
[rates_boe,ages] = CG_BOE(mxTest1, agesTo105, 110, 0); % rates, ages, age_close, value_close
[rates_nan,singleYrmx] = CG_NAN(mxTest1);

hold on
plot(log(mxTest1))
plot(log(rates_boe), '--')
plot(log(rates_nan), '-.')
legend('raw', 'boe', 'nan', 'Location', 'NorthWest')
print -dpng foo
hold off

stuff =[ages', log(mxTest1)', log(rates_boe)', log(rates_nan)'];
headings = [' ages ', ' rates_raw ', ' rates_boe ', ' rates_nan'];