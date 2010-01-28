%function [mxc,mx,Bx,Kt,bxc,Ktc, epr] = multicountry1hmd(iger);  % -*-matlab-*-
%For 1952--96 (Limited byGermany)

clear;
nc0=15;%number of 15 countries without eastern europe
nht=45;%historical years
mxc=zeros(nc0,nht,24);%country-specific mx, until age 105--110
pxc=zeros(nc0,nht,18);%country-specific px

%Austria
load ./multicountry0/data/austria/m5296.txt;load ./multicountry0/data/austria/p5296.txt
mxc(1,1:nht,1:18)=m5296;pxc(1,1:nht,1:18)=p5296;
%Canada
load ./multicountry0/data/canada/m5296.txt;load ./multicountry0/data/canada/p5296.txt
mxc(2,1:nht,1:18)=m5296;pxc(2,1:nht,1:18)=p5296;
%denmark
load ./multicountry0/data/denmark/m5296.txt;load ./multicountry0/data/canada/p5296.txt
mxc(3,1:nht,1:18)=m5296;pxc(3,1:nht,1:18)=p5296;
%england
load ./multicountry0/data/england/m5296.txt;load ./multicountry0/data/england/p5296.txt
mxc(4,1:nht,1:18)=m5296;pxc(4,1:nht,1:18)=p5296;
%finland
load ./multicountry0/data/finland/m5296.txt;load ./multicountry0/data/finland/p5296.txt
mxc(5,1:nht,1:18)=m5296;pxc(5,1:nht,1:18)=p5296;
%france
load ./multicountry0/data/france/m5296.txt;load ./multicountry0/data/france/p5296.txt
mxc(6,1:nht,1:18)=m5296;pxc(6,1:nht,1:18)=p5296;
%germanyw
load ./multicountry0/data/germanyw/m5296.txt;load ./multicountry0/data/germanyw/p5296.txt
mxc(7,1:nht,1:18)=m5296;pxc(7,1:nht,1:18)=p5296;
%italy
load ./multicountry0/data/italy/m5296.txt;load ./multicountry0/data/italy/p5296.txt
mxc(8,1:nht,1:18)=m5296;pxc(8,1:nht,1:18)=p5296;
%Japan
load ./multicountry0/data/japan/m5296.txt;load ./multicountry0/data/japan/p5296.txt
mxc(9,1:nht,1:18)=m5296;pxc(9,1:nht,1:18)=p5296;
%netherland
load ./multicountry0/data/netherland/m5296.txt;load ./multicountry0/data/netherland/p5296.txt
mxc(10,1:nht,1:18)=m5296;pxc(10,1:nht,1:18)=p5296;
%norway
load ./multicountry0/data/norway/m5296.txt;load ./multicountry0/data/norway/p5296.txt
mxc(11,1:nht,1:18)=m5296;pxc(11,1:nht,1:18)=p5296;
%spain
load ./multicountry0/data/spain/m5296.txt;load ./multicountry0/data/spain/p5296.txt
mxc(12,1:nht,1:18)=m5296;pxc(12,1:nht,1:18)=p5296;
%sweden
load ./multicountry0/data/sweden/m5296.txt;load ./multicountry0/data/sweden/p5296.txt
mxc(13,1:nht,1:18)=m5296;pxc(13,1:nht,1:18)=p5296;
%sweitzerland
load ./multicountry0/data/sweitzerland/m5296.txt;load ./multicountry0/data/sweitzerland/p5296.txt
mxc(14,1:nht,1:18)=m5296;pxc(14,1:nht,1:18)=p5296;
%usa
load ./multicountry0/data/usa/m5296.txt;load ./multicountry0/data/usa/p5296.txt
mxc(nc0,1:nht,1:18)=m5296;pxc(nc0,1:nht,1:18)=p5296;

%Caole-Guo
for ic=1:nc0
  for i=1:nht
	for j=1:18;
	  drt(j)=mxc(ic,i,j);
    end     
    mxcg=CoaleGt(drt);
    mxc(ic,i,19:24)=mxcg(19:24);
  end
end

