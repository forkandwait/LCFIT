function [eoh,eof,drft,sdgkt]=multicountry2GC(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt) % -*-matlab-*-
% This function returns empirical e_0, projected e_0, and the drift and stdev of Kt
%
% Parameters:  
%   Bx -- bx from collective rates 
%   Kt -- kt from collect rates
%   mx -- ASDR for specific country in 5 year intervals (?)
%   rndgk --  vector of random numbers, ~N(0,1).  Set, for example, group1s.m
%   nfor -- number of time to be forecasted,
%   ntrj -- number of trajectories,
%   nfor5 -- number of time to be forecasted in 5-yr interval,
%   nspt -- different bewteen first year of forscast in 5-yr and the last hist data 
%   ("nag" is usually number of ages)
%
% Output:
%   eoh --  vector of e_0 at each year from empirical sample
%   eof -- 3 x Y array of e0's, where rows are vector of e0 per year, 5%, 50%, and 95% spread in
%      the column 
%   drft -- drift from Kt 
%   sdgkt -- stdev from diffed Kt

xxx=size(mx);
nht=xxx(1);							% number of years

% Coale-Guo the mx's, put result in mxt, save life expectancy in eoh
for i=1:nht
  for j=1:18;
	drt(j)=mx(i,j);
  end     
  mxt(i,:)=CoaleGt(drt);
  eoh(i)=lfexpt(mxt(i,:));
end

xxx=size(mxt);
nag=xxx(2)

%(4) Estimating drift and sdgkt for the Random Walk w Drift RWD of group
dKt=diff(Kt);
drft=mean(dKt); 
sdgkt=sqrt(cov(dKt));
%End (4)

%(6)Forcasting
%End (6.1)
% (6.2) Generate stochastic trajectories of Kt
stokg=zeros(ntrj,nfor+1);
stokg(:,1)=Kt(nht);  %This holds the simulation of group Kt, using RWD
for tind =1:ntrj,
  for yind0=1:nfor, % Do innovations.  (was "Single yr forecast for handle AR(1) simplier")
	stokg(tind,yind0+1)=stokg(tind,1)+yind0*drft+(yind0+yind0^2/nht)^.5*sdgkt*rndgk(tind,yind0);%RWD
  end
end
%End(6.2)

% (6.3)
% The following creates a matrix of mx using the above Kt and Bx,
% as well as smushing it all into 5 year intervals and making sure
% the mx is small enough to insure there won't appear q>1
mxf=zeros(ntrj,nfor5,nag);
for tt=1:nfor5
  tto=nspt+5*(tt-1);
  for tind=1:ntrj
	for j=1:nag   
	  mxf(tind,tt,j)=mxt(nht,j)*exp((stokg(tind,tto)-stokg(tind,1))*Bx(j));    
	end
	if mxf(tind,tt,1)>0.78;				% at age 0 or 110?
	  mxf(tind,tt,1)=0.78;
	end; %keep q<1
	if mxf(tind,tt,2)>0.66;				% at age 105?
	  mxf(tind,tt,2)=0.66;
	end;
	for i=3:3;
	  if mxf(tind,tt,i)>0.4;			% at age what?
		mxf(tind,tt,i)=0.39;  
	  end;
	end;
  end;
end;
%End (6.3)

%End(6)

%(7) Forecasted Eo  
[e9750,e500,e250]=pictG(mxf);

eof(1,:)=e9750;
eof(2,:)=e500;
eof(3,:)=e250;

%mxo(1:ntrj)=mxf(:,nfor5,1);mean(mxo)
%Male ASDR(0) at 2100,1.0372e-004
%Female ASDR(0) at 2100,8.9978e-005
%Ratio of M/F=1.15
%Male ASDR(0) at 2002,0.0036
%Female ASDR(0) at 2002,0.0031
%Ratio of M/F=1.16


%Male ASDR(40-44) at 2002,0.0015
%Female ASDR(40-44) at 2002,8.7100e-004
%Ratio of M/F =1.72
