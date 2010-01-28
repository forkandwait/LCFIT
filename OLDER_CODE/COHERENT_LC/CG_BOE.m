function [mx_extended,ages_extended] =  CG_BOE (mx_data,mx_ages,age_close,value_close)
% COALEGUO 
% version for 5 year age-groups

% Coale-Guo procedure using raw mx values.  Extends the raw death
%       rates to higher ages assuming empirically derived sub-Gompertz
%       hazard increase

% New mx values are extended out to 5M125

% Based on Ron Lee Gauss program and Coale and Gurang Guo, pp.613-643.
% l80k corresponds to k80 in Coale  article; it is log(m8085k/m7579k).

%      mx_data, raw mx values;
%      mx_ages, lower bound of age intervals covered by mx_data; the last age
%         group is open ended, as indicated by a negative value;
%      age_close: close out age.  Defaults to 105
%      value_close: value of 5Mx at x=age_close.  Defaults to Coale-Guo
%         assumption that x=105 and value_close = 0.66+ 5M80


% open age interval corresponds to negative age entry

nmax = 110; % final age to return, was 125

if (nargin ~= 4);
  error('coaleguo: bad number of arguments')
end

if(age_close == 0)                      % use default
  age_close = 105;
end

% Check to see if there is an age that is negative (eg 110).  This is the open age interval.
iselneg = (mx_ages < 0);
if (sum(iselneg) ~= 1);
  disp('warning:  Coale-Guo without open age interval');
end;

% Coale-Kisker empiric observation is that the log(m[x]/m[x-5]) declines
% linearly for x beyond age 80.  In this code diff(diff(log(mx))) is constant except after nmax.  It isn't in Nan's

isel80 = mx_ages==80;
isel75 = mx_ages==75;

if ~(sum(isel80)==1 & sum(isel75)==1)
  error('Need values at both age 75,80 ');
end  

m80 = mx_data(isel80);
m75 = mx_data(isel75);

[n,m]=size(mx_ages);

k80 = log( m80/m75 );

if (value_close == 0);
  % use Coale-Guo closeout assumption  
  value_close = 0.66 + mx_data(isel75);
end

if rem(age_close,5) ~= 0 | age_close < 90;
  error('COALEGUO: closing age must be multiple of 5 and over age 90');
end

% A is the number of age groups from 80 to age_close
A = floor((age_close - 80)/5);

% C-G with curve go through value_close at
% age_close ... 

% ... infrastructure ....
seqmx = (1:length(mx_data));
n_extend = floor( (nmax - 80)/5);
addedages = 85:5:nmax;
addedages(length(addedages))= -1* addedages(length(addedages)); % change signs of last age to indicate open-ended
addedmx = zeros(1, length(addedages));

% ... CG "s" ....
s = log(value_close) - log(m80) - A*k80;
cntAddends = (A*(A+1))/2;                  % Was some strange formula before
s = -s/cntAddends;

% Get ready for loop to fill mx
tmp = m80*exp(k80 - s);                 % Use this to recurse
addedmx(1) = tmp;
tmpdiff = 0;
for i=2:length(addedmx)
  % Get mx from k80 and s ...
  tmpnew = tmp*exp(k80 - i*s); % This is funky, because the lim (...) = tmp, so thus we must
                               % compensate later.  Funky, but still the official 
                               % algorithm. Remember k80 = log(m80/m75), so
  
  % ... update, check for peak, adjust tmpnew if necessary.  Make sure that rates to not drop after
  % age_close: this can happen when the cubic ends up peaking in the interval [age_close,nmax]; in
  % that case, (where k80-i*s < 0) we continue at the same increment as before the peak....
  if( tmpnew < tmp);
    tmpnew = tmp + tmpdiff;
  end      
  tmpdiff = tmpnew-tmp;

  % ... set tmp for next round ...
  tmp=tmpnew;     

  % ... finis on this mx.
  addedmx(i)=tmp;
end

% max of entries is unity?  No, we dont restrict range of mx here but test
% for range of qx later.  This was causing some anomalies

% addedmx(addedmx>1) = 1+0*addedmx(addedmx>1);

% construct extended mx vector for return
mx_extended = [ mx_data(1: seqmx(isel80) ) addedmx ]; % Concatenation of vectors in matlab
ages_extended = [ mx_ages(1: seqmx(isel80) ) addedages ] ;