%Making mx for total group    
for i=1:nht %Get sex-combined death rates
  for j=1:18
	p=0;d=0;
	for ic=1:nc0%For nc0
	  p=p+pxc(ic,i,j);
	  d=d+pxc(ic,i,j)*mxc(ic,i,j);
	end
	drt(j)=d/p;%mx for nc0
  end
  mxcg=CoaleGt(drt);%Caole-Guo
  mx(i,1:24)=mxcg;
end

%SVD for nc0 combined
lnmx = log(mx);Ax= mean(lnmx);
for ix = 1:nht,
  lnmx1(ix,:) = lnmx(ix,:)-Ax;
end

% SVD, where bx is sum to 1
[U S V] = svd(lnmx1,0);
Bx = bx_normalize(V(:,1)); %Bx = V(:,1)/sum(V(:,1));
K = S(1,1)*U(:,1)*sum(V(:,1));
epr(1) = S(1,1)^2/trace(S'*S);

% Fit eo
for i=1:nht
  kt=K(i);mx1=mx(i,:);
  [Kt(i)]=fiteo(Ax,Bx,kt,mx1);    
end

save BXKT Bx Kt; 

%SVD for single country



for ic=1:nc0%For nc0
  for i=1:nht
	for j=1:24
	  lnmxc(i,j) = log(mxc(ic,i,j));
	end
  end
  
  for j=1:24
	xx=0;
	for i=1:nht 
	  xx=xx+log(mxc(ic,i,j));
	end
	ax(ic,j)=xx/nht;
  end
  
  for i=1:nht
	for j=1:24
	  lnmxc2(i,j)=log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i);
	  lnmxc1(i,j)=log(mxc(ic,i,j))-ax(ic,j);
	end
  end
  %Separate 
  [U S V] = svd(lnmxc1,0);
  k(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';
  bxo = bx_normalize(V(:,1));  %bxo=(V(:,1)/sum(V(:,1)));
  for i=1:nht
	kt=k(ic,i);
	mx1(1:24)=mxc(ic,i,1:24);
    [kto(i)]=fiteo(ax(ic,:),bxo,kt,mx1);    
  end
  xx1=0;xx2=0;
  
for i=1:nht
	for j=1:24
	  lnmxc(i,j) = log(mxc(ic,i,j));
	  xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;
	  xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-bxo(j)*kto(i))^2;
	end
  end
  epr(ic,1)=1-xx2/xx1;   

  %Group
  [U S V] = svd(lnmxc2,0);
  kc(ic,:)= (S(1,1)*U(:,1)*sum(V(:,1)))';
  bxc = bx_normalize(V(:,1))    %bxc=(V(:,1)/sum(V(:,1)));
  %for i=1:nht%Give up adjusting k(t,i)
  %   kt=kc(ic,i);mx1(1:24)=mxc(ic,i,1:24);
  %   axo=ax(ic,:)'+Bx*Kt(i);
  %   [ktc(i)]=fiteoc(axo',bxc,kt,mx1,i);     
  % end
  xx1=0;xx2=0;xx3=0;
  for i=1:nht
	for j=1:24
	  lnmxc(i,j) = log(mxc(ic,i,j));
	  xx1=xx1+(log(mxc(ic,i,j))-ax(ic,j))^2;
	  xx2=xx2+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i))^2;
	  xx3=xx3+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i)-bxc(j)*kc(ic,i))^2;
	  %   xx3=xx3+(log(mxc(ic,i,j))-ax(ic,j)-Bx(j)*Kt(i)-bxc(j)*ktc(i))^2;
	end
  end
  epr(ic,2)=1-xx2/xx1;
  epr(ic,3)=1-xx3/xx1;%epr(ic,3)=1-xx3/xx1;
  bxC(ic,:)=bxc';
  
  %AR(1) coef.
  for i=1:nht-1
	X(i,2)=kc(ic,i);X(i,1)=1;y(i)=kc(ic,i+1);    
  end
  %OLS  
  b(1)=sum(y);b(2)=y*X(:,2);
  a(1,1)=nht-1;a(1,2)=sum(X(:,2));a(2,1)=a(1,2);a(2,2)=X(:,2)'*X(:,2);
  xxx=(a^-1)*b';
  a0=xxx(1);
  a1=xxx(2);
  a00=mean(y);
  ar(ic)=a1;
  
  Ktc(ic,1)=kc(ic,1);
  for i=2:nht
	Ktc(ic,i)=a0+a1*kc(ic,i-1);
  end
  for i=1:nht
	%e(i)=y(i)-a0-a1*X(i,2);
	e(i)=kc(ic,i)-Ktc(ic,i);   
  end
  sdckt=sqrt(cov(e));
  e0=diff(kc(ic,:));

  RsqRW(ic)=1-e0*e0'/cov(kc(ic,:));%R^2 of RW
  RsqAR(ic)=1-cov(e)/cov(kc(ic,:));%R^2 of AR(1)
  SDCKT(ic) = sdckt  
  A0(ic) = a0
  A1(ic) = a1
  A00(ic)= a00

  ic   
