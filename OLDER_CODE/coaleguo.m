function [mx_extended,ages_extended] =  coaleguo (mx_data,mx_ages,age_close,value_close)  %-*-text-*-

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

nmax = 125; % final age to return

if (nargin ~= 4);
  error('coaleguo: bad number of arguments')
end

if(age_close == 0)			% use default
  age_close = 105;
end

iselneg = (mx_ages < 0);
if (sum(iselneg) ~= 1);
  disp('warning:  Coale-Guo without open age interval');
end;

% Coale-Kisker empiric observation is that the log(m[x]/m[x-5]) declines
% linearly for x beyond age 80.  
isel80 = mx_ages==80;
isel75 = mx_ages==75;

if ~(sum(isel80)==1 & sum(isel75)==1)
  error('Need values at both age 75,80 ');
end  
if (value_close == 0);
  % use Coale-Guo closeout assumption  
  value_close = 0.66 + mx_data(isel75);	
end
if rem(age_close,5) ~= 0 | age_close < 90;
  error('COALEGUO: closing age must be multiple of 5 and over age 90');
end
seqmx=  (1:length(mx_data));
n_extend = floor( (nmax - 80)/5);
addedages = 85:5:nmax;

m80 = mx_data(isel80);
m75 = mx_data(isel75);
[n,m]=size(mx_ages);
k80 = log( m80/m75 );

% A is the number of age groups from 80 to age_close
A = floor((age_close - 80)/5);

% generalization of C-G formula to have curve go through value_close at
% age_close; 
s = log(value_close/m80) - A*k80 ; 		% Used to be: A*k80 == k80 - (A-1)*k80
s = (-2*s) / (A*(A-1)) 					% was -s/( A*(A-1)/2 + A);

% change signs of last age to indicate open-ended
addedages(length(addedages))= -1* addedages(length(addedages));
addedmx = zeros(1, length(addedages));
tmp = m80*exp(k80 - s);
addedmx(1) = tmp;
tmpdiff = 0;

% care needed to make sure that rates to not drop after age_close.  This can
% happen when the cubic ends up peaking in the interval [age_close,nmax]. In
% that case, (where k80-i*s < 0) we continue at the same increment as before the peak.
for i=2:length(addedmx)
  tmpnew = tmp*exp(k80 - i*s);
  if( tmpnew < tmp);
    tmpnew = tmp + tmpdiff;
  end
      
  tmpdiff = tmpnew-tmp;
  tmp=tmpnew;
  addedmx(i)=tmp;
end

% max of entries is unity?  No, we dont restrict range of mx here but test
% for range of qx later.  This was causing some anomalies

% addedmx(addedmx>1) = 1+0*addedmx(addedmx>1);

% construct extended mx vector for return
mx_extended = [ mx_data(1: seqmx(isel80) ) addedmx ];
ages_extended = [ mx_ages(1: seqmx(isel80) ) addedages ] ;
