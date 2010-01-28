function [eof,drft,sdgkt,a0,a1,sdckt,Rsq]=multicountry2(ic,Bx,Kt,mxc,rndgk,nfor,ntrj)  %-*-matlab-*-

%This code does correlated LC forecast, including:

for i=1:39
    for j=1:24
        mxt(i,j)=mxc(ic,i,j);
    end
end
          
%mxt--matrix of ASDR,
%nffy--first year of forecasting,
%nfor--number of time to be forecasted,
%ntrj--number of trajectories,

xx1=size(mxt);
nht=xx1(1); %Get sizes of historical time
nag=xx1(2);
                    
%(2)SVD 
 %(1.1)make matrix for SVD
lnmx = log(mxt);ax= mean(lnmx);
for ix = 1:nht,
    for j=1:nag
   lnmx1(ix,j) = lnmx(ix,j)-ax(j)-Bx(j)*Kt(ix);
   end
end
% SVD, where bx is sum to 1
[U S V] = svd(lnmx1,0);bx = V(:,1)/sum(V(:,1));k= S(1,1)*U(:,1)*sum(V(:,1));
epr=S(1,1)^2/trace(S'*S);
%End (2)

%(3) To modify kt by fitting Eo, need fiteo.m

for i=1:nht
    ktoo=Kt(i);kt=k(i);
    for j=1:24
        mx1(j)=mxt(i,j);
    end
    axo=ax;
   [kt1(i)]=fiteoc(axo,Bx,bx,ktoo,kt,mx1);    
end
      
%(4) Estimating drift and sdgkt for the RWD of group
dKt=diff(Kt);drft=mean(dKt); sdgkt=sqrt(cov(dKt));
%End (4)

%(5) Estimating a0,a1 and sdckt for the AR(1)-->k(t)=a0+a1*k(t-1)+sdckt*e(t) of a country.
for i=1:nht-1
    X(i,2)=kt1(i);X(i,1)=1;y(i)=kt1(i+1);    
end
%OLS
b(1)=sum(y);b(2)=y*X(:,2);
a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
xxx=(a^-1)*b';
a0=xxx(1);a1=xxx(2);a00=mean(y);
for i=1:nht-1
    e(i)=y(i)-a0-a1*X(i,2);
    e0(i)=y(i)-a00;
end
sdckt=sqrt(var(e));
Rsq=1-var(e)/var(e0)
%R^2


%End (5)


%(6)Forcsting
  %(6.1)Get the random numbers 
randn('state',1); rndck=randn(ntrj,nfor); %For innovating country's (local) k(t)
%End (6.1)
  % (6.2) Generate stochastic trajectories of Kt and ktc:
stokg=zeros(ntrj,nfor+1);stokg(:,1)=Kt(nht);%Group Kt, RWD
stokc=zeros(ntrj,nfor+1);stokc(:,1)=kt1(nht);%Local ktc, AR(1) or RW
for tind =1:ntrj,
   for yind0=1:nfor,%Single yr forecast for handle AR(1) simplier
      stokg(tind,yind0+1)=stokg(tind,1)+yind0*drft+(yind0+yind0^2/nht)^.5*sdgkt*rndgk(tind,yind0);%RWD
      stokc(tind,yind0+1)=a0+a1*stokc(tind,yind0)+sdckt*rndck(tind,yind0);%AR(1)      
   end
end
%End(6.2)

% (6.3)mx 
mxf=zeros(ntrj,nfor,nag);
for tt=1:nfor
 for tind=1:ntrj
  for j=1:nag
   mxf(tind,tt,j)=mxt(nht,j)*exp((stokg(tind,tt+1)-stokg(tind,1))*Bx(j)+(stokc(tind,tt+1)-stokc(tind,1))*bx(j));    
  end   
 end
end
%End (6.3)

%(6.4) make qx<=1; b/c 5-yr group
  for tind=1:ntrj
      for tt=1:nfor
           if mxf(tind,tt,1)>0.78;mxf(tind,tt,1)=0.78;end;%keep q<1
           if mxf(tind,tt,2)>0.66;mxf(tind,tt,2)=0.66;end;
           for i=3:3;if mxf(tind,tt,i)>0.4;mxf(tind,tt,i)=0.39;end;end;
      end
  end
  
%End(6.4)
%End(6)

%(7) Forecasted Eo  
[kt9750,kt500,kt250,e9750,e500,e250]=pict(mxf,stokc);%kt
eof(1,:)=e9750;eof(2,:)=e500;eof(3,:)=e250;