end

%Table2
%epr

%ic=3(UK),8(japan),9(Netherlands),10(Norway), 14(USA)
%clf;plot(kc(ic,:));hold;plot(Ktc(ic,:),'r')

% clear 
% load sweden/BxKt
% %Austria
% load ./multicountry0/data/austria/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %Canada
% load ./multicountry0/data/canada/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %denmark
% load ./multicountry0/data/denmark/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %england
% load ./multicountry0/data/england/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %finland
% load ./multicountry0/data/finland/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %france
% load ./multicountry0/data/france/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %germanyw
% load ./multicountry0/data/germanyw/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %italy
% load ./multicountry0/data/italy/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %Japan
% load ./multicountry0/data/japan/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %netherland
% load ./multicountry0/data/netherland/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %norway
% load ./multicountry0/data/norway/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %Spain
% load ./multicountry0/data/spain/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %sweden
% load ./multicountry0/data/sweden/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %sweitzerland
% load ./multicountry0/data/sweitzerland/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %usa
% load ./multicountry0/data/usa/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %Can be non-group countries be forecasted noon-divergently withg the group?

% %bulgaria
% load ./multicountry0/data/bulgaria/m5296.txt;
% mx=m5296;nht=45;
% [epr,ar,rsq] = multicountry1hmdG(Bx,Kt,mx,nht);

% %Czech
% load ./multicountry0/data/czech/m5296.txt;
% mx=m5296;nht=45;
% [epr,ar,rsq] = multicountry1hmdG(Bx,Kt,mx,nht);

% %germanye
% clear mx
% load ./multicountry0/data/germanye/m5696.txt;
% mx=m5696;nht=40;
% Kto=Kt(5:45);
% [epr,ar,rsq] = multicountry1hmdG(Bx,Kto,mx,nht);

% %hungary
% clear mx
% load ./multicountry0/data/hungary/m5296.txt;
% mx=m5296;nht=45;
% [epr,ar,rsq] = multicountry1hmdG(Bx,Kt,mx,nht);

% %Lithuania
% clear mx
% load ./multicountry0/data/lithuania/m5296.txt;
% mx=m5296;nht=45;
% [epr,ar,rsq] = multicountry1hmdG(Bx,Kt,mx,nht);


% %russia
% clear mx Kto
% load ./multicountry0/data/russia/m7096.txt;
% mx=m7096;nht=27;
% Kto=Kt(19:45);
% [epr,ar,rsq] = multicountry1hmdG(Bx,Kto,mx,nht);

% %bulgaria
% load ./multicountry0/data/bulgaria/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %Czech
% load ./multicountry0/data/czech/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %germanye
% clear mx
% load ./multicountry0/data/germanye/m5696.txt;
% mx=m5696;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %hungary
% clear mx
% load ./multicountry0/data/hungary/m5296.txt;
% mx=m5296;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)

% %Lithuania
% clear mx
% load ./multicountry0/data/lithuania/m6096.txt;
% mx=m6096;
% [RsqRW,RsqAR,a0,a1,sda0,sda1,t,sdckt]=multisfactAR(Bx,Kt,mx)
% a0/(1-a1)
