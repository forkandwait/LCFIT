function [eoh,eof,drft,sdgkt,a0,a1,sdckt]=multicountry2GCS(Bx,Kt,mx,rndgk,nfor,ntrj,nfor5,nspt); %-*-matlab-*-
%
% RW (combined kt) and AR1 (residual kt) estimation and simulation,
% yielding model coefficients and percentile life expects
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
%   eoh -- empirical e0 after CG
%   eof -- e0s at percentiles 2.5% 50% 97.5% 
%   drft -- drift of kt for mx
%   sdgkt -- stderr from diffed Kt
%   a0 -- first AR(1) coefficient
%   a1 -- second AR(1) coefficient
%   sdckt -- standard error for AR(1) in totality.  
%				I would say "STDERR of Equation", but I am not sure if this is correct.

xxx=size(mx);nht=xxx(1);

% Caole-Guo
for i=1:nht
  for j=1:18;
	drt(j)=mx(i,j);
  end     
  mxt(i,:)=CoaleGt(drt);
  eoh(i)=lfexpt(mxt(i,:));
end

xxx=size(mxt);
nag=xxx(2);

% Find residuals
lnmx = log(mxt);
ax= mean(lnmx);
for ix = 1:nht,
  for j=1:nag
	lnmx1(ix,j) = lnmx(ix,j)-ax(j)-Bx(j)*Kt(ix);
  end
end
% SVD of the residuals
[U S V] = svd(lnmx1,0);
bx = V(:,1)/sum(V(:,1));
kt= S(1,1)*U(:,1)*sum(V(:,1));

% Estimating drift and sdgkt for the RWD of group ("Kt" is passed
% in as a parameter).
dKt=diff(Kt);
drft=mean(dKt); 
sdgkt=sqrt(cov(dKt));

% Estimate a0, a1, sdckt of kt of residuals using AR(1) model (k(t)=a0+a1*k(t-1)+sdckt*e(t))
for i=1:nht-1
  X(i,2)=kt(i);X(i,1)=1;y(i)=kt(i+1);    
end
%OLS
b(1)=sum(y);b(2)=y*X(:,2);
a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
xxx=(a^-1)*b';
a0=xxx(1);a1=xxx(2);a00=mean(y);

% one-step forecasts
ktm(1)=kt(1);
for i=2:nht
  ktm(i)=a0+a1*ktm(i-1);
end

% residuals from one-step forecasts
for i=1:nht    
  e(i)=kt(i)-ktm(i);				
  e0(i)=kt(i)-mean(kt);
end
sdckt=sqrt(cov(e));
Rsq=1-cov(e)/cov(e0);%R^2

%Estimating SDERR of a0 and a1.
sda0=sdckt/sqrt((nht-1));
sda1=sdckt/sqrt((kt'*kt));              
%End (5)

%(6)Forcsting

% (6.2) Generate stochastic trajectories of Kt and ktc: make matrices
% of random numbers ~ N(0,1) for combined kt and residuals
randn('state',1);
rndgc=randn(ntrj,nfor);                 % comb kt
randn('state',2);
rndgce=randn(ntrj,nfor);                % residuals

% set up empty matrix and initialize first element with last empirical kt
stokg=zeros(ntrj,nfor+1);
stokg(:,1)=Kt(nht);
stokc=zeros(ntrj,nfor+1);
stokc(:,1)=kt(nht);

% Do simulation on parallell Kt and kt (combined and residual)
for tind =1:ntrj,						% Fill each run
  for yind0=1:nfor,						% Fill each year
		
	%% RWD on combined Kt
	stokg(tind,yind0+1)=stokg(tind,1) + yind0*drft + (yind0+yind0^2/nht)^.5*sdgkt*rndgk(tind,yind0);

	% AR(1) on residuals  
	zzz=(a0+sda0*rndgce(tind,yind0))+(a1+sda1*rndgce(tind,yind0))*stokc(tind,yind0);
	stokc(tind,yind0+1)=zzz+sdckt*rndgc(tind,yind0);   
  end
end
%End(6.2)

%(6.3) calculate mx from simulated Kt (RW, "stokg") and simulate Kt
%residuals (AR1, "stokc").  Fix high mx's to keep qx <= 1.0.  "mxt"
%is the log of the input empirical death rates; being used like ax
%here, methinks.  The result -- "mxf" -- is used to generate
%percentiles of life expectancy.
mxf=zeros(ntrj,nfor5,nag);
for tt=1:nfor5
  tto=nspt+5*(tt-1);
  for tind=1:ntrj
	for j=1:nag   
	  mxf(tind,tt,j)=mxt(nht,j)*exp((stokg(tind,tto) - stokg(tind, 1))*Bx(j) ...
                                    +(stokc(tind,tto)-stokc(tind,1))*bx(j)); % XXX -- mxt like Ax -- weird!
	end
	if mxf(tind,tt,1)>0.78;mxf(tind,tt,1)=0.78;end;%keep q<1
	if mxf(tind,tt,2)>0.66;mxf(tind,tt,2)=0.66;end;
	for i=3:3;if mxf(tind,tt,i)>0.4;mxf(tind,tt,i)=0.39;end;end;
  end
end

%End(6.3)
%(7) Forecasted Eo  
[e9750,e500,e250]=pictG(mxf);%kt
eof(1,:)=e9750;
eof(2,:)=e500;
eof(3,:)=e250;