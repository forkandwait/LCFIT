function [eofs]=multicountry2S(mx,nhly,nffy5,nfor5,ntrj)  % -*-matlab-*-
%  MULTICOUNTRY2S: *non-convergent* LC projection
%
% Inputs 
%    mx    -- ASDR
%    nhly  -- starting year (like 1996)
%    nffy5 -- ???  First 5 year starting point (like 2000)
%    nfor5 -- number of time to be forecasted 
%    ntrj  -- number of trajectories.
% 
% Output eofs -- matrix of e_0 for forecasted death rates, 5% + 50% + 95% in rows, projected years
%    in columns.

%    XXX  nfst  -- first time of forecast from the hostorical data,  
%    XXX  nstp  -- length of time interval in forecasting,


% XXX Don't know what the following means: 
%Historical mortality in XXXX--1993 each year, forecasting 50 years 
%starting at 1995 with 5-year time interval and 1000 trajectries.
%Inputs: nfor5=10(50/5),nfst=2(1995-1993),nstp=5,ntrj=1000,
%Returns: Mortality in 1995, 2000, 2005, ... 2045;

nfst=nffy5-nhly;
nstp=5;

%(1) Data
xxx=size(mx);
nht=xxx(1); %Get sizes of historical time
for it=1:nht %Using Coale-Guo to get 85-89,...100-104.
  drt=mx(it,:);
  [nmx]= CoaleGt(drt);
  mxt(it,:)=nmx; % extended by CG   
end
nag=24;

%(2)Lee-carter model 
%(1.1)make matrix for SVD
lnmx = log(mxt);
ax= mean(lnmx);
for ix = 1:nht;
  lnmx1(ix,:) = lnmx(ix,:)-ax;
end

% SVD, where bx is sum to 1
[U S V] = svd(lnmx1,0);
bx = V(:,1)/sum(V(:,1));
k = S(1,1)*U(:,1)*sum(V(:,1));

%End of (1.1)
%(1.2)To modify kt by fitting Eo, need fiteo.m
if min(bx)>0;
  for i=1:nht
	kt=k(i);mx1=mxt(i,:);
	[kt1]=fiteo(ax,bx,kt,mx1);
	kteo(i)=kt1;    
  end %End of (1.2)
else
  bx'  
  kteo=k;
end
%End of (1)

%(2)Forcsting
%(2.0)Get the random numbers rdn(ntrj,nfor5)
randn('state',1); 
rdn=randn(ntrj,nfor5);

% Fit the random walk model
dkteo=diff(kteo); 
drft=mean(dkteo); 
sdktnd=sqrt(cov(dkteo));

% (2.1)Now generate stochastic trajectories of ktnd:
stok=zeros(ntrj,nfor5+1); 
for tind =1:ntrj,
  for yind0=1:nfor5,
	yind=nstp*(yind0-1)+nfst;
	stok(tind,yind0+1)=kteo(nht)+yind*drft+(yind+yind^2/nht)^.5*sdktnd*rdn(tind,yind0);
	%here the error of estimating drft term is included by (yrs/nht)      
  end
end
stok(:,1)=kteo(nht);

%End of (2.1)
% (2.2)mx 
% Uses nht -- number of data years -- to get jump off mx.
for tt=1:nfor5
  for tind=1:ntrj
	for j=1:nag
	  drtf(j)=mxt(nht,j)*exp((stok(tind,tt+1)-kteo(nht))*bx(j)');
	end
	mxf(tind,tt,:)=drtf;
	
  end
end%End of (2.2)

[e9750,e500,e250]=pictG(mxf);%kt
eofs(1,:)=e9750;eofs(2,:)=e500;eofs(3,:)=e250;

aa(1)=0;aa(2)=1;aa(3:24)=5*(1:22);tt=1959+(1:37);
%For Fig 8
clf;
%subplot(2,2,1);  plot(aa,bx,'k');ylabel('The b(x) of OLC');xlabel('Age'); % XXX error
%subplot(2,2,2);  plot(tt,kteo,'k'); ylabel('The k(t) of OLC');xlabel('Year'); % XXX error

%mxo(1:ntrj,1:24)=mxf(:,nfor5,:);xo=mean(mxo);
%Male ASDR(0) at 2100,8.3953e-005
%Female ASDR(0) at 2100,1.1378e-004
%Ratio M/F = 0.7379

%Male xo(10)=ASDR(40-44) at 2100,5.1504e-004
%Female ASDR(40-44) at 2100,1.8712e-004
%Ratio M/F =2.75
end
