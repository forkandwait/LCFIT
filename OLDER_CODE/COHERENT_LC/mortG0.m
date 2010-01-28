function [mxh,mxf0]=mortG0(mx,yrs,agm,nffy,nfor,ntrj)  % -*-matlab-*-
%This code does general LC forecast on a single mx, including:
% unequal historical interval
% variance of b(x)
% variance of sigma
%  
%mx--matrix of (# years,age) at years of 'yrs',
%yrs--vector of years at which the historic data are used for forecasting,
%agm--maximum reliable age:
%   if the starting age of the open age group <85, agm=0;
%   if the starting age of the open age group >=85, agm=19(85)--23(105);
%
%nffy--first year of forecasting,
%nfor--number of time to be forecasted,
%ntrj--number of trajectories,
  
  nstp=5;%forecasting interval

  xx0=size(yrs);
  nfst=nffy-yrs(xx0(2)); % years b/w nffy and the last historic data

  %Returns forecasted age-specific death rates mxf(trajectory,time,age).  E.g., historical mortality
  %in 1974, 1981, 1990 (ie missing data between).  Forecast 50 years starting at 1995 with 5-year
  %time interval and 1000 trajectries.  Inputs: fvsg=0.5,nffy=1995,nfor=10(50/5),ntrj=1000, Returns:
  %Mortality in 1995, 2000, 2005, ... 2045;

  %(1) Data:(nag-1)--80-84 from Gompertz; agm--105 from Coale-Guo      
  xx1=size(mx);
  nht=xx1(1); %Get sizes of historical time
  nag=xx1(2);
  drt=zeros*(1:18);
  if nag<19; %For the starting age of open age group younger than 85, 
	for jj=1:nht;
      drt=mx(jj,:);
	  ka=log(drt(nag-1)/drt(nag-2));
	  for ii=nag:18;
		drt(ii)=mx(jj,nag-1)*exp(ka*(ii-nag+1));% using Gompertz to get until 80-84
	  end
	  [mxt(jj,:)]= CoaleGt(drt);%using CG to get 80-84,...,105-109;
	end
  else
    for jj=1:nht;
      for ii=1:18;
		drt(ii)=mx(jj,ii);
	  end;
      mxe= CoaleGt(drt);%using CG to get 80-84,...,105-109;
      mxt(jj,1:agm)=mx(jj,1:agm);
      mxt(jj,agm+1:24)=mxe(agm+1:24);
	end    
  end
  nag=24;
  %END(1)
    
  %(2)SVD 
  %(1.1)make matrix for SVD
  lnmx = log(mxt);
  ax= mean(lnmx);
  for ix = 1:nht,
	lnmx1(ix,:) = lnmx(ix,:)-ax;
  end
  % SVD, where bx is sum to 1
  [U S V] = svd(lnmx1,0);
  bx = V(:,1)/sum(V(:,1));
  k = S(1,1)*U(:,1)*sum(V(:,1));
  %End (2)

  %(3) get OLS bx (bxo) and its var (vbx) 
  %OLS bx
  for j=1:nag
    bx(j)=(k'*lnmx1(:,j))/(k'*k);
    bx95(2,j)=bx(j);
  end
  %error matrix
  for i=1:nht;
    for j=1:nag
	  e(i,j)=lnmx1(i,j)-bx(j)*k(i);
    end
  end
  %Var of bx, see Fox, 1997' Applied Regression...' pp115
  for j=1:nag
    varbx(j)=cov(e(:,j))/((nht-1)*cov(k));%Var(bx)
    sdbx(j)=sqrt(varbx(j));%SD of bx
    bx95(1,j)=bx(j)+1.96*sdbx(j);%Upper 95%
    bx95(3,j)=bx(j)-1.96*sdbx(j);%lower
  end
  %End (3)


  %(4) To modify kt by fitting Eo, need fiteo.m
  %(4.1)
  for i=1:nht
	kt=k(i);mx1=mxt(i,:);
	[kt1(i)]=fiteo(ax,bx,kt,mx1);    
  end
  %(4.2) Produce historical m(x,t)
  yrsh=min(yrs)+(1:range(yrs)+1)-1;%historical continuous years
  for i=1:range(yrs)+1
    kh(i)=kt1(1)-(kt1(1)-kt1(nht))*(yrsh(1)-yrsh(i))/(yrsh(1)-yrsh(range(yrs)+1));
  end
  for i=1:range(yrs)+1
    mxh(i,:)=exp(ax+bx'*kh(i));
    for j=1:nht
	  if yrsh(i)==yrs(j)
		mxh(i,:)=mxt(j,:);
	  end
    end
  end
  %End (4)

  %(5) Estimating drift and sigma for unequal intervals
  %Make decline rate version
  for i=1:nht-1
    k1(i)=(kt1(i+1)-kt1(i))/(yrs(i+1)-yrs(i));
  end
  drft=0;
  for i=1:nht-1
    drft=drft-k1(i)*(yrs(i+1)-yrs(i))/(yrs(nht)-yrs(1));
  end
  zz1=0;
  zz2=0;
  for i=1:nht-1
    zz1=zz1+((k1(i)+drft)*(yrs(i+1)-yrs(i)))^2;
    zz2=zz2+(yrs(i+1)-yrs(i))^2;
  end
  sigma0=sqrt(zz1/(yrs(nht)-yrs(1)-zz2/(yrs(nht)-yrs(1))));%standard deviation of sigma

  drft/(sigma0/sqrt((yrs(nht)-yrs(1))));%t value of drft

  kteo=kt1/drft;%Scaling
  sigma=sigma0/drft;
  bx=bx*drft;
  bx95=bx95*drft;
  drft=1;

  zzz=0;
  for i=1:nht-1
    zzz=zzz+(yrs(i+1)-yrs(i))^2;
  end
  resig=sqrt(1/(2*(yrs(nht)-yrs(1)-zzz/(yrs(nht)-yrs(1)))));%Analytical formula of re(var(see))

  %End (5)


  %(6)Forcsting
  %(6.1)Get the random numbers 
  %load ran_start; randn('state', start_state);rndk= randn(ntrj,nfor);
  randn('state',0); 
  rndk=randn(ntrj,nfor); %For innovating k(t)

  %End (6.1)
  % (6.2) Generate stochastic trajectories of kteo:
  stok0=zeros(ntrj,nfor+1);
  stok1=zeros(ntrj,nfor+1);
  stok2=zeros(ntrj,nfor+1);
  for tind =1:ntrj,
	for yind0=1:nfor,
      yind=nstp*(yind0-1)+nfst; %make the first yind the starting year of forscasting
      yyy0=((yind+yind^2/(yrs(nht)-yrs(1)))^.5)*sigma*rndk(tind,yind0);%For most possible CI
      yyy1=((yind+yind^2/(yrs(nht)-yrs(1)))^.5)*sigma*(1+1.96*resig)*rndk(tind,yind0);%For 2.5% wide CI
      yyy2=((yind+yind^2/(yrs(nht)-yrs(1)))^.5)*sigma*(1-1.96*resig)*rndk(tind,yind0);%For 2.5% narrow CI

	  %yind^.5*sigma--innovation of k(t)
	  %(yind^2/(nht-1))^.5*sigma=yind*(sigma^2/(nht-1))^.5--SD of drift term
	  stok0(tind,yind0+1)=kteo(nht)-yind*drft+yyy0;
	  stok1(tind,yind0+1)=kteo(nht)-yind*drft+yyy1;
	  stok2(tind,yind0+1)=kteo(nht)-yind*drft+yyy2;
	end
  end
  stok0(:,1)=kteo(nht);stok1(:,1)=kteo(nht);stok2(:,1)=kteo(nht);
  %End(6.2)

  mxf0=zeros(ntrj,nfor,nag);
  mxf1=zeros(ntrj,nfor,nag);
  maf2=zeros(ntrj,nfor,nag);
  % (6.3)mx 
  for tt=1:nfor
	for tind=1:ntrj
	  for j=1:nag
		mxf0(tind,tt,j)=mxt(nht,j)*exp((stok0(tind,tt+1)-kteo(nht))*bx(j));
		mxf1(tind,tt,j)=mxt(nht,j)*exp((stok1(tind,tt+1)-kteo(nht))*bx(j));
		mxf2(tind,tt,j)=mxt(nht,j)*exp((stok2(tind,tt+1)-kteo(nht))*bx(j));
	  end   
	end
  end
  %End (6.3)
  
  %(6.4) make qx<=1; b/c 5-yr group
  for tind=1:ntrj
	for tt=1:nfor
	  if mxf0(tind,tt,1)>0.78;
		mxf0(tind,tt,1)=0.78;
	  end;%keep q<1
	  if mxf0(tind,tt,2)>0.66;
		mxf0(tind,tt,2)=0.66;
	  end;
	  for i=3:3;if mxf0(tind,tt,i)>0.4;
		  mxf0(tind,tt,i)=0.39;
		end;
	  end;
	  if mxf1(tind,tt,1)>0.78;
		mxf1(tind,tt,1)=0.78;
	  end;%keep q<1
	  if mxf1(tind,tt,2)>0.66;
		mxf1(tind,tt,2)=0.66;
	  end;
	  for i=3:3;
		if mxf1(tind,tt,i)>0.4;
		  mxf1(tind,tt,i)=0.39;
		end;
	  end;
	  if mxf2(tind,tt,1)>0.78;
		mxf2(tind,tt,1)=0.78;
	  end;%keep q<1
	  if mxf2(tind,tt,2)>0.66;
		mxf2(tind,tt,2)=0.66;
	  end;
	  for i=3:3;
		if mxf2(tind,tt,i)>0.4;
		  mxf2(tind,tt,i)=0.39;
		end;
	  end;
	end
  end
  
  %End(6.4)
  %End(6)


  %(7)%pictures  
  
  [kt9750,kt500,kt250,e9750,e500,e250]=pict(mxf0,stok0);%kt
  [kt9751,kt501,kt251,e9751,e501,e251]=pict(mxf1,stok1);
  [kt9752,kt502,kt252,e9752,e502,e252]=pict(mxf2,stok2);

  timef=nffy-5+5*(1:nfor);
  clf;plot(yrs,kteo,'^-');hold;plot(timef,kt9750(2:nfor+1));
  plot(timef,kt500(2:nfor+1));plot(timef,kt250(2:nfor+1));
  plot(timef,kt9751(2:nfor+1),'--');plot(timef,kt501(2:nfor+1),'--');plot(timef,kt251(2:nfor+1),'--');
  plot(timef,kt9752(2:nfor+1),'-.');plot(timef,kt502(2:nfor+1),'-.');plot(timef,kt252(2:nfor+1),'-.');

  set(gca, 'Xlim', [yrs(1) timef(nfor)]);
  ylabel('Ajusted (by Eo) k(t)');xlabel('Year')
  title('Historic and forecast Eo (Mean, Most possible 95% CI, 2.5% wide 95% CI, 2.5% narrow 95% CI)')  

  for i=1:nht%Eo
    eoh(i)=lfexpt(mxt(i,:));
  end
  clf;plot(yrs,eoh,'^-');hold;plot(timef,e9750);
  plot(timef,e500);plot(timef,e250);
  plot(timef,e9751,'--');plot(timef,e501,'--');plot(timef,e251,'--');
  plot(timef,e9752,'-.');plot(timef,e502,'-.');plot(timef,e252,'-.');
  set(gca, 'Xlim', [yrs(1) timef(nfor)]);
  ylabel('Life expectancy at birth, Eo');xlabel('Year');
  title('Historic and forecast Eo (Mean, Most possible 95% CI, 2.5% wide 95% CI, 2.5% narrow 95% CI)')  