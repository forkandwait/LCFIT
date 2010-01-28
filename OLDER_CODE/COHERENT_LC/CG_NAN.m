function [nmx, mx]= CG_NAN(drt)
% CoaleGt
%
% Input: "drt" 18 age-specific death rates for 0, 1-4, 5-9,...80-84. (1, 2, 3, ..., 18) 
%
% Output: "nmx" 22 age-specific death rates for 0, 1-4, 5-9,...100-104. Also returning single year for info
%
% Note: We get lx, Lx for 0,...80-84; using Lifetable(mx_ages, mx_data)

A=110;    % closing age

%Here is CG for 1-yr mx(i), i=85,86,....,A;
[drt(18), drt(17)];
k85=.2*log(drt(18)/drt(17));             % ".2" because only want a single year from five year data
m84=drt(18)*exp(3*k85);         		% XXX 5_m_85 = 1*k85 + 2*k85 + 5_m_75.  would be drt(19)?
mA=0.66+drt(17);           				% inf_m_110.

% The coale-guo thing itself.  Fills a single year matrix (indexed by HA).
HA=A-85+1;								% Number of indexes until close.  110-85+1 = 26
cntAddends = (HA*(HA-1))/2;              % like the (A*(A+1))/2 form, but off by one (1,0), (2,1), (3,3), (4,6) ..
sNum = log(mA) - log(m84) - HA*k85;
s = sNum / cntAddends;                    % s =(log(mA/m84)-HA*k85)*2/(HA*(HA-1))

log(mA);
for i=1:HA                              % Each element in the matrix.  Boe does this recursively by using an updated tmp
   mx(i) = m84*exp(i*k85+s*i*(i-1)/2);
   [i,k85,s];
end

mx5year = mean(reshape(mx(2:end), 5, []));                 % Check mx for reasonableness

% Create 1-year life table so that later we can recompute the 5_m_x from lx and nLx
% Get 1-yr q(i) ....
for i=1:HA; % 85,86,...,125,
   %q(i)=2*mx(i)/(2+mx(i));
   q(i)=1-exp(-(mx(i) + .008*(mx(i)^2)));
end

% ... 1-yr lx(i) ...
lx(1)=1; %1 means 85
for i=1:HA; % lx, 85,86,...,125,126
   lx(i+1)=lx(i)*(1-q(i));
end

% ... 5-yr lx and nLx.  Looping over the 1-yr lx, taking avg, summing the five 1-yr averages ...
HB=(HA-1)/5; % the max age of 5-yr
nlx(1)=1;
for i=1:HB; % nLx:  85, 90, ..., 120
   ki1=1+5*(i-1);
   ki2=i;
   nLx(ki2)=0;
   for j=ki1:ki1+4
      nLx(ki2)=nLx(ki2)+0.5*(lx(j)+lx(j+1));
   end
   nlx(ki2+1)=lx(ki1+5);    % I think this gives l_80, l_85, etc.  Offset by 1 because he is starting at 79
end 

% ... 5-yr mx, fill out the rest and finis.
for i=1:18
   nmx(i)=drt(i);
end
for i=19:23 
   nmx(i)=(nlx(i-18)-nlx(i-17))/nLx(i-18);
end
nmx(24)=mx(HA); % the last open interval
nmx
%FINIS
