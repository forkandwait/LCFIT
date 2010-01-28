function [RsqRW,RsqAR,a0,a1,sda0,sda1,z,sdckt]=multisfactAR(Bx,Kt,mx) % -*-matlab-*-
%This code does non-divergent LC forecast, for a single population
%(I think)

xxx=size(mx);nht=xxx(1);
%Caole-Guo
for i=1:nht
  for j=1:18;
	drt(j)=mx(i,j);
  end     
  mxt(i,:)=CoaleGt(drt);
  eoh(i)=lfexpt(mxt(i,:));
end

%mxt--matrix of ASDR,
%nffy--first year of forecasting,
%nfor--number of time to be forecasted,
%nfor--number of time to be forecasted in 5-yr interval,
%nspt--different bewteen first year of forscast in 5-yr and the last hist data 
%ntrj--number of trajectories,

xxx=size(mxt);nag=xxx(2);

%(2)SVD 
%(1.1)make matrix for SVD
lnmx = log(mxt);ax= mean(lnmx);
for ix = 1:nht,
  for j=1:nag
	lnmx1(ix,j) = lnmx(ix,j)-ax(j)-Bx(j)*Kt(ix);
  end
end

% SVD, where bx is sum to 1
[U S V] = svd(lnmx1,0);bx = V(:,1)/sum(V(:,1));kt= S(1,1)*U(:,1)*sum(V(:,1));
%End (2)

%(4) Estimating drift and sdgkt for the RWD of group
dKt=diff(Kt);
drft=mean(dKt); 
sdgkt=sqrt(cov(dKt));
%End (4)

%(5) Estimating a0,a1 and sdckt for the AR(1)-->k(t)=a0+a1*k(t-1)+sdckt*e(t) of a country.
for i=1:nht-1
  X(i,2)=kt(i);
  X(i,1)=1;
  y(i)=kt(i+1);    
end
%OLS
b(1)=sum(y);b(2)=y*X(:,2);
a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
xxx=(a^-1)*b';
a0=xxx(1);a1=xxx(2);a00=mean(y);
ktm(1)=kt(1);
for i=2:nht
  ktm(i)=a0+a1*kt(i-1);
end
for i=1:nht    
  e(i)=kt(i)-ktm(i);   
end
sdckt=sqrt(cov(e));
e0=diff(kt);
RsqRW=1-e0'*e0/cov(kt);%R^2 of RW
RsqAR=1-cov(e)/cov(kt);%R^2 of AR(1)

%Estimating SDT of a0 and a1
sda0=sdckt/sqrt((nht-1));
sda1=sdckt/sqrt((kt'*kt));              
%End (5)
%prob of a1>1
z=(1-a1)/sda1;%t-score

%Prob{[c1-c1(observed))/sdc1>(1-c1(obsvered)/sdc1}=Prob{z>z(observed)}=Prob{c1>1